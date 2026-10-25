"""Optional adapters. No SDK installs or external calls at import/initialization.

Contract-tested; live verification requires credentials and explicit cloud consent.
Canonical SQLite copies remain authoritative even with cloud services selected.
"""
import base64
import hashlib
import json
import os
import time
import uuid
from typing import Protocol
from urllib.parse import urlparse

from .providers import HTTPProvider, ProviderError, LocalMemory, ChromaKnowledge
from .security import redact, redact_data


class SearchProvider(Protocol):
    def search(self, query: str) -> list[dict]: ...


class VoiceProvider(Protocol):
    def synthesize(self, text: str) -> bytes: ...


class DisabledFeature:
    def __init__(self, reason): self.reason=reason
    def search(self, query): raise ProviderError(self.reason)
    def synthesize(self, text): raise ProviderError(self.reason)


class CloudGate:
    """Reserve a user-configured operation ceiling, including retries.

    This is an application estimate, not a guarantee against provider billing.
    Provider-side spending limits are also required before enabling paid services.
    """
    def __init__(self, settings, store): self.s,self.store=settings,store
    def reserve(self, service, key):
        if not self.s.allow_cloud or not self.s.allow_paid or not self.s.data_consent or not key:
            raise ProviderError(service + ': credentials and explicit cloud/paid/data consent required')
        ceiling=float(os.getenv(service.upper()+'_MAX_REQUEST_USD','0'))
        if ceiling<=0 or self.s.max_cost<=0:
            raise ProviderError(service + ': configure a positive request cost ceiling and total budget')
        with self.store.lock:
            ledger=self.store.get('budget','system','cloud') or {'reserved_usd':0}
            if ledger['reserved_usd']+2*ceiling>self.s.max_cost:
                raise ProviderError('Configured spending cap reached')
            ledger['reserved_usd']+=2*ceiling
            self.store.put('budget','system','cloud',ledger)


from .retrieval import INDEX_VERSION, chunk_text, embedding_inputs


class PineconeKnowledge(HTTPProvider):
    def __init__(self, settings, store, embeddings, transport=None):
        super().__init__(30,transport)
        self.s,self.store,self.embeddings=settings,store,embeddings
        self.gate=CloudGate(settings,store)
        self.key=os.getenv('PINECONE_API_KEY','')
        self.host=os.getenv('PINECONE_HOST','').rstrip('/')
        if self.host and (urlparse(self.host).scheme!='https' or not (urlparse(self.host).hostname or '').endswith('.pinecone.io')):
            raise ValueError('PINECONE_HOST must be an HTTPS Pinecone index host')

    def namespace(self,tenant):
        docs=self.store.list('document',tenant)
        digest=ChromaKnowledge.digest(docs)
        return hashlib.sha256((tenant+self.s.embed_model+digest+INDEX_VERSION).encode()).hexdigest()[:32]

    def send(self,path,body):
        if not self.host: raise ProviderError('Pinecone host is not configured')
        self.gate.reserve('pinecone',self.key)
        return self.request('POST',self.host+path,headers={'Api-Key':self.key,'X-Pinecone-Api-Version':'2025-10'},json=redact_data(body))

    def rebuild(self,tenant):
        docs=self.store.list('document',tenant)
        chunks=[{'id':d['id']+f':{i}','document_id':d['id'],'title':d['title'],'text':text}
                for d in docs for i,text in enumerate(chunk_text(d['text']))]
        if not chunks:return 0
        vectors=self.embeddings.embed(embedding_inputs(self.s.embed_model,[c['text'] for c in chunks],'document'))
        expected=int(os.getenv('PINECONE_DIMENSION','0'))
        if not expected or len(vectors[0])!=expected:raise ProviderError('Pinecone dimension must match the configured embedding model; rebuild into a compatible index')
        self.send('/vectors/upsert',{'namespace':self.namespace(tenant),'vectors':[{'id':c['id'],'values':v,'metadata':c} for c,v in zip(chunks,vectors)]})
        self.store.put('cloud_index',tenant,'pinecone',{'namespace':self.namespace(tenant),'dimensions':expected})
        return len(chunks)

    def search(self,tenant,query,top_k=3):
        index=self.store.get('cloud_index',tenant,'pinecone')
        if not index or index['namespace']!=self.namespace(tenant):
            raise ProviderError('Pinecone index needs an explicit rebuild; canonical documents are retained locally')
        vector=self.embeddings.embed(embedding_inputs(self.s.embed_model,[query],'query'))[0]
        if len(vector)!=index['dimensions']:raise ProviderError('Embedding dimension mismatch; rebuild required')
        result=self.send('/query',{'namespace':index['namespace'],'vector':vector,'topK':top_k,'includeMetadata':True})
        canonical={d['id']:d for d in self.store.list('document',tenant)}
        evidence=[]
        for m in result.get('matches',[]):
            meta=m.get('metadata',{});doc=canonical.get(meta.get('document_id'))
            # Never trust cloud metadata as a canonical citation.
            if not doc or meta.get('text','') not in doc['text']:continue
            evidence.append({**meta,'id':m['id'],'score':m['score'],'kind':'runbook'})
        return evidence


class Mem0Memory(LocalMemory,HTTPProvider):
    def __init__(self,settings,store,transport=None):
        LocalMemory.__init__(self,store);HTTPProvider.__init__(self,30,transport)
        self.gate=CloudGate(settings,store);self.key=os.getenv('MEM0_API_KEY','')
    def retrieve(self,tenant,query):
        self.gate.reserve('mem0',self.key)
        response=self.request('POST','https://api.mem0.ai/v3/memories/search/',headers={'Authorization':'Token '+self.key},
                              json={'query':query,'filters':{'user_id':tenant},'top_k':3})
        # Only return canonical records owned by this tenant, not generated cloud facts.
        records=[]
        for r in response.get('results',[]):
            key=r.get('metadata',{}).get('canonical_id')
            doc=self.store.get('memory',tenant,key) if key else None
            if doc:records.append(doc)
        return records
    def save(self,tenant,key,value):
        LocalMemory.save(self,tenant,key,value)
        # Queue cloud synchronization; external writes are explicitly initiated by an operator.
        self.store.put('memory_outbox',tenant,key,{'id':key,'value':value})
    def sync(self,tenant):
        count=0
        for item in self.store.list('memory_outbox',tenant):
            self.gate.reserve('mem0',self.key)
            self.request('POST','https://api.mem0.ai/v3/memories/add/',headers={'Authorization':'Token '+self.key},
                         json={'messages':[{'role':'user','content':item['value']['text']}],'user_id':tenant,'metadata':{'canonical_id':item['id']}})
            self.store.delete('memory_outbox',tenant,item['id']);count+=1
        return count


class LangfuseTrace:
    """Local-first outbox; explicit OTLP JSON export avoids silent data egress."""
    def __init__(self,settings,store,transport=None):
        self.store=store;self.gate=CloudGate(settings,store);self.http=HTTPProvider(30,transport)
    def trace(self,tenant,run,node,detail,**kwargs):return self.store.trace(tenant,run,node,detail,**kwargs)
    def export(self,tenant,run):
        public,secret=os.getenv('LANGFUSE_PUBLIC_KEY',''),os.getenv('LANGFUSE_SECRET_KEY','')
        self.gate.reserve('langfuse',public and secret)
        host=os.getenv('LANGFUSE_URL','https://cloud.langfuse.com').rstrip('/')
        if host not in {'https://cloud.langfuse.com','https://us.cloud.langfuse.com'}:raise ProviderError('Use a supported Langfuse cloud region')
        spans=[]
        for e in self.store.list('trace',tenant):
            if e['run_id']!=run:continue
            stamp=str(time.time_ns())
            spans.append({'traceId':hashlib.sha256(run.encode()).hexdigest()[:32],'spanId':e['id'][:16],
                'name':e['node'],'kind':1,'startTimeUnixNano':stamp,'endTimeUnixNano':stamp,
                'attributes':[{'key':'hub.event','value':{'stringValue':json.dumps(e)}}]})
        auth=base64.b64encode((public+':'+secret).encode()).decode()
        result=self.http.request('POST',host+'/api/public/otel/v1/traces',headers={'Authorization':'Basic '+auth,'x-langfuse-ingestion-version':'4'},
            json={'resourceSpans':[{'resource':{'attributes':[{'key':'service.name','value':{'stringValue':'integration-intelligence-hub'}}]},'scopeSpans':[{'scope':{'name':'hub'},'spans':spans}]}]})
        if result.get('partialSuccess',{}).get('rejectedSpans',0):raise ProviderError('Langfuse rejected some spans')
        return len(spans)


class KeenableSearch(HTTPProvider):
    def __init__(self,settings,store,transport=None):
        super().__init__(30,transport);self.gate=CloudGate(settings,store)
    def search(self,query):
        key=os.getenv('KEENABLE_API_KEY','');self.gate.reserve('keenable',key)
        return self.request('POST','https://api.keenable.ai/v1/search',headers={'X-API-Key':key},
                            json={'query':redact(query)[:300],'max_results':3,'snippet_max_length':1000})['results']


class ElevenLabsVoice(HTTPProvider):
    def __init__(self,settings,store,transport=None):
        super().__init__(45,transport);self.gate=CloudGate(settings,store)
    def synthesize(self,text):
        key=os.getenv('ELEVENLABS_API_KEY','');voice=os.getenv('ELEVENLABS_VOICE_ID','')
        if not voice or not voice.isalnum():raise ProviderError('An explicitly selected ElevenLabs voice id is required')
        if len(text)>2000:raise ProviderError('Speech text is limited to 2000 characters')
        self.gate.reserve('elevenlabs',key)
        # No automatic retries on a billable audio generation.
        try:
            response=self.client.post('https://api.elevenlabs.io/v1/text-to-speech/'+voice,
                headers={'xi-api-key':key},json={'text':redact(text),'model_id':'eleven_multilingual_v2'})
            response.raise_for_status()
            return response.content
        except Exception as exc:raise ProviderError('Speech request failed; no retry was sent') from exc
