import type { PageState } from "../hooks/useHub";
import { ArrowUpRight, LoaderCircle, ShieldCheck } from "lucide-react";
import { Badge, Empty } from "../components/common";
import type { Item } from "../types";
import { api } from "../lib/api";
export function InvestigationPage({
  setPage,
  selected,
  run,
  setNotice,
  busy,
  approvalNote,
  setApprovalNote,
  setConfirmAction,
  act,
  approve,
  finding,
  runPicker,
}: Pick<
  PageState,
  | "setPage"
  | "selected"
  | "run"
  | "error"
  | "setNotice"
  | "busy"
  | "title"
  | "approvalNote"
  | "setApprovalNote"
  | "setConfirmAction"
  | "act"
  | "approve"
  | "finding"
  | "runPicker"
>) {
  return (
    <>
      {runPicker}
      {!run ? (
        <Empty text="Choose an investigation or start one in the agent workspace." />
      ) : (
        <>
          <div className="section-heading">
            <h2>{run.incident.title}</h2>
            <Badge value={run.status} />
          </div>
          {run.status === "running" && (
            <div className="alert">
              <LoaderCircle className="spin" size={18} />
              Stage:{" "}
              {run.traces?.filter((t: Item) => t.phase === "started").at(-1)
                ?.node || "triage"}{" "}
              ·{" "}
              {Math.max(
                0,
                Math.floor((Date.now() - Date.parse(run.created_at)) / 1000),
              )}{" "}
              seconds elapsed · {run.analysis_attempts || 0} analysis attempts
              completed. Progress refreshes every five seconds.
            </div>
          )}
          {run.error && <div className="alert error">{run.error}</div>}
          {finding && (
            <div className="two-columns">
              <section>
                <div className="section-heading">
                  <h2>Root-cause hypothesis</h2>
                  <Badge value={finding.confidence + " confidence"} />
                </div>
                <p className="finding">{finding.hypothesis}</p>
                <div className="uncertainty">
                  <strong>What remains uncertain</strong>
                  <p>{finding.uncertainty}</p>
                </div>
                <h3>Recommended checks</h3>
                <ol>
                  {finding.checks.map((c: string, i: number) => (
                    <li key={i}>{c}</li>
                  ))}
                </ol>
                <h3>Proposed recovery</h3>
                <ol>
                  {finding.recovery.map((c: string, i: number) => (
                    <li key={i}>{c}</li>
                  ))}
                </ol>
              </section>
              <section>
                <h2>Evidence trail</h2>
                {finding.citations.map((c: Item, i: number) => (
                  <blockquote key={i}>
                    <code>{c.source_id}</code>
                    <p>“{c.quote}”</p>
                    <Badge
                      value={
                        run.validation?.citations[i]?.valid
                          ? "valid_quote"
                          : "unverified"
                      }
                    />
                  </blockquote>
                ))}
                <p className="muted">{run.validation?.scope}</p>
                <details>
                  <summary>Retrieved context</summary>
                  {run.evidence?.map((e: Item) => (
                    <div key={e.id}>
                      <h4>{e.title}</h4>
                      <p>{e.text}</p>
                    </div>
                  ))}
                </details>
              </section>
            </div>
          )}
          {run.status === "awaiting_approval" && (
            <section className="approval-panel">
              <ShieldCheck />
              <div>
                <h2>Review before creating a recovery ticket</h2>
                <p>
                  This writes a local ticket and saves a reviewed hypothesis to
                  memory. It does not change an external system.
                </p>
                <label>
                  Review note
                  <input
                    value={approvalNote}
                    onChange={(e) => setApprovalNote(e.target.value)}
                    placeholder="Add verification notes or constraints"
                  />
                </label>
                <div className="actions">
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() => setConfirmAction("approve")}
                  >
                    Review and approve
                  </button>
                  <button disabled={busy} onClick={() => void approve(false)}>
                    Decline ticket
                  </button>
                </div>
              </div>
            </section>
          )}
          {run.status === "failed" && (
            <button
              onClick={() =>
                void act(async () => {
                  await api(`/runs/${selected}/retry`, { method: "POST" });
                  setNotice("Resuming from the saved checkpoint.");
                })
              }
            >
              Retry from checkpoint
            </button>
          )}
          <button onClick={() => setPage("Execution timeline")}>
            View execution timeline <ArrowUpRight size={16} />
          </button>
        </>
      )}
    </>
  );
}
