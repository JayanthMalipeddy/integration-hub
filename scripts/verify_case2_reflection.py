"""Live repair replay: seed the historical Case 2 omission, then use real local inference.

This is a targeted repair-stage verification, not a fresh end-to-end benchmark.
No ticket is approved and no existing evaluation score is modified.
"""
import hashlib
import json
import time
import uuid
from dataclasses import replace
from pathlib import Path

from backend.app.config import Settings
from backend.app.providers import ProviderFactory
from backend.app.store import Store, now
from backend.app.workflow import InvestigationWorkflow, parse_logs, validate_finding
from scripts.seed import seed


def verify():
    root=Path(__file__).resolve().parents[1]
    live=Settings.from_env()
    if live.profile!='local_free' or live.effective_vector_store!='chroma':
        raise ValueError('Replay requires local_free with Chroma; paid calls are not enabled by this script')
    historical_path=root/'evaluations/results/eval-250629587ee5.json'
    historical=json.loads(historical_path.read_text())
    finding=next(r['finding'] for r in historical['results'] if r['case']=='partner-quota')
    case=next(c for c in json.loads((root/'data/incidents.json').read_text()) if c['id']=='partner-quota')
    replay_id='case2-reflection-'+uuid.uuid4().hex[:12]
    settings=replace(live,data_dir=live.data_dir/'verifications'/replay_id)
    store=Store(settings.data_dir)
    seed(store)
    for doc in store.list('document','local'):store.put('document',replay_id,doc['id'],doc)
    providers=ProviderFactory(settings,store)
    workflow=InvestigationWorkflow(settings,store,providers)
    evidence=providers.knowledge.search(replay_id,case['logs'])
    initial_validation=validate_finding(finding,evidence,case['logs'])
    assert not initial_validation['passed'] and not initial_validation['log_and_document_cited']
    initial={'id':replay_id,'tenant':replay_id,'incident':{k:case[k] for k in ('title','service','logs')},
             'status':'running','signals':parse_logs(case['logs']),'finding':finding,'evidence':evidence,
             'decision':{'tool':'search_runbooks','query':case['logs'],'reason':'Historical Case 2 replay'},
             'analysis_attempts':1,'schema_error':'','calls':[],'created_at':now(),'profile':'local_free'}
    # Resume the actual graph immediately after the historical bad analyst response.
    workflow.graph.update_state(workflow.config(replay_id,replay_id),initial,as_node='analyze')
    print(json.dumps({'replay_id':replay_id,'initial_validation':initial_validation,'next_node':'verify'}),flush=True)
    started=time.perf_counter()
    result=workflow.run(tenant=replay_id,id=replay_id)
    traces=list(reversed([t for t in store.list('trace',replay_id) if t['run_id']==replay_id]))
    checks=[t['validation']['passed'] for t in traces if t['node']=='verify']
    no_writes=not store.list('ticket',replay_id) and not store.list('memory',replay_id)
    passed=(result['status']=='awaiting_approval' and result.get('validation',{}).get('passed')
            and checks[0] is False and checks[-1] is True and no_writes)
    report={'id':replay_id,'timestamp':now(),'test_kind':'live repair replay of historical missing citation; not an end-to-end benchmark',
            'historical_input':historical_path.name,'workflow_sha256':hashlib.sha256((root/'backend/app/workflow.py').read_bytes()).hexdigest(),
            'passed':bool(passed),'status':result['status'],'validation_sequence':checks,
            'seeded_analysis_attempts':1,'new_model_calls':len(result.get('calls',[])),
            'analysis_attempts':result.get('analysis_attempts'),'latency_ms':round((time.perf_counter()-started)*1000,2),
            'initial_finding':finding,'final_finding':result.get('finding'),'validation':result.get('validation'),
            'calls':result.get('calls',[]),'traces':traces,'no_ticket_or_memory_write':no_writes,'error':result.get('error')}
    target=root/'evaluations/results'/f'{replay_id}.json'
    target.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'artifact':str(target),'passed':bool(passed),'status':result['status'],'validation_sequence':checks,'new_model_calls':report['new_model_calls']}),flush=True)
    if not passed:raise SystemExit('Live repair did not pass; inspect the saved artifact')


if __name__=='__main__':verify()
