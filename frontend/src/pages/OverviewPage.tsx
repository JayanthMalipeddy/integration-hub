import type { PageState } from "../hooks/useHub";
import {
  ArrowUpRight,
  ArrowRight,
  GitBranch,
  ShieldCheck,
  Activity,
  BookOpen,
  Gauge,
  Clock3,
} from "lucide-react";
import { Stat } from "../components/common";
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
  lastUpdated,
}: Pick<
  PageState,
  | "setPage"
  | "dashboard"
  | "samples"
  | "useSample"
  | "latest"
  | "taskMetric"
  | "running"
  | "waiting"
  | "runList"
  | "lastUpdated"
>) {
  return (
    <>
      <div className="overview-context">
        <span>
          <span className="context-dot" />
          Evidence-backed incident review
        </span>
        <span>
          {lastUpdated
            ? `Updated ${new Date(lastUpdated).toLocaleTimeString()}`
            : "Waiting for data"}
        </span>
      </div>
      <div className="stats overview-stats">
        <Stat
          icon={Activity}
          label="Investigations"
          value={dashboard.runs.length}
          detail={`${running} currently running`}
        />
        <Stat
          icon={ShieldCheck}
          label="Awaiting review"
          value={waiting}
          detail="Human approval before writes"
        />
        <Stat
          icon={BookOpen}
          label="Knowledge sources"
          value={dashboard.documents ?? 0}
          detail="Canonical source documents"
        />
        <Stat
          icon={Gauge}
          label="Measured task pass rate"
          value={taskMetric ? taskMetric.percent + "%" : "Not run"}
          detail={
            taskMetric
              ? `${taskMetric.passed}/${taskMetric.total} synthetic cases · ${latest.model}`
              : "No completed benchmark"
          }
        />
      </div>
      <div className="overview-grid">
        <section className="review-card">
          <div className="section-heading">
            <span className="feature-icon">
              <ShieldCheck size={24} />
            </span>
            <span className="eyebrow">REVIEW QUEUE</span>
          </div>
          <h2>
            {waiting
              ? `${waiting} investigation${waiting === 1 ? "" : "s"} need your review`
              : "Your review queue is clear"}
          </h2>
          <p>
            {waiting
              ? "Check the hypothesis and cited evidence before approving a local recovery ticket."
              : "New findings will appear here when an investigation is ready for your decision."}
          </p>
          <button
            onClick={() =>
              setPage(waiting ? "Incident analysis" : "Agent workspace")
            }
          >
            {waiting ? "Review investigations" : "Start an investigation"}
            <ArrowUpRight size={16} />
          </button>
        </section>
        <section className="workflow-card">
          <div className="section-heading">
            <h2>From signal to decision</h2>
            <span className="muted">Investigation workflow</span>
          </div>
          <div className="workflow-strip">
            {[
              "Triage logs",
              "Retrieve sources",
              "Verify findings",
              "Human review",
            ].map((step, index) => (
              <div key={step}>
                <span className="workflow-number">0{index + 1}</span>
                <strong>{step}</strong>
                {index < 3 && <ArrowRight size={16} />}
              </div>
            ))}
          </div>
          <div className="workflow-note">
            <Clock3 size={16} />
            <span>
              Local inference can take several minutes. Follow recorded stages
              in the execution timeline.
            </span>
          </div>
        </section>
      </div>
      <section>
        <div className="section-heading">
          <div>
            <h2>Recent investigations</h2>
            <p className="section-description">
              Follow active work and revisit completed findings.
            </p>
          </div>
          <button
            className="text-button"
            onClick={() => setPage("Incident analysis")}
          >
            View all
            <ArrowUpRight size={16} />
          </button>
        </div>
        {runList}
      </section>
      <div className="section-heading">
        <div>
          <h2>Explore a scenario</h2>
          <p className="section-description">
            Synthetic examples to explore the investigation flow.
          </p>
        </div>
        <span className="badge">Demo data</span>
      </div>
      <div className="scenario-grid">
        {samples.slice(0, 4).map((s) => (
          <button key={s.id} className="scenario" onClick={() => useSample(s)}>
            <GitBranch size={22} />
            <h3>{s.title}</h3>
            <p>{s.service}</p>
            <span>
              Investigate
              <ArrowUpRight size={16} />
            </span>
          </button>
        ))}
      </div>
    </>
  );
}
