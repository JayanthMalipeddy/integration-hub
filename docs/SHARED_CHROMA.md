# Shared local Chroma

One database and one UI serve the existing local projects. No software was installed.

- Database: http://127.0.0.1:8082
- UI: http://127.0.0.1:8090
- UI connection URL: http://127.0.0.1:8090/chroma (same-origin proxy)
- Tenant/database: `default_tenant` / `default_database`
- Active data: `C:\Projects\chroma db\server-data`

```powershell
& 'C:\Projects\chroma db\start-shared.ps1'
```

The launcher reuses healthy services, serializes concurrent starts, and refuses occupied ports instead of choosing another port. Integration Hub's `scripts/start-chroma.ps1` delegates here. OS login autostart has not been configured. The launcher uses the existing Integration Hub Chroma executable and existing UI node_modules; keep those installations available.

## Connect another project

```python
import chromadb
client = chromadb.HttpClient(host="127.0.0.1", port=8082)
collection = client.get_or_create_collection("your_project_documents")
```

Use a project-specific collection prefix. Keep incompatible embedding models and dimensions in separate collections. A collection prefix separates data by convention; it is not an access-control boundary. This service is bound to localhost for trusted local projects. Do not create a new per-project server, Docker Chroma service, or PersistentClient in application startup. Temporary isolated test stores are appropriate and must never target live collections.

## Migration

Consolidated seven original stores into 22 collections and 154 records on 2026-10-25. Original stores were retained, and backup copies plus logical exports are in `backups/unify-20261025-130226`. IDs, documents, metadata, vector dimensions and distance metrics were preserved without re-embedding. Cosine indexing may introduce floating-point normalization differences; verification uses rtol=1e-6, atol=1e-7.

`collections.json` records the initial mapping. `verification.json` records the final audit. `verify-migration.py` compares live data against the frozen original exports; later legitimate indexing or new documents can change this baseline. ReguGraph's pre-existing index refresh can rebuild its own corpus when the embedding model changes. Retrieval tests now use isolated temporary databases instead of rebuilding the shared live collection.

| Source | Shared collection | Records | Dimensions |
| --- | --- | ---: | --- |
| integration-hub-http | `integration_hub_8ce5c1fd8bc466e987ff2b80` | 4 | 768 |
| integration-hub-http | `integration_hub_2fe57f8aaca8120240180107` | 4 | 768 |
| integration-hub-http | `integration_hub_f247db265d73d13e979438b5` | 4 | 768 |
| integration-hub-http | `integration_hub_364de058c13a4410932d00b7` | 4 | 768 |
| integration-hub-http | `integration_hub_d600353794beaa291294c8d6` | 4 | 768 |
| integration-hub-http | `integration_hub_6959d3f48b10adcedbc6be4e` | 4 | 768 |
| integration-hub-http | `integration_hub_7b7faeb7e7b9d034bf3d5a00` | 4 | 768 |
| regugraph | `integration_hub_18bdaaf71c500a397ddde457` | 4 | 768 |
| regugraph | `integration_hub_60d80b327743c3ab56c4e4dc` | 4 | 768 |
| regugraph | `cbuae_regulations` | 15 | 384 |
| regugraph | `cbuae_eval_runs` | 2 | 384 |
| mohesr | `mohesr_test_notes` | 10 | 384 |
| vector-current | `vectorembeddings_orbit_handbook_c1000` | 11 | 768 |
| vector-current | `vectorembeddings_cbuae_regulations` | 15 | 384 |
| vector-current | `vectorembeddings_orbit_handbook_c500` | 14 | 768 |
| vector-current | `vectorembeddings_my_docs` | 9 | 768 |
| vector-current | `vectorembeddings_cbuae_eval_runs` | 2 | 384 |
| vector-current | `vectorembeddings_orbit_handbook_c300` | 19 | 768 |
| vector-legacy-rag | `vectorembeddings_legacy_learning_notes` | 12 | 384 |
| vector-legacy-rag | `vectorembeddings_legacy_my_docs` | 5 | 384 |
| vector-legacy-notes | `vectorembeddings_legacy_langchain` | 0 | - |
| integration-hub-embedded | `integration_hub_archive_knowledge_60d80b327743c3ab56c4e4dc` | 4 | 768 |

## Recovery

The originals remain at their previous paths; none were deleted. Pre-change project files are in the backup's `project-config-before` directory. To reverse the migration, first stop the affected applications and shared services, preserve any writes made since migration, restore the relevant project connection files from that backup, and explicitly start the previous service against its original data. Never open the active shared data directory with a second server or embedded client. Returning to an original store alone will not include new writes made after migration.

For future backups, stop database writers and the server before copying the complete `server-data` directory, then restart with the shared launcher. Scheduled backups and container-to-host connectivity are not configured or verified by this local consolidation.

## Verification completed

- Integration Hub: 111 tests passed.
- ReguGraph: 45 tests passed with graph and retrieval calls isolated from live collections.
- Post-test migration audit: all 22 collections and 154 records preserved.
- Stored-vector queries succeeded for all 21 nonempty collections.
- Shared startup invoked twice without changing either listener PID; only 8082 and 8090 listen, not 8080 or 8081.
- UI health and proxied collection listing returned HTTP 200.
- MOHESR scripts and 41 notebook Python cells passed syntax checks; notebooks were not executed or reindexed.

## Portable connection to the existing shared service

Integration Hub does not provision another Chroma instance. On this laptop, keep the existing server at 127.0.0.1:8082 and UI at 127.0.0.1:8090. The launcher defaults to the sibling `chroma db` directory. On another approved workstation, set `SHARED_CHROMA_ROOT` to its separately provisioned shared-service directory containing `start-shared.ps1`, or pass `-SharedRoot` explicitly. A missing launcher produces an actionable error and does not select a new port. This setting locates the launcher; it does not change the data directory or application collection prefix.

A clean checkout requires separately provisioned Ollama/model weights and the shared Chroma/UI installation. The repository does not silently install these office-laptop prerequisites. Copy `.env.example` to a private `.env`, configure the existing HTTP endpoint, run `python -m scripts.configure_access`, and start the application. Dependency installation commands in README are instructions for an approved clean setup, not operations performed during this repair. Never run a second server against `server-data`.
