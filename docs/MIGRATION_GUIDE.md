# Migration and recovery

## Canonical assets

`runtime/hub.sqlite3` holds sanitized documents, incidents, results, provider usage, decisions, reviewed hypotheses, traces, recovery tickets and evaluations. `runtime/checkpoints.sqlite3` holds durable LangGraph state/interrupts. Source prompts and schemas are versioned in `backend/app/workflow.py` and `models.py`; synthetic datasets are under `data`. Provider secrets are never exported. Process configuration is documented separately in `.env.example`.

## Backup and restore

Stop the backend and any evaluation process before backing up both databases so their cross-database state is consistent. SQLite's backup API creates each snapshot, and a manifest hashes both files. A backup contains no vector index, environment file or key.

```powershell
python -m scripts.backup backup runtime my-backup.zip
python -m scripts.backup restore my-backup.zip restored-runtime
$env:DATA_DIR='restored-runtime'
$env:AI_PROFILE='local_free'
python -m scripts.rebuild
python -m scripts.serve
```

Restore refuses nonempty targets, unexpected ZIP paths, duplicate entries, mismatched checksums and oversized archives. The operator must protect the archive: it contains incident information and is not encrypted by this application. Backup/restore round trip and traversal rejection are tested.

## Sponsored to local

1. Stop the backend; keep canonical databases and create a backup.
2. Set AI_PROFILE=local_free. Remove cloud credentials from the process environment and leave cloud/paid/data consent disabled.
3. Ensure the chosen Ollama language and embedding models exist locally.
4. Rebuild the local index from canonical documents using `python -m scripts.rebuild`.
5. Restart the backend and verify provider status, a representative query and a new approval workflow.

Mem0-derived facts are not authoritative: the adapter maps cloud search hits back to canonical reviewed memories. Locally created memory remains usable after cloud credits expire. Existing cloud-only memory must first be exported and reviewed for ingestion; the application cannot recover data it never stored.

Pinecone embeddings are not copied into incompatible local collections. The local rebuild recomputes embeddings from source text. Collection/namespace identity includes the embedding model; the Pinecone adapter also validates configured dimension. When changing model or dimension, use a compatible Pinecone index and explicitly rebuild. Old cloud namespaces are not automatically deleted, to avoid destructive cleanup.

Langfuse events generated here have canonical local copies. Other historical cloud traces need the provider's export; this implementation does not promise a lossless conversion of arbitrary distributed traces. Granola exports can be ingested as UTF-8 text/JSON, retaining their text; audio/transcription features are not migrated.

Paused runs retain the original profile in state. Failed-run retry refuses a changed profile to prevent an unreviewed data destination change. Finish or explicitly restart those investigations under the intended profile. The core workflow needs no vendor-specific source changes.

## Existing Chroma server

When CHROMA_MODE=http, vectors live in the running server's storage, not runtime/chroma. The application backup still contains canonical source text and checkpoints; rebuild the project-specific server collection after restore. Do not copy or edit an active Chroma server's SQLite files. The original embedded index is retained for CHROMA_MODE=embedded. Other projects' server collections are not migrated, reset or deleted.
