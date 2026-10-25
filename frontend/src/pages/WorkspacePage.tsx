import type { PageState } from "../hooks/useHub";
import {
  BookOpen,
  ChevronRight,
  Database,
  LoaderCircle,
  Play,
  ShieldCheck,
} from "lucide-react";
import { Badge } from "../components/common";
export function WorkspacePage({
  samples,
  busy,
  title,
  setTitle,
  service,
  setService,
  logs,
  setLogs,
  useSample,
  start,
}: Pick<
  PageState,
  | "samples"
  | "busy"
  | "title"
  | "setTitle"
  | "service"
  | "setService"
  | "logs"
  | "setLogs"
  | "useSample"
  | "start"
>) {
  return (
    <div className="two-columns">
      <section>
        <h2>Open an investigation</h2>
        <p className="muted">
          Paste a small, sanitized log excerpt. The agent will select a
          read-only tool and build a reviewable hypothesis.
        </p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            if (!busy && title.length >= 3 && logs.length >= 3) void start();
          }}
        >
          <label>
            Incident title
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={160}
              placeholder="e.g. Customer API returns 401"
            />
          </label>
          <label>
            Affected service
            <input
              value={service}
              onChange={(e) => setService(e.target.value)}
              maxLength={80}
            />
          </label>
          <label>
            Log evidence
            <textarea
              className="code-input"
              rows={10}
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              maxLength={12000}
              placeholder="Paste timestamps, HTTP errors and correlation IDs…"
            />
          </label>
          <p className="muted">
            A title and log evidence of at least three characters are required.
          </p>
          <div className="form-footer">
            <small>{logs.length}/12,000 characters</small>
            <button
              className="primary"
              disabled={busy || title.length < 3 || logs.length < 3}
              type="submit"
            >
              {busy ? (
                <LoaderCircle className="spin" size={16} />
              ) : (
                <Play size={16} />
              )}
              Start investigation
            </button>
          </div>
        </form>
      </section>
      <section>
        <h2>Available tools</h2>
        <div className="tool-card">
          <BookOpen />
          <div>
            <strong>Search runbooks</strong>
            <p>Local embeddings and Chroma retrieve source passages.</p>
          </div>
          <Badge value="read_only" />
        </div>
        <div className="tool-card">
          <Database />
          <div>
            <strong>Search incident memory</strong>
            <p>Find previously reviewed hypotheses.</p>
          </div>
          <Badge value="read_only" />
        </div>
        <div className="tool-card">
          <ShieldCheck />
          <div>
            <strong>Create recovery ticket</strong>
            <p>Local ticket only. Requires your explicit approval.</p>
          </div>
          <Badge value="approval" />
        </div>
        <h3>Try a scenario</h3>
        {samples.map((s) => (
          <button
            className="sample-row"
            key={s.id}
            onClick={() => useSample(s)}
          >
            {s.title}
            <ChevronRight size={15} />
          </button>
        ))}
      </section>
    </div>
  );
}
