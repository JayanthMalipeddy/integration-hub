import { useState } from "react";
import type { HubState } from "../hooks/useHub";
import { ArrowUpRight, Search } from "lucide-react";
import { Badge, Empty } from "./common";
interface ListedRun {
  id: string;
  status: string;
  created_at: string;
  incident: { title: string; service: string };
}
export function RunList({
  dashboard,
  openRun,
}: Pick<HubState, "dashboard" | "title" | "service" | "openRun">) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const runs: ListedRun[] = dashboard.runs;
  const rows = runs.filter(
    (run) =>
      (status === "all" || run.status === status) &&
      `${run.incident.title} ${run.incident.service} ${run.id}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  return (
    <>
      <div className="table-toolbar">
        <label className="search-field">
          <Search size={17} />
          <span className="sr-only">Search investigations</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search title, service or run ID"
          />
        </label>
        <label className="status-filter">
          <span className="sr-only">Filter by status</span>
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="all">All statuses</option>
            {[...new Set(runs.map((r) => r.status))].map((s) => (
              <option key={s} value={s}>
                {s.replaceAll("_", " ")}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="table-wrap">
        <table>
          <caption className="sr-only">
            Investigations; open a title to review evidence
          </caption>
          <thead>
            <tr>
              <th scope="col">Investigation</th>
              <th scope="col">Service</th>
              <th scope="col">Status</th>
              <th scope="col">Started</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <button className="run-link" onClick={() => openRun(r)}>
                    {r.incident.title}
                    <ArrowUpRight size={14} />
                  </button>
                  <small>{r.id.slice(0, 12)}</small>
                </td>
                <td>{r.incident.service}</td>
                <td>
                  <Badge value={r.status} />
                </td>
                <td>
                  <time dateTime={r.created_at}>
                    {new Date(r.created_at).toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                    })}
                    <small>{new Date(r.created_at).toLocaleTimeString()}</small>
                  </time>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!rows.length && (
        <Empty
          text={
            runs.length
              ? "No investigations match these filters."
              : "Your first investigation will appear here."
          }
        />
      )}
      <div className="table-count" role="status">
        {rows.length} of {runs.length} investigations
      </div>
    </>
  );
}
