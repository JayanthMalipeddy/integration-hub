import { useState } from "react";

type Observation = { source_id: string; line_id: string; quote: string };
type Props = {
  runId: string;
  revision: number;
  status: string;
  observations: Observation[];
  questions: string[];
  busy: boolean;
  act: (fn: () => Promise<void>) => Promise<void>;
  setNotice: (text: string) => void;
};
import { api } from "../lib/api";

export function EvidenceFollowUp({
  runId,
  revision,
  status,
  observations,
  questions,
  busy,
  act,
  setNotice,
}: Props) {
  const [text, setText] = useState("");
  const canContinue =
    ["needs_human", "failed", "awaiting_approval"].includes(status) &&
    revision < 5;
  return (
    <section aria-label="Manual evidence review">
      <h2>Observed evidence</h2>
      <p className="muted">
        Revision {revision}. These are excerpts you supplied, not independently
        verified telemetry.
      </p>
      {observations.length ? (
        observations.map((fact, i) => (
          <blockquote key={`${fact.line_id}-${i}`}>
            <code>
              {fact.source_id} / {fact.line_id}
            </code>
            <p>{fact.quote}</p>
          </blockquote>
        ))
      ) : (
        <p>No supported failure observation has been identified yet.</p>
      )}
      {questions.length > 0 && (
        <>
          <h3>Details that would help the investigation</h3>
          <ul>
            {questions.map((q) => (
              <li key={q}>{q}</li>
            ))}
          </ul>
        </>
      )}
      {canContinue && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            void act(async () => {
              await api(`/runs/${runId}/evidence`, {
                method: "POST",
                body: JSON.stringify({ text, expected_revision: revision }),
              });
              setText("");
              setNotice(
                "Evidence added. The investigation is continuing with a new revision; any previous approval proposal is invalidated.",
              );
            });
          }}
        >
          <label htmlFor="follow-up-evidence">
            Additional observations or answers
          </label>
          <textarea
            id="follow-up-evidence"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            minLength={3}
            maxLength={6000}
            required
            disabled={busy}
            placeholder="Paste sanitized findings with timestamps, identify conflicting observations, or say which requested details are unavailable."
          />
          <p className="muted">
            No database connection or direct log-file access is required.
            Previous evidence is retained. Combined evidence limit: 12,000
            characters.
          </p>
          <button
            type="submit"
            className="primary"
            disabled={busy || text.trim().length < 3}
          >
            Add evidence and continue
          </button>
        </form>
      )}
      {revision >= 5 && (
        <p>
          Five evidence revisions reached. Export the investigation for operator
          review.
        </p>
      )}
    </section>
  );
}
