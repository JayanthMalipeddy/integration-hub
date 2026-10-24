"""Use the existing local server; only rebuild Integration Hub's own collection."""
import hashlib
import json
from pathlib import Path
from backend.app.config import Settings
from backend.app.providers import ProviderFactory
from backend.app.store import Store, now

s=Settings.from_env()
assert s.chroma_mode=='http' and s.effective_vector_store=='chroma' and s.profile=='local_free'
p=ProviderFactory(s,Store(s.data_dir))
client=p.knowledge.client
own=p.knowledge.collection_name('local')

def foreign_snapshot():
    snapshot={}
    for collection in client.list_collections():
        if collection.name!=own:
            rows=client.get_collection(collection.name).get(include=['documents','metadatas'])
            canonical=sorted(zip(rows['ids'],rows['documents'],rows['metadatas']),key=lambda x:x[0])
            snapshot[collection.name]={'count':len(canonical),'digest':hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest()}
    return snapshot

before=foreign_snapshot()
count=p.knowledge.rebuild('local')
results=p.knowledge.search('local','HTTP 401 invalid_token token expired')
assert results and results[0]['document_id']=='rb-auth'
after=foreign_snapshot()
assert before==after,'Another project collection changed during verification; inspect concurrent writers'
report={'timestamp':now(),'chroma':p.knowledge.health(),'indexed_chunks':count,
        'query':'HTTP 401 invalid_token token expired','top_document':results[0]['document_id'],
        'existing_collections_unchanged':True,'other_collection_counts':{k:v['count'] for k,v in after.items()},
        'profile':s.profile,'paid_enabled':s.allow_paid,
        'note':'Real local HTTP retrieval check, not a rerun of the model benchmark.'}
Path('evaluations/results/chroma-http-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
