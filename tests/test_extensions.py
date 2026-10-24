import json
import zipfile
from pathlib import Path

import httpx
import pytest

from backend.app.config import Settings
from backend.app.extensions import CloudGate, PineconeKnowledge, Mem0Memory, KeenableSearch, ElevenLabsVoice, LangfuseTrace
from backend.app.providers import ProviderError, ProviderFactory
from backend.app.store import Store
from scripts.backup import backup, restore


@pytest.fixture
def cloud(tmp_path,monkeypatch):
    for name in ('pinecone','mem0','langfuse','keenable','elevenlabs'):
        monkeypatch.setenv(name.upper()+'_MAX_REQUEST_USD','0.01')
    s=Settings(data_dir=tmp_path,profile='sponsored',allow_cloud=True,allow_paid=True,data_consent=True,max_cost=1)
    return s,Store(tmp_path)


def test_gate_blocks_unapproved_services(tmp_path):
    s=Settings(data_dir=tmp_path)
    with pytest.raises(ProviderError,match='consent'):CloudGate(s,Store(tmp_path)).reserve('pinecone','key')


def test_pinecone_scoped_search_and_canonical_filter(cloud,monkeypatch):
    s,store=cloud
    monkeypatch.setenv('PINECONE_API_KEY','fixture');monkeypatch.setenv('PINECONE_HOST','https://fixture.svc.pinecone.io');monkeypatch.setenv('PINECONE_DIMENSION','2')
    store.put('document','tenant-a','rb',{'id':'rb','title':'Test','text':'Canonical operational evidence'})
    requests=[]
    def respond(r):
        body=json.loads(r.content);requests.append((r.url.path,body))
        if r.url.path.endswith('upsert'):return httpx.Response(200,json={'upsertedCount':1})
        return httpx.Response(200,json={'matches':[{'id':'rb:0','score':.9,'metadata':{'document_id':'rb','text':'Canonical operational evidence','title':'Test'}}, {'id':'evil','score':1,'metadata':{'document_id':'other-tenant','text':'invented'}}]})
    class Embed:
        def embed(self,texts):return [[1.,0.] for _ in texts]
    provider=PineconeKnowledge(s,store,Embed(),httpx.MockTransport(respond))
    assert provider.rebuild('tenant-a')==1
    assert len(provider.search('tenant-a','evidence'))==1
    assert requests[0][1]['namespace']==requests[1][1]['namespace']
    assert provider.namespace('tenant-b')!=provider.namespace('tenant-a')


def test_mem0_explicit_sync_and_tenant_filter(cloud,monkeypatch):
    s,store=cloud;monkeypatch.setenv('MEM0_API_KEY','fixture')
    calls=[]
    def respond(r):
        body=json.loads(r.content);calls.append(body)
        if r.url.path.endswith('search/'):return httpx.Response(200,json={'results':[{'metadata':{'canonical_id':'m1'}}]})
        return httpx.Response(200,json={'results':[]})
    p=Mem0Memory(s,store,httpx.MockTransport(respond))
    p.save('tenant-a','m1',{'id':'m1','text':'Reviewed hypothesis'})
    assert calls==[] and p.sync('tenant-a')==1
    assert p.retrieve('tenant-a','query')[0]['id']=='m1'
    assert calls[-1]['filters']=={'user_id':'tenant-a'}
    assert p.retrieve('tenant-b','query')==[]


def test_search_and_speech_contracts(cloud,monkeypatch):
    s,store=cloud
    monkeypatch.setenv('KEENABLE_API_KEY','fixture');monkeypatch.setenv('ELEVENLABS_API_KEY','fixture');monkeypatch.setenv('ELEVENLABS_VOICE_ID','fixtureVoice')
    def search(r):
        assert r.headers['X-API-Key']=='fixture'
        assert json.loads(r.content)['max_results']==3
        return httpx.Response(200,json={'results':[{'title':'Doc','url':'https://example.test','snippet':'Reference'}]})
    assert len(KeenableSearch(s,store,httpx.MockTransport(search)).search('query'))==1
    def speech(r):
        assert r.url.path=='/v1/text-to-speech/fixtureVoice'
        assert 'user@example.com' not in json.loads(r.content)['text']
        return httpx.Response(200,content=b'fixture audio')
    assert ElevenLabsVoice(s,store,httpx.MockTransport(speech)).synthesize('user@example.com')==b'fixture audio'


def test_langfuse_explicit_export(cloud,monkeypatch):
    s,store=cloud
    monkeypatch.setenv('LANGFUSE_PUBLIC_KEY','pk-fixture');monkeypatch.setenv('LANGFUSE_SECRET_KEY','sk-fixture')
    requests=[]
    def respond(r):requests.append(r);return httpx.Response(200,json={})
    p=LangfuseTrace(s,store,httpx.MockTransport(respond));p.trace('local','run','triage','Parsed')
    assert requests==[]
    assert p.export('local','run')==1
    assert requests[0].url.path=='/api/public/otel/v1/traces'
    assert requests[0].headers['x-langfuse-ingestion-version']=='4'


def test_backup_restore_and_zip_traversal(tmp_path):
    source=tmp_path/'source';store=Store(source);store.put('document','local','1',{'text':'Canonical'})
    archive=tmp_path/'backup.zip';backup(source,archive)
    dest=tmp_path/'restored';restore(archive,dest)
    assert Store(dest).get('document','local','1')['text']=='Canonical'
    with pytest.raises(ValueError,match='empty'):restore(archive,dest)
    bad=tmp_path/'bad.zip'
    with zipfile.ZipFile(bad,'w') as z:z.writestr('../escape.txt','bad')
    with pytest.raises(ValueError,match='Unexpected'):restore(bad,tmp_path/'another')


def test_profile_factory_switches_without_network(tmp_path,monkeypatch):
    # No actual provider call is made by factory construction.
    for profile in ('local_free','hybrid','sponsored'):
        s=Settings(data_dir=tmp_path/profile,profile=profile)
        p=ProviderFactory(s,Store(s.data_dir))
        assert isinstance(p.knowledge,PineconeKnowledge)==(profile=='sponsored')
        assert isinstance(p.memory,Mem0Memory)==(profile=='sponsored')


def test_canonical_mutation_blocks_approval(tmp_path):
    from tests.test_workflow import build,state
    _,store,_,flow=build(tmp_path)
    store.put('document','local','doc',{'id':'doc','text':'Changed source no longer supports the retrieved quote'})
    result=flow.run(state())
    assert result['status']=='needs_human'
    assert not result['validation']['canonical_sources_valid']
