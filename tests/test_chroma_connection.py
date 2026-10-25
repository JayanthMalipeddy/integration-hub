from types import SimpleNamespace
import os

import httpx
import pytest

from backend.app.config import Settings
from backend.app.providers import ChromaKnowledge, ProviderFactory, ProviderError
from backend.app.store import Store


def test_env_file_loads_chroma_and_environment_takes_precedence(tmp_path, monkeypatch):
    monkeypatch.setattr(os, 'environ', os.environ.copy())
    env = tmp_path / '.env'
    env.write_text('AI_PROFILE=local_free\nCHROMA_MODE=http\nCHROMA_HOST=127.0.0.1\nCHROMA_PORT=8081\nVECTOR_STORE=chroma\n')
    for key in ('AI_PROFILE','CHROMA_MODE','CHROMA_HOST','CHROMA_PORT','VECTOR_STORE'):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv('CHROMA_PORT', '8082')
    s = Settings.from_env(env)
    assert s.chroma_mode == 'http' and s.chroma_port == 8082
    assert s.effective_vector_store == 'chroma'
    assert s.public()['chroma_endpoint'] == 'http://127.0.0.1:8082'


@pytest.mark.parametrize('key,value', [('CHROMA_HOST','external.example'), ('CHROMA_PORT','70000'), ('CHROMA_MODE','bad'), ('VECTOR_STORE','bad')])
def test_invalid_chroma_settings_rejected(tmp_path, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    with pytest.raises(ValueError): Settings.from_env(tmp_path/'no-env')


def test_http_client_is_lazy_and_project_scoped(tmp_path, monkeypatch):
    import chromadb
    calls = []
    fake = SimpleNamespace(get_or_create_collection=lambda name, **kw: calls.append(name))
    monkeypatch.setattr(chromadb, 'HttpClient', lambda **kw: (calls.append(kw) or fake))
    monkeypatch.setattr(chromadb, 'PersistentClient', lambda **kw: pytest.fail('Must not create a separate embedded database'))
    settings = Settings(data_dir=tmp_path,chroma_mode='http')
    p = ChromaKnowledge(settings, Store(tmp_path), None)
    assert calls == []
    p.collection('local')
    assert calls[0]['host'] == '127.0.0.1' and calls[0]['port'] == 8082
    assert calls[1].startswith('integration_hub_')
    assert p.collection_name('other') != p.collection_name('local')
    assert calls[1] not in {'cbuae_regulations','cbuae_eval_runs'}


def test_chroma_outage_visible_without_silent_fallback(tmp_path, monkeypatch):
    import chromadb
    def offline(**kw): raise RuntimeError('offline')
    monkeypatch.setattr(chromadb, 'HttpClient', offline)
    monkeypatch.setattr(chromadb, 'PersistentClient', lambda **kw: pytest.fail('No fallback'))
    monkeypatch.setattr('backend.app.providers.httpx.get', lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError('offline')))
    p = ChromaKnowledge(Settings(data_dir=tmp_path,chroma_mode='http'), Store(tmp_path), None)
    assert p.health()['status'] == 'unavailable'
    with pytest.raises(ProviderError,match='Cannot connect'): p.collection('local')


def test_paid_model_profile_can_retain_local_chroma(tmp_path):
    s = Settings(data_dir=tmp_path,profile='sponsored',vector_store='chroma',chroma_mode='http')
    p = ProviderFactory(s,Store(tmp_path))
    assert isinstance(p.knowledge,ChromaKnowledge)
    assert p.knowledge._client is None
    assert s.effective_vector_store == 'chroma'
    with pytest.raises(ProviderError,match='disabled'):
        p.llm.generate([],{'type':'object'})


def test_rebuild_modifies_only_selected_project_collection(tmp_path, monkeypatch):
    import chromadb
    operations=[]
    class Collection:
        def count(self): return 1
        def get(self): return {'ids':['old-app-chunk']}
        def delete(self,**kw):operations.append(('delete',kw))
        def upsert(self,**kw):operations.append(('upsert',kw))
    class Client:
        def get_or_create_collection(self,name,**kw):
            operations.append(('collection',name));return Collection()
    monkeypatch.setattr(chromadb,'HttpClient',lambda **kw:Client())
    store=Store(tmp_path)
    store.put('document','local','rb',{'id':'rb','title':'Auth','text':'HTTP 401 authentication guidance'})
    embed=SimpleNamespace(embed=lambda texts:[[1.0,0.0] for _ in texts])
    p=ChromaKnowledge(Settings(data_dir=tmp_path,chroma_mode='http'),store,embed)
    assert p.rebuild('local')==1
    assert operations[0][1].startswith('integration_hub_')
    assert operations[1]==('delete',{'ids':['old-app-chunk']})
    assert operations[2][1]['ids']==['rb:0']


def test_default_application_connection_is_shared_http(tmp_path, monkeypatch):
    for key in ("CHROMA_MODE", "CHROMA_HOST", "CHROMA_PORT"):
        monkeypatch.delenv(key, raising=False)
    settings = Settings.from_env(tmp_path / "no-env")
    assert settings.chroma_mode == "http"
    assert settings.chroma_host == "127.0.0.1"
    assert settings.chroma_port == 8082
