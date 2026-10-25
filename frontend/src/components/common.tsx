import { Layers, type LucideIcon } from "lucide-react";
export function Badge({ value }: { value: string }) {
  return <span className={"badge " + value}>{value.replaceAll("_", " ")}</span>;
}
export function Empty({ text }: { text: string }) {
  return (
    <div className="empty">
      <Layers size={30} />
      <p>{text}</p>
    </div>
  );
}
export function Stat({
  label,
  value,
  detail,
  icon: Icon,
}: {
  icon?: LucideIcon;
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <div className="stat">
      <span className="stat-label">
        {label}
        {Icon && <Icon size={18} aria-hidden="true" />}
      </span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}
