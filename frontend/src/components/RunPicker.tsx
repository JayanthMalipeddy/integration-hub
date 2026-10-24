import type { HubState } from "../hooks/useHub";
import type { Item } from "../types";
export function RunPicker({
  dashboard,
  selected,
  setSelected,
  setRun,
}: Pick<
  HubState,
  "dashboard" | "selected" | "setSelected" | "setRun" | "title"
>) {
  return (
    <label className="run-picker">
      Investigation
      <select
        value={selected}
        onChange={(e) => {
          setSelected(e.target.value);
          setRun(null);
        }}
      >
        <option value="">Select an investigation</option>
        {dashboard.runs.map((r: Item) => (
          <option key={r.id} value={r.id}>
            {r.incident.title} · {r.id.slice(0, 6)}
          </option>
        ))}
      </select>
    </label>
  );
}
