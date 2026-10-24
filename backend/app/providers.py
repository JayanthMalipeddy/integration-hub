"""Provider boundary. Network activity lives here, never in agent nodes."""
import hashlib
import json
import math
import re
import threading
import time
from typing import Protocol

import httpx
from .retrieval import INDEX_VERSION, chunk_text, embedding_inputs


class ProviderError(RuntimeError):
    def __init__(self, message, transient=False):
        super().__init__(message)
        self.transient = transient


class LLMProvider(Protocol):
    def generate(self, messages: list, schema: dict) -> dict: ...


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorStoreProvider(Protocol):
    def search(self, tenant: str, query: str, top_k: int = 3) -> list[dict]: ...


class MemoryProvider(Protocol):
    def retrieve(self, tenant: str, query: str) -> list[dict]: ...
    def save(self, tenant: str, key: str, value: dict) -> None: ...


class ObservabilityProvider(Protocol):
    def trace(self, tenant: str, run: str, node: str, detail: str, **kwargs) -> dict: ...


class HTTPProvider:
    def __init__(self, timeout=180, transport=None):
        self.client = httpx.Client(timeout=timeout, transport=transport, trust_env=False)
        self.failures = 0
        self.open_until = 0.0

    def request(self, method, url, **kwargs):
        if time.monotonic() < self.open_until:
            raise ProviderError("Provider circuit is open; try again after 30 seconds", True)
        for attempt in range(2):
            try:
                response = self.client.request(method, url, **kwargs)
                if response.status_code in (401, 403):
                    raise ProviderError("Provider rejected credentials; fallback is forbidden")
                if response.status_code == 429 or response.status_code >= 500:
                    raise ProviderError(f"Provider temporarily unavailable (HTTP {response.status_code})", True)
                if response.is_error:
                    raise ProviderError(f"Provider rejected request (HTTP {response.status_code}); check model capabilities/configuration")
                result = response.json()
                self.failures = 0
                return result
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                error = ProviderError(f"Provider connection failed: {type(exc).__name__}", True)
            except ProviderError as exc:
                if not exc.transient:
                    raise
                error = exc
            except (ValueError, KeyError) as exc:
                raise ProviderError("Provider returned an invalid response") from exc
            if attempt == 0:
                time.sleep(0.3 * (2 ** attempt))
        self.failures += 1
        if self.failures >= 3:
            self.open_until = time.monotonic() + 30
        raise error


class OllamaLLM(HTTPProvider):
    def __init__(self, settings, transport=None):
        super().__init__(settings.timeout, transport)
        self.s = settings

    def generate(self, messages, schema):
        result = self.request("POST", self.s.ollama_url + "/api/chat", json={
            "model": self.s.model, "messages": messages, "stream": False, "format": schema,
            "options": {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": self.s.max_output},
            "keep_alive": "10m"})
        try:
            content = json.loads(result["message"]["content"])
        except (KeyError, ValueError) as exc:
            raise ProviderError("Model did not produce valid structured JSON") from exc
        return {"content": content, "provider": "ollama", "model": result.get("model", self.s.model),
                "input_tokens": result.get("prompt_eval_count"), "output_tokens": result.get("eval_count"),
                "cost_usd": 0.0, "cost_basis": "Local inference: no API charge; hardware/electricity excluded",
                "fallback": False}


class OpenAICompatibleLLM(HTTPProvider):
    def __init__(self, settings, store, transport=None):
        super().__init__(settings.timeout, transport)
        self.s, self.store = settings, store
        self.lock = threading.Lock()

    def generate(self, messages, schema):
        s = self.s
        if not s.allow_cloud or not s.data_consent or not s.cloud_key or not s.cloud_model:
            raise ProviderError("Cloud is disabled or missing credentials/model/data consent; no request was sent")
        if s.profile == "sponsored" and (not s.allow_paid or s.max_cost <= 0 or s.input_price <= 0 or s.output_price <= 0):
            raise ProviderError("Sponsored inference requires explicit paid consent, positive budget and configured prices")
        if s.profile == "hybrid" and not s.cloud_model.endswith(":free"):
            raise ProviderError("Hybrid requires an explicitly selected OpenRouter :free model")
        # Reserve a conservative upper bound for BOTH possible attempts before any network call.
        reserve = 2 * (len(json.dumps(messages).encode()) * s.input_price + s.max_output * s.output_price) / 1e6
        if s.profile == "sponsored":
            with self.lock:
                ledger = self.store.get("budget", "system", "cloud") or {"reserved_usd": 0}
                if ledger["reserved_usd"] + reserve > s.max_cost:
                    raise ProviderError("Configured spending cap reached; no request was sent")
                ledger["reserved_usd"] += reserve
                self.store.put("budget", "system", "cloud", ledger)
        base = "https://api.tokenfactory.nebius.com/v1" if s.profile == "sponsored" else "https://openrouter.ai/api/v1"
        body = {"model": s.cloud_model, "messages": messages, "temperature": 0, "max_tokens": s.max_output,
                "response_format": {"type": "json_schema", "json_schema": {"name": "agent_result", "schema": schema}}}
        if s.profile == "hybrid":
            body["provider"] = {"max_price": {"prompt": 0, "completion": 0}}
        result = self.request("POST", base + "/chat/completions", headers={"Authorization": "Bearer " + s.cloud_key}, json=body)
        try:
            content = json.loads(result["choices"][0]["message"]["content"])
        except (KeyError, IndexError, ValueError) as exc:
            raise ProviderError("Cloud model returned invalid structured output") from exc
        usage = result.get("usage", {})
        cost = ((usage.get("prompt_tokens", 0) * s.input_price + usage.get("completion_tokens", 0) * s.output_price) / 1e6) if usage else None
        return {"content": content, "provider": "nebius" if s.profile == "sponsored" else "openrouter",
                "model": result.get("model", s.cloud_model), "input_tokens": usage.get("prompt_tokens"),
                "output_tokens": usage.get("completion_tokens"), "cost_usd": cost,
                "cost_basis": "Estimate from configured rates; reserved budget is conservative", "fallback": False}


class FallbackLLM:
    def __init__(self, primary, local, allowed):
        self.primary, self.local, self.allowed = primary, local, allowed

    def generate(self, messages, schema):
        try:
            return self.primary.generate(messages, schema)
        except ProviderError as exc:
            if not self.allowed or not exc.transient:
                raise
            result = self.local.generate(messages, schema)
            result.update(fallback=True, fallback_reason=str(exc))
            return result


class OllamaEmbeddings(HTTPProvider):
    def __init__(self, settings, transport=None):
        super().__init__(settings.timeout, transport)
        self.s = settings

    def embed(self, texts):
        result = self.request("POST", self.s.ollama_url + "/api/embed", json={"model": self.s.embed_model, "input": texts, "truncate": False})
        vectors = result.get("embeddings", [])
        if len(vectors) != len(texts) or not vectors or not vectors[0]:
            raise ProviderError("Embedding count/dimensions invalid")
        if any(len(v) != len(vectors[0]) or any(not math.isfinite(x) for x in v) for v in vectors):
            raise ProviderError("Embedding dimensions inconsistent or values non-finite")
        return vectors


def words(text):
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


class LocalMemory:
    def __init__(self, store): self.store = store
    def retrieve(self, tenant, query):
        terms = words(query)
        records = self.store.list("memory", tenant)
        return sorted((r for r in records if words(r["text"]) & terms), key=lambda r: -len(words(r["text"]) & terms))[:3]
    def save(self, tenant, key, value): self.store.put("memory", tenant, key, value)


class ChromaKnowledge:
    def __init__(self, settings, store, embeddings):
        self.store, self.embeddings, self.s = store, embeddings, settings
        self._client = None
        self.lock = threading.RLock()

    @property
    def client(self):
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        with self.lock:
            if self._client is None:
                try:
                    options = ChromaSettings(anonymized_telemetry=False)
                    if self.s.chroma_mode == "http":
                        self._client = chromadb.HttpClient(host=self.s.chroma_host, port=self.s.chroma_port, settings=options)
                    else:
                        self._client = chromadb.PersistentClient(path=str(self.s.data_dir / "chroma"), settings=options)
                except Exception as exc:
                    raise ProviderError("Cannot connect to the configured Chroma instance; check its address and whether it is running", True) from exc
            return self._client

    def health(self):
        endpoint = f"http://{self.s.chroma_host}:{self.s.chroma_port}"
        try:
            if self.s.chroma_mode == "http":
                response = httpx.get(endpoint + "/api/v2/heartbeat", timeout=3, trust_env=False)
                response.raise_for_status()
                ready = isinstance(response.json().get("nanosecond heartbeat"), int)
            else:
                ready = bool(self.client.heartbeat())
        except Exception:
            ready = False
        return {"provider": "chroma", "status": "ready" if ready else "unavailable", "mode": self.s.chroma_mode,
                "endpoint": endpoint if self.s.chroma_mode == "http" else str(self.s.data_dir / "chroma"),
                "collection": self.collection_name("local")}

    def collection_name(self, tenant):
        fingerprint = hashlib.sha256((tenant + self.s.embed_model + INDEX_VERSION).encode()).hexdigest()[:24]
        # HTTP mode shares a server with other projects; never reuse their collections.
        prefix = "integration_hub_" if self.s.chroma_mode == "http" else "knowledge_"
        return prefix + fingerprint

    def collection(self, tenant):
        return self.client.get_or_create_collection(self.collection_name(tenant), embedding_function=None,
                                                  metadata={"hnsw:space": "cosine", "embedding_model": self.s.embed_model})

    def rebuild(self, tenant):
        with self.lock:
            docs = self.store.list("document", tenant)
            if not docs: return 0
            chunks = []
            for d in docs:
                for i, text in enumerate(chunk_text(d["text"])):
                    chunks.append({"id": d["id"] + f":{i}", "text": text, "title": d["title"], "document_id": d["id"]})
            vectors = self.embeddings.embed(embedding_inputs(self.s.embed_model, [c["text"] for c in chunks], "document"))
            col = self.collection(tenant)
            if col.count():
                col.delete(ids=col.get()["ids"])
            col.upsert(ids=[c["id"] for c in chunks], embeddings=vectors, documents=[c["text"] for c in chunks],
                       metadatas=[{"title": c["title"], "document_id": c["document_id"]} for c in chunks])
            self.store.put("index", tenant, "current", {"model": self.s.embed_model, "version": INDEX_VERSION, "dimensions": len(vectors[0]), "chunks": len(chunks), "digest": self.digest(docs)})
            return len(chunks)

    @staticmethod
    def digest(docs):
        return hashlib.sha256(json.dumps(sorted(docs, key=lambda d: d["id"]), sort_keys=True).encode()).hexdigest()

    def search(self, tenant, query, top_k=3):
        with self.lock:
            docs = self.store.list("document", tenant)
            if not docs: return []
            index = self.store.get("index", tenant, "current")
            if not index or index.get("version") != INDEX_VERSION or index["model"] != self.s.embed_model or index["digest"] != self.digest(docs) or self.collection(tenant).count() == 0:
                self.rebuild(tenant)
            vector = self.embeddings.embed(embedding_inputs(self.s.embed_model, [query], "query"))[0]
            result = self.collection(tenant).query(query_embeddings=[vector], n_results=min(top_k, self.collection(tenant).count()))
            items = []
            for id, text, meta, distance in zip(result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]):
                items.append({"id": id, "text": text, "title": meta["title"], "document_id": meta["document_id"], "score": round(1 - distance, 4), "kind": "runbook"})
            return items


class ProviderFactory:
    def __init__(self, settings, store):
        self.settings, self.store = settings, store
        local = OllamaLLM(settings)
        self.llm = local if settings.profile == "local_free" else FallbackLLM(OpenAICompatibleLLM(settings, store), local, settings.local_fallback)
        self.embeddings = OllamaEmbeddings(settings)
        self.memory = LocalMemory(store)
        self.observability = store
        from .extensions import (DisabledFeature, PineconeKnowledge, Mem0Memory, LangfuseTrace, KeenableSearch, ElevenLabsVoice)
        self.knowledge = PineconeKnowledge(settings, store, self.embeddings) if settings.effective_vector_store == "pinecone" else ChromaKnowledge(settings, store, self.embeddings)
        self.search = DisabledFeature("Web search is disabled in the offline profile")
        self.voice = DisabledFeature("Voice is optional and disabled; local speech models are not installed")
        if settings.profile == "sponsored":
            self.memory = Mem0Memory(settings, store)
            self.observability = LangfuseTrace(settings, store)
            self.search = KeenableSearch(settings, store)
            self.voice = ElevenLabsVoice(settings, store)

    def status(self):
        s = self.settings
        try:
            result = httpx.get(s.ollama_url + "/api/tags", timeout=3, trust_env=False).json()
            names = [m["name"] for m in result.get("models", [])]
            llm_ready = s.model in names
            embed_ready = s.embed_model in names
            ollama = "ready" if llm_ready and embed_ready else "model_missing"
        except (httpx.HTTPError, ValueError, KeyError):
            ollama = "unavailable"
        status = {"llm": {"provider": "ollama" if s.profile == "local_free" else ("nebius" if s.profile == "sponsored" else "openrouter"),
                        "status": ollama if s.profile == "local_free" else "not_live_verified" if s.allow_cloud and s.cloud_key and s.data_consent else "disabled"},
                "embeddings": {"provider": "ollama", "status": ollama},
                "vector_store": self.knowledge.health() if s.effective_vector_store == "chroma" else {"provider": "pinecone", "status": "not_live_verified"},
                "memory": {"provider": "sqlite", "status": "local"},
                "observability": {"provider": "sqlite traces", "status": "local"},
                "voice": {"provider": "none", "status": "disabled"},
                "web_search": {"provider": "none", "status": "disabled_offline"},
                "meetings": {"provider": "text export import", "status": "local"}}
        if s.profile == "sponsored":
            for feature, name in {"memory":"mem0 with canonical SQLite", "observability":"Langfuse export with local traces", "voice":"elevenlabs", "web_search":"keenable"}.items():
                status[feature] = {"provider":name, "status":"not_live_verified" if s.allow_cloud and s.allow_paid and s.data_consent else "disabled"}
            if s.effective_vector_store == "pinecone":
                status["vector_store"]["status"] = "not_live_verified" if s.allow_cloud and s.allow_paid and s.data_consent else "disabled"
        return status
