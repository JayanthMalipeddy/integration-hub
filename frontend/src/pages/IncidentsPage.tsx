import type { PageState } from "../hooks/useHub";

export function IncidentsPage({
  run,
  runPicker,
  runList,
}: Pick<PageState, "run" | "logs" | "runPicker" | "runList">) {
  return (
    <>
      <section>{runList}</section>
      {runPicker}
      {run && (
        <section>
          <h2>Parsed signals</h2>
          <pre>{JSON.stringify(run.signals || {}, null, 2)}</pre>
          <h3>Original sanitized log evidence</h3>
          <pre>{run.incident.logs}</pre>
        </section>
      )}
    </>
  );
}
