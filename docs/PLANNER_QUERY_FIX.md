# Planner query-length recovery

A model-generated Decision.query longer than 200 characters previously stopped an investigation with a Pydantic validation error, even when the submitted incident satisfied its input limits.

The planner now receives explicit query/reason limits. Before schema validation, generated queries are compacted to at most 200 characters using whole terms, deduplication and priority for diagnostic codes/acronyms, including ORA codes, HTTP status codes and numeric error labels. This changes only the generated search query; submitted evidence retains the existing secret-redaction behavior. No additional model request is required. Long display reasons are bounded to 300 characters; request_human carries an empty query.

Tool allowlisting, strict types and extra-field rejection remain enforced. An unusable decision causes a needs_human handoff before retrieval, records the model's returned usage and reports a clear message instead of exposing raw validation details. Trace events identify normalized fields without recording the discarded raw response. Evidence validation and approval requirements are unchanged.

## Verification

- Complete backend suite: 127 passed (7.03 seconds).
- Regression cases cover the anonymized HTTP 408 / CPU / PBKDF2 / JDBC scenario, query boundaries, diagnostic codes at the end, Unicode, invalid types/tools/extra fields, empty queries, human handoff and a verified workflow reaching approval without unapproved writes.
- Actual local qwen2.5:latest planner smoke check: 75-character query, search_runbooks selected, one retrieval call, 504 input tokens and 57 output tokens; 32.58 seconds. Result: needs_human because the test intentionally used an empty knowledge fixture.
- Local check artifact: runtime/verifications/planner-query-fix-4cc26cae/report.json.
- Tests use isolated temporary SQLite stores and fixture retrieval. The live check did not access shared Chroma or call paid providers.
- API restarted after confirming zero running investigations; authenticated health and shared Chroma/UI connectivity checked.

This verifies planner recovery, not diagnosis accuracy for arbitrary production incidents. No full workflow benchmark was rerun. Oracle/webMethods knowledge coverage and the larger manual-evidence follow-up flow remain separate work. Historical failed investigations retain their original result; submit a new investigation to use the fix.

Pre-change backups: runtime/planner-fix-backups/20261025-141853.
