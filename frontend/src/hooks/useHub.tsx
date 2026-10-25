import { useCallback, useEffect, useRef, useState } from "react";
import type React from "react";
import type { Item } from "../types";
import { api, ApiError, authorizationHeaders } from "../lib/api";
export function useHub() {
  const [authenticationRequired, setAuthenticationRequired] = useState(true);
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
  const [connection, setConnection] = useState<
    "connecting" | "connected" | "stale"
  >("connecting");
  const [lastUpdated, setLastUpdated] = useState<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [connectionError, setConnectionError] = useState("");
  const refreshController = useRef<AbortController | null>(null);
  const actionPending = useRef(false);
  const refresh = useCallback(
    async (poll = false) => {
      if (poll && refreshController.current) return;
      refreshController.current?.abort();
      const controller = new AbortController();
      refreshController.current = controller;
      setRefreshing(true);
      const options = { signal: controller.signal };
      try {
        const [d, c, s, k, m, operations] = await Promise.all([
          api("/dashboard", options),
          api("/config", options),
          api("/samples", options),
          api("/documents", options),
          api("/memory", options),
          api("/operations", options),
        ]);
        const selectedRun = selected
          ? await api("/runs/" + selected, options)
          : null;
        if (controller.signal.aborted) return;
        setDashboard(d);
        setConfig({ ...c, operations });
        setAuthenticationRequired(false);
        setConnection("connected");
        setConnectionError("");
        setLastUpdated(Date.now());
        setSamples(s);
        setDocs(k);
        setMemory(m);
        if (selected) setRun(selectedRun);
      } catch (e) {
        if (controller.signal.aborted) return;
        setConnection("stale");
        if (e instanceof ApiError && e.status === 401) {
          setAuthenticationRequired(true);
          setDashboard({ runs: [], tickets: [], evaluations: [] });
          setConfig({ providers: {} });
          setDocs([]);
          setMemory([]);
          setRun(null);
        }
        setConnectionError(
          e instanceof ApiError
            ? e.message
            : "Unable to reach the workspace. Check the connection and try again.",
        );
      } finally {
        if (refreshController.current === controller) {
          refreshController.current = null;
          setRefreshing(false);
        }
      }
    },
    [selected],
  );
  useEffect(() => {
    void refresh();
    const t = setInterval(() => {
      if (!document.hidden) void refresh(true);
    }, 5000);
    const onVisible = () => {
      if (!document.hidden) void refresh(true);
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      clearInterval(t);
      refreshController.current?.abort();
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [refresh]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("hub-theme", theme);
  }, [theme]);
  const act = async (fn: () => Promise<void>) => {
    if (actionPending.current) return;
    actionPending.current = true;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
      await refresh();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setAuthenticationRequired(true);
        setDashboard({ runs: [], tickets: [], evaluations: [] });
        setConfig({ providers: {} });
        setDocs([]);
        setMemory([]);
        setRun(null);
      }
      setError((e as Error).message);
    } finally {
      actionPending.current = false;
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
        body: JSON.stringify({
          approved,
          note: approvalNote,
          review_digest: run?.review_digest,
        }),
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
      const res = await fetch(`/api/runs/${selected}/report.docx`, {
        headers: authorizationHeaders(),
      });
      if (!res.ok) throw new Error("Report export failed");
      const u = URL.createObjectURL(await res.blob());
      const a = document.createElement("a");
      a.href = u;
      a.download = "investigation-" + selected.slice(0, 8) + ".docx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      // Give the browser time to start reading the blob before releasing it.
      window.setTimeout(() => URL.revokeObjectURL(u), 1000);
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
    connectionError,
    connection,
    lastUpdated,
    refreshing,
    authenticationRequired,
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
