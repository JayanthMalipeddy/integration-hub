"""Real model + durable approval smoke check. Explicitly synthetic local ticket."""
import json
import uuid
from pathlib import Path
from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.workflow import InvestigationWorkflow
from backend.app.store import now
from scripts.seed import seed

if __name__=='__main__':
    settings=Settings.from_env()
    if settings.profile!='local_free':raise SystemExit('This verification only permits local_free')
    app=create_app(settings);store=app.state.store;seed(store)
    flow=app.state.workflow
    source_checks=[]
    for old in store.list('run','local'):
        if old.get('finding'):
            check=flow.verify(old)['validation']
            source_checks.append({'run_id':old['id'],'canonical_sources_valid':check['canonical_sources_valid'],'passed':check['passed']})
    initial={'id':uuid.uuid4().hex,'tenant':'local','incident':{'title':'Final verification: expired API token','service':'synthetic-verification',
        'logs':'2026-10-24T12:00:00Z gateway status=401 error=invalid_token message=token expired correlation_id=final-check'},
        'status':'running','calls':[],'created_at':now(),'profile':'local_free'}
    result=flow.run(initial)
    print(json.dumps({'run_id':initial['id'],'status':result['status']}),flush=True)
    assert result['status']=='awaiting_approval', result.get('error')
    assert not store.get('ticket','local','REC-'+initial['id'][:8])
    restarted=InvestigationWorkflow(settings,store,app.state.providers)
    done=restarted.run(tenant='local',id=initial['id'],approval={'approved':True,'note':'Synthetic developer smoke check; local ticket only'})
    assert done['status']=='completed'
    assert store.get('ticket','local',done['ticket_id'])
    assert store.get('memory','local',initial['id'])
    report={'timestamp':now(),'run_id':initial['id'],'status':done['status'],'ticket_id':done['ticket_id'],
            'real_model':done['calls'],'durable_resume':True,'no_write_before_approval':True,'canonical_revalidation':source_checks}
    Path('evaluations/results/live-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)
