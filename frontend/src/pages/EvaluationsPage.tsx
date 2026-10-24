import { useState } from "react";
import { ChevronRight } from "lucide-react";
import type { PageState } from "../hooks/useHub";
import { Badge, Empty, Stat } from "../components/common";
import type { Item } from "../types";
export function EvaluationsPage({
  setPage,
  setSelected,
  latest: newest,
  dashboard,
}: Pick<PageState, "setPage" | "setSelected" | "latest" | "dashboard">) {
  const [evaluationId, setEvaluationId] = useState("");
  const latest =
    dashboard.evaluations.find((e: Item) => e.id === evaluationId) || newest;
  return (
    <>
      <label className="run-picker">
        Benchmark run
        <select
          value={evaluationId}
          onChange={(e) => setEvaluationId(e.target.value)}
        >
          <option value="">Latest completed benchmark</option>
          {dashboard.evaluations.map((e: Item) => (
            <option key={e.id} value={e.id}>
              {new Date(e.timestamp).toLocaleString()} ? {e.dataset_size} cases
              ? {e.metrics.task_passed.percent}%
            </option>
          ))}
        </select>
      </label>
      {!latest ? (
        <Empty text="No benchmark has been run. Execute python -m evaluations.run from the project directory." />
      ) : (
        <>
          <div className="alert">
            Executed {new Date(latest.timestamp).toLocaleString()} ·{" "}
            {latest.profile} · {latest.model} · {latest.dataset_size} synthetic
            cases
          </div>
          {latest.configuration && (
            <section>
              <h2>Benchmark configuration</h2>
              <p>
                {latest.configuration.chroma_mode} Chroma ·{" "}
                {latest.configuration.embedding_model} ·{" "}
                {latest.configuration.index_version}
              </p>
              <p>
                {latest.approval_mode}. Task pass means a valid proposal or the
                expected handoff; completion measures local ticket and memory
                writes after simulated approval.
              </p>
              <p>
                Baseline: {latest.split_metrics.baseline.task_passed.passed}/
                {latest.split_metrics.baseline.task_passed.total} · Holdout:{" "}
                {latest.split_metrics.holdout.task_passed.passed}/
                {latest.split_metrics.holdout.task_passed.total}
              </p>
              <details>
                <summary>Dataset and code fingerprints</summary>
                <p style={{ overflowWrap: "anywhere" }}>
                  Dataset: {latest.dataset_version}
                  <br />
                  Code: {latest.code_version}
                </p>
              </details>
            </section>
          )}
          <div className="stats">
            {Object.entries(latest.metrics).map(([key, m]) => (
              <Stat
                key={key}
                label={key.replaceAll("_", " ")}
                value={
                  (m as Item).percent === null
                    ? "Not measured"
                    : (m as Item).percent + "%"
                }
                detail={`${(m as Item).passed}/${(m as Item).total} applicable checks`}
              />
            ))}
          </div>
          <section>
            <h2>Measured retrieval comparison</h2>
            <p className="muted">
              Four-runbook corpus. Vector timing includes local query embedding.
              See the run limitations for repetition counts and measurement
              order. These results apply to this workload.
            </p>
            {["lexical", "vector"].map((mode) => {
              const rows = latest.retrieval_comparison.filter(
                (r: Item) => r.mode === mode,
              );
              const mean =
                rows.reduce((n: number, r: Item) => n + r.latency_ms, 0) /
                (rows.length || 1);
              return (
                <div className="benchmark-row" key={mode}>
                  <strong>{mode}</strong>
                  <div className="bar-track">
                    <div
                      style={{
                        width:
                          (100 * mean) /
                            Math.max(
                              1,
                              ...["lexical", "vector"].map((m) => {
                                const rs = latest.retrieval_comparison.filter(
                                  (r: Item) => r.mode === m,
                                );
                                return (
                                  rs.reduce(
                                    (n: number, r: Item) => n + r.latency_ms,
                                    0,
                                  ) / (rs.length || 1)
                                );
                              }),
                            ) +
                          "%",
                      }}
                    />
                  </div>
                  <span>
                    {mean.toFixed(2)} ms mean ·{" "}
                    {rows.filter((r: Item) => r.top1_correct).length}/
                    {rows.length} top-1
                  </span>
                </div>
              );
            })}
          </section>
          <section>
            <h2>Case-level evidence</h2>
            {latest.results.map((r: Item) => (
              <details className="evaluation-case" key={r.case}>
                <summary className="case-summary">
                  <ChevronRight
                    className="case-chevron"
                    size={16}
                    aria-hidden="true"
                  />
                  <span className="case-name">{r.case}</span>
                  <Badge value={r.task_passed ? "passed" : "failed"} />
                  <span className="case-duration">
                    {(r.latency_ms / 1000).toFixed(1)} s
                  </span>
                </summary>
                <pre>{JSON.stringify(r, null, 2)}</pre>
                {!latest.configuration && (
                  <button
                    onClick={() => {
                      setSelected(r.run_id);
                      setPage("RCA investigation");
                    }}
                  >
                    Open investigation
                  </button>
                )}
              </details>
            ))}
            <p className="muted">{latest.limitations}</p>
            <h3>Not measured</h3>
            <ul>
              {latest.not_measured.map((x: string) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
            <p>
              Sponsored and hybrid: not run without credentials and explicit
              consent.
            </p>
          </section>
        </>
      )}
    </>
  );
}
