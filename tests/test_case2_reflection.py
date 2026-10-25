"""Case 2 regression: fixture responses exercise the real graph, not benchmark scoring."""
import json
from copy import deepcopy
from pathlib import Path

from tests.test_workflow import build, state

ROOT = Path(__file__).resolve().parents[1]


def test_case2_missing_runbook_citation_is_corrected_inside_graph(tmp_path):
    case = next(c for c in json.loads((ROOT/'data/incidents.json').read_text()) if c['id']=='partner-quota')
    doc = next(d for d in json.loads((ROOT/'data/runbooks.json').read_text()) if d['id']=='rb-rate')
    historical = json.loads((ROOT/'evaluations/results/eval-250629587ee5.json').read_text())
    omitted = next(r['finding'] for r in historical['results'] if r['case']=='partner-quota')
    assert all(c['source_id']=='incident:logs' for c in omitted['citations'])
    evidence = {'id':'rb-rate:0','document_id':'rb-rate','title':doc['title'],'text':doc['text']}

    class Case2Knowledge:
        def search(self, *args): return [evidence]

    class Case2LLM:
        analyses = 0
        def generate(self, messages, schema):
            if schema['title']=='Decision':
                content={'tool':'search_runbooks','query':'HTTP 429 rate limit Retry-After','reason':'Read rate-limit guidance'}
            else:
                self.analyses += 1
                data=json.loads(messages[-1]['content'])
                content=deepcopy(omitted)
                if self.analyses == 2:
                    assert data['correction']['invalid_citations'] == omitted['citations']
                    assert any('retrieved evidence source' in error for error in data['correction']['errors'])
                    assert data['evidence'][0]['id']=='rb-rate:0'
                    content['citations'].append({'source_id':'rb-rate:0','quote':'HTTP 429 means that the upstream service is rate limiting requests.'})
            return {'content':content,'provider':'test_fixture','model':'case2_fixture','input_tokens':20,'output_tokens':30,'cost_usd':0}

    llm=Case2LLM()
    _,store,_,workflow=build(tmp_path,llm=llm,knowledge=Case2Knowledge())
    store.put('document','local','rb-rate',doc)
    initial=state(case['logs'])
    initial['incident']={k:case[k] for k in ('title','service','logs')}
    result=workflow.run(initial)
    assert result['status']=='awaiting_approval'
    assert result['analysis_attempts']==2 and llm.analyses==2
    assert result['validation']['passed'] and result['validation']['canonical_sources_valid']
    assert [c['node'] for c in result['calls']]==['plan','analyze','analyze']
    checks=list(reversed([t for t in store.list('trace','local') if t['run_id']==initial['id'] and t['node']=='verify']))
    assert [t['validation']['passed'] for t in checks]==[False,True]
    assert not store.list('ticket','local') and not store.list('memory','local')
