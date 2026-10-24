import type { PageState } from "../hooks/useHub";
import { ArrowUpRight, Check, GitBranch, ShieldCheck } from "lucide-react";
import { Stat } from "../components/common";
import React from "react";
export function OverviewPage({
  setPage,
  dashboard,
  samples,
  useSample,
  latest,
  taskMetric,
  running,
  waiting,
  runList,
}: Pick<
  PageState,
  | "setPage"
  | "dashboard"
  | "samples"
  | "title"
  | "service"
  | "useSample"
  | "latest"
  | "taskMetric"
  | "running"
  | "waiting"
  | "runList"
>) {
  return (
    <>
      <div className="hero">
        <div>
          <span className="eyebrow">INCIDENT REVIEW</span>
          <h2>
            Investigate API failures
            <br />
            with the relevant runbooks.
          </h2>
          <p>
            Add a log excerpt to find relevant guidance.
            <br />
            Check the findings before approving a recovery ticket.
          </p>
          <button onClick={() => setPage("Agent workspace")}>
            Try an example <ArrowUpRight size={16} />
          </button>
        </div>
        <div className="flow-visual">
          {[
            "Triage logs",
            "Retrieve evidence",
            "Review hypothesis",
            "Approve recovery",
          ].map((s, i) => (
            <React.Fragment key={s}>
              <div className={"flow-step step-" + i}>
                <span>{i + 1}</span>
                {s}
                {i === 3 ? <ShieldCheck size={17} /> : <Check size={17} />}
              </div>
              {i < 3 && <div className="flow-line" />}
            </React.Fragment>
          ))}
        </div>
      </div>
      <div className="stats">
        <Stat
          label="Investigations"
          value={dashboard.runs.length}
          detail={`${running} currently running`}
        />
        <Stat
          label="Awaiting review"
          value={waiting}
          detail="No writes before approval"
        />
        <Stat
          label="Knowledge sources"
          value={dashboard.documents || 0}
          detail="Canonical documents retained"
        />
        <Stat
          label="Measured task pass rate"
          value={taskMetric ? taskMetric.percent + "%" : "Not run"}
          detail={
            taskMetric
              ? `${taskMetric.passed}/${taskMetric.total} synthetic cases · ${latest.model}`
              : "Run the evaluation harness"
          }
        />
      </div>
      <section>
        <div className="section-heading">
          <h2>Recent investigations</h2>
          <span className="muted">Live application data</span>
        </div>
        {runList}
      </section>
      <div className="section-heading">
        <h2>Start with a synthetic scenario</h2>
        <span className="muted">Demo data · no production logs</span>
      </div>
      <div className="scenario-grid">
        {samples.slice(0, 4).map((s) => (
          <button key={s.id} className="scenario" onClick={() => useSample(s)}>
            <GitBranch size={22} />
            <h3>{s.title}</h3>
            <p>{s.service}</p>
            <span>
              Investigate <ArrowUpRight size={15} />
            </span>
          </button>
        ))}
      </div>
    </>
  );
}
