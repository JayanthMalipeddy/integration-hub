import type { HubState } from "../hooks/useHub";
import { ChevronRight } from "lucide-react";
import { Badge, Empty } from "../components/common";
import type { Item } from "../types";
export function RunList({
  dashboard,
  openRun,
}: Pick<HubState, "dashboard" | "title" | "service" | "openRun">) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Investigation</th>
            <th>Service</th>
            <th>Status</th>
            <th>Started</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {dashboard.runs.map((r: Item) => (
            <tr
              key={r.id}
              onClick={() => openRun(r)}
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && openRun(r)}
            >
              <td>
                <strong>{r.incident.title}</strong>
                <small>{r.id.slice(0, 12)}</small>
              </td>
              <td>{r.incident.service}</td>
              <td>
                <Badge value={r.status} />
              </td>
              <td>{new Date(r.created_at).toLocaleTimeString()}</td>
              <td>
                <ChevronRight size={16} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!dashboard.runs.length && (
        <Empty text="Your first investigation will appear here." />
      )}
    </div>
  );
}
