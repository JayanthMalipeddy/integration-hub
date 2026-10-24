import type { PageState } from "../hooks/useHub";
import { Badge, Empty } from "../components/common";
export function MemoryPage({
  memory,
  setConfirmAction,
}: Pick<PageState, "memory" | "title" | "setConfirmAction">) {
  return (
    <section>
      <h2>Reviewed incident memory</h2>
      <p>
        Only approved investigations enter memory. These remain hypotheses, not
        verified production facts.
      </p>
      {memory.length ? (
        memory.map((m) => (
          <article className="memory-card" key={m.id}>
            <h3>{m.title}</h3>
            <p>{m.text}</p>
            <Badge value={m.kind} />
            <button onClick={() => setConfirmAction("forget:" + m.id)}>
              Forget this memory
            </button>
          </article>
        ))
      ) : (
        <Empty text="Approve a recovery ticket to retain the reviewed hypothesis." />
      )}
    </section>
  );
}
