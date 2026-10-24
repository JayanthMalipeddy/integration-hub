import type { PageState } from "../hooks/useHub";
import { BookOpen, RefreshCw } from "lucide-react";
import { Badge } from "../components/common";
import { api } from "../lib/api";
export function KnowledgePage({
  config,
  docs,
  setNotice,
  busy,
  docTitle,
  setDocTitle,
  docText,
  setDocText,
  filter,
  setFilter,
  act,
}: Pick<
  PageState,
  | "config"
  | "docs"
  | "setNotice"
  | "busy"
  | "title"
  | "docTitle"
  | "setDocTitle"
  | "docText"
  | "setDocText"
  | "filter"
  | "setFilter"
  | "act"
>) {
  return (
    <>
      <div className="two-columns">
        <section>
          <h2>Canonical knowledge</h2>
          <p>
            TXT, Markdown or JSON · UTF-8 · maximum 50 KB. Embedding indexes
            rebuild from these records.
          </p>
          <input
            aria-label="Search documents"
            placeholder="Filter documents…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          {docs
            .filter((d) =>
              (d.title + d.text).toLowerCase().includes(filter.toLowerCase()),
            )
            .map((d) => (
              <details key={d.id}>
                <summary>
                  <BookOpen size={17} />
                  {d.title}
                  <Badge value={d.synthetic ? "synthetic" : d.kind} />
                </summary>
                <p className="prewrap">{d.text}</p>
                <small>Source ID: {d.id}</small>
              </details>
            ))}
          <button
            disabled={busy}
            onClick={() =>
              void act(async () => {
                const r = await api("/index/rebuild", { method: "POST" });
                setNotice(
                  `${r.chunks} chunks indexed with ${config.embedding_model}.`,
                );
              })
            }
          >
            <RefreshCw size={16} />
            Rebuild local index
          </button>
        </section>
        <section>
          <h2>Add knowledge</h2>
          <label>
            Document title
            <input
              value={docTitle}
              onChange={(e) => setDocTitle(e.target.value)}
            />
          </label>
          <label>
            Runbook or meeting export
            <textarea
              rows={9}
              value={docText}
              onChange={(e) => setDocText(e.target.value)}
              maxLength={50000}
            />
          </label>
          <button
            className="primary"
            disabled={busy || docTitle.length < 3 || docText.length < 20}
            onClick={() =>
              void act(async () => {
                await api("/documents", {
                  method: "POST",
                  body: JSON.stringify({ title: docTitle, text: docText }),
                });
                setDocText("");
                setDocTitle("");
                setNotice(
                  "Document saved. Index will refresh on the next search.",
                );
              })
            }
          >
            Save document
          </button>
          <label className="upload">
            Upload document
            <input
              type="file"
              accept=".txt,.md,.json"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f)
                  void act(async () => {
                    const b = new FormData();
                    b.append("file", f);
                    await api("/documents/upload", { method: "POST", body: b });
                    setNotice("Document uploaded.");
                  });
              }}
            />
          </label>
        </section>
      </div>
    </>
  );
}
