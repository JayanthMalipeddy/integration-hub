import type { PageState } from "../hooks/useHub";
import { Badge, Empty } from "../components/common";
import type { Item } from "../types";
export function TimelinePage({
  run,
  runPicker,
}: Pick<PageState, "run" | "runPicker">) {
  return (
    <>
      {runPicker}
      <section>
        <h2>Persistent execution trace</h2>
        {run?.traces?.length ? (
          run.traces.map((t: Item) => (
            <div className="trace" key={t.id}>
              <span className="trace-dot" />
              <div>
                <div className="section-heading">
                  <h3>{t.node}</h3>
                  <small>{new Date(t.timestamp).toLocaleTimeString()}</small>
                </div>
                <p>{t.detail}</p>
                {t.provider && (
                  <Badge value={t.provider + " / " + t.model} />
                )}{" "}
                {t.latency_ms !== undefined && (
                  <small>{(t.latency_ms / 1000).toFixed(2)} s</small>
                )}
                {t.fallback && (
                  <div className="alert">Fallback: {t.fallback_reason}</div>
                )}
                <details>
                  <summary>Event details</summary>
                  <pre>{JSON.stringify(t, null, 2)}</pre>
                </details>
              </div>
            </div>
          ))
        ) : (
          <Empty text="Node events appear here during an investigation." />
        )}
      </section>
    </>
  );
}
