import { useCallback, useEffect, useState } from "react";
import type React from "react";
import type { Item } from "../types";
import { api, authorizationHeaders } from "../lib/api";
export function useHub() {
  const [page, setPage] = useState("Overview"),
    [theme, setTheme] = useState(localStorage.getItem("hub-theme") || "dark");
  const [dashboard, setDashboard] = useState<Item>({
      runs: [],
      tickets: [],
      evaluations: [],
    }),
    [config, setConfig] = useState<Item>({ providers: {} });
  const [samples, setSamples] = useState<Item[]>([]),
    [docs, setDocs] = useState<Item[]>([]),
    [memory, setMemory] = useState<Item[]>([]);
  const [selected, setSelected] = useState(""),
    [run, setRun] = useState<Item | null>(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false),
    [title, setTitle] = useState(""),
    [service, setService] = useState("integration-api"),
    [logs, setLogs] = useState("");
  const [docTitle, setDocTitle] = useState(""),
    [docText, setDocText] = useState(""),
    [filter, setFilter] = useState(""),
    [token, setToken] = useState("");
  const [approvalNote, setApprovalNote] = useState(""),
    [confirmAction, setConfirmAction] = useState<string | null>(null);
  const refresh = useCallback(async () => {
    try {
      const [d, c, s, k, m] = await Promise.all([
        api("/dashboard"),
        api("/config"),
        api("/samples"),
        api("/documents"),
        api("/memory"),
      ]);
      setDashboard(d);
      setConfig(c);
      setSamples(s);
      setDocs(k);
      setMemory(m);
      if (selected) setRun(await api("/runs/" + selected));
    } catch (e) {
      setError((e as Error).message);
    }
  }, [selected]);
  useEffect(() => {
    void refresh();
    const t = setInterval(() => void refresh(), 5000);
    return () => clearInterval(t);
  }, [refresh]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("hub-theme", theme);
  }, [theme]);
  const act = async (fn: () => Promise<void>) => {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  const useSample = (s: Item) => {
    setTitle(s.title);
    setService(s.service);
    setLogs(s.logs);
    setPage("Agent workspace");
  };
  const openRun = (r: Item, p = "RCA investigation") => {
    setSelected(r.id);
    setRun(r);
    setPage(p);
  };
  const start = () =>
    act(async () => {
      const r = await api("/runs", {
        method: "POST",
        body: JSON.stringify({ title, service, logs }),
      });
      setSelected(r.id);
      setRun(r);
      setPage("RCA investigation");
    });
  const approve = (approved: boolean) =>
    act(async () => {
      await api(`/runs/${selected}/approval`, {
        method: "POST",
        body: JSON.stringify({ approved, note: approvalNote }),
      });
      setConfirmAction(null);
      setNotice(
        approved
          ? "Approval recorded. Creating the local recovery ticket."
          : "Recovery ticket declined.",
      );
    });
  const exportReport = () =>
    act(async () => {
      const res = await fetch(`/api/runs/${selected}/report`, {
        headers: authorizationHeaders(),
      });
      if (!res.ok) throw new Error("Report export failed");
      const u = URL.createObjectURL(await res.blob());
      const a = document.createElement("a");
      a.href = u;
      a.download = "investigation-" + selected.slice(0, 8) + ".md";
      a.click();
      URL.revokeObjectURL(u);
    });
  const latest = dashboard.evaluations[0],
    taskMetric = latest?.metrics.task_passed;
  const running = dashboard.runs.filter(
    (r: Item) => r.status === "running",
  ).length;
  const waiting = dashboard.runs.filter(
    (r: Item) => r.status === "awaiting_approval",
  ).length;
  const finding = run?.finding?.citations ? run.finding : null;
  return {
    page,
    setPage,
    theme,
    setTheme,
    dashboard,
    setDashboard,
    config,
    setConfig,
    samples,
    setSamples,
    docs,
    setDocs,
    memory,
    setMemory,
    selected,
    setSelected,
    run,
    setRun,
    error,
    setError,
    notice,
    setNotice,
    busy,
    setBusy,
    title,
    setTitle,
    service,
    setService,
    logs,
    setLogs,
    docTitle,
    setDocTitle,
    docText,
    setDocText,
    filter,
    setFilter,
    token,
    setToken,
    approvalNote,
    setApprovalNote,
    confirmAction,
    setConfirmAction,
    refresh,
    act,
    useSample,
    openRun,
    start,
    approve,
    exportReport,
    latest,
    taskMetric,
    running,
    waiting,
    finding,
  };
}
export type HubState = ReturnType<typeof useHub>;
export type PageState = HubState & {
  runPicker: React.ReactNode;
  runList: React.ReactNode;
};
