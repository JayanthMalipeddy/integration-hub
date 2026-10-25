# Provider matrix and verification boundary

| Capability | LOCAL_FREE | HYBRID | SPONSORED | Verification |
|---|---|---|---|---|
| LLM | Ollama Qwen | OpenRouter explicitly selected `:free` model | Nebius OpenAI-compatible API | Ollama live; cloud mocked contracts only |
| Embeddings | Ollama nomic | Same local model | Same local model | Live; intentionally reusable across vector vendors |
| Vector store | Chroma | Chroma | Pinecone adapter | Chroma live; Pinecone scoped request/response contract tested |
| Memory | Canonical SQLite | Canonical SQLite | Mem0 retrieval + canonical SQLite/outbox | Local live; cloud contract tested |
| Observability | SQLite trace events | SQLite trace events | Local traces + explicit Langfuse OTLP export | Local live; cloud export contract tested |
| Voice | Disabled | Disabled | Explicit ElevenLabs text-to-speech command | Mocked audio transport only; no live call |
| Web search | Disabled offline | Disabled | Explicit Keenable search command | Mocked contract only; not automatically sent incident logs |
| Meeting processing | Text/JSON import | Text/JSON import | Granola text/JSON exports through same import | Generic ingestion tested; no recording/transcription |

`AI_PROFILE` selects this entire mapping without changing the graph. A missing key produces an actionable failure; it is never treated as permission to try another cloud service. Cloud status is displayed as disabled or not-live-verified rather than healthy based on configuration alone. Local status checks the actual Ollama model list.

## Enabling a cloud profile deliberately

Set process environment variables from `.env.example`. For inference, configure CLOUD_API_KEY, CLOUD_MODEL, ALLOW_CLOUD and CLOUD_DATA_CONSENT. Sponsored operations also require ALLOW_PAID, MAX_COST_USD and configured input/output rates. The budget ledger persists conservative reservations before requests, including retry allowance. Estimates do not replace provider-side spending limits. Set hard caps/disable automatic top-ups at the provider before any billable use.

Hybrid only accepts a model ID ending in `:free` and sends a zero-price provider constraint. Free model availability, limits and structured-output support vary. No specific model was claimed available without a live check. [OpenRouter free variants](https://openrouter.ai/docs/guides/routing/model-variants/free).

Optional sponsored services require their named credentials and a positive `*_MAX_REQUEST_USD` ceiling. Their explicit operator commands are:

```powershell
python -m scripts.extensions rebuild-cloud-index --approve-external
python -m scripts.extensions sync-memory --approve-external
python -m scripts.extensions export-trace --value RUN_ID --approve-external
python -m scripts.extensions search --value 'Public technical question' --approve-external
python -m scripts.extensions speak --value 'Approved public report text' --output report.mp3 --approve-external
```

These commands were **not executed against real services**. Operator consent is required because they can upload data or incur charges. Approval of a local recovery ticket does not automatically synchronize memory to Mem0 or export traces to Langfuse.

## References and limitations

- [Pinecone upsert](https://docs.pinecone.io/reference/api/2025-10/data-plane/upsert) and [query](https://docs.pinecone.io/reference/api/2025-10/data-plane/query): fixed API version; dimension and canonical-source checks included.
- [Mem0 add](https://docs.mem0.ai/api-reference/memory/add-memories) and [search](https://docs.mem0.ai/api-reference/memory/search-memories): v3 requests with tenant filters and canonical IDs. Remote extraction may be asynchronous; availability after a write is not guaranteed immediately. Explicit sync retries may create remote duplicates after ambiguous failures; local ticket writes are idempotent.
- [Langfuse OpenTelemetry](https://langfuse.com/integrations/native/opentelemetry): explicit OTLP JSON export. Local event timestamps remain inside event metadata; exported spans are event markers, not accurate reconstructed distributed span durations. Local trace export cannot recover historical cloud-only traces never imported.
- [ElevenLabs TTS](https://elevenlabs.io/docs/api-reference/text-to-speech/convert): caller selects a voice; no voice cloning, transcription or live voice agent is implemented.
- [Keenable search](https://docs.keenable.ai/api-reference/search): bounded public-query search. It is not part of the core incident planner's tool allowlist.
- No authoritative product/API contract for the prompt's exact name “Laya Router” was established; no dependency or capability was assumed.

Local Whisper/Piper, a self-hosted SearXNG service, Phoenix and full self-hosted Langfuse were deliberately not installed on the office laptop. The free core uses local text input and SQLite tracing; optional audio/search capabilities remain explicitly unavailable offline. Replit is an optional hosting surface, not a dependency.

## Local Chroma and paid model combination

The existing local Chroma service is used through HttpClient at 127.0.0.1:8082, with an integration_hub_ collection prefix. Set CHROMA_MODE=http in .env; embedded remains available. VECTOR_STORE=chroma keeps Chroma for any AI_PROFILE, including sponsored. The table above describes profile defaults when VECTOR_STORE=auto. Changing these settings requires a backend restart; it does not enable paid calls or transmit data by itself.
