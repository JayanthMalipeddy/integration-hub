import type { PageState } from "../hooks/useHub";
import { FileText } from "lucide-react";
import { Badge, Empty } from "../components/common";
import type { Item } from "../types";
export function ReportsPage({
  dashboard,
  selected,
  busy,
  exportReport,
  runPicker,
}: Pick<
  PageState,
  "dashboard" | "selected" | "busy" | "title" | "exportReport" | "runPicker"
>) {
  return (
    <>
      {runPicker}
      <section>
        <h2>Portable investigation report</h2>
        <p>
          Export the hypothesis, supporting quotations, uncertainties, recovery
          plan, and actual provider provenance as a Word document (.docx).
        </p>
        <button
          className="primary"
          disabled={!selected || busy}
          onClick={exportReport}
        >
          <FileText size={17} />
          Download selected report
        </button>
      </section>
      <section>
        <h2>Recovery tickets</h2>
        {dashboard.tickets.length ? (
          dashboard.tickets.map((t: Item) => (
            <details key={t.id}>
              <summary>
                {t.id} · {t.title}
                <Badge value={t.status} />
              </summary>
              <ol>
                {t.plan.map((x: string, i: number) => (
                  <li key={i}>{x}</li>
                ))}
              </ol>
            </details>
          ))
        ) : (
          <Empty text="No local recovery tickets have been approved." />
        )}
      </section>
    </>
  );
}
