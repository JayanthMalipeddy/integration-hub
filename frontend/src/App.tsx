import { useHub } from "./hooks/useHub";
import { RunPicker } from "./components/RunPicker";
import { RunList } from "./components/RunList";
import { OverviewPage } from "./pages/OverviewPage";
import { WorkspacePage } from "./pages/WorkspacePage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { IncidentsPage } from "./pages/IncidentsPage";
import { InvestigationPage } from "./pages/InvestigationPage";
import { TimelinePage } from "./pages/TimelinePage";
import { EvaluationsPage } from "./pages/EvaluationsPage";
import { ProvidersPage } from "./pages/ProvidersPage";
import { MemoryPage } from "./pages/MemoryPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import {
  Activity,
  Bot,
  BookOpen,
  ChevronRight,
  ClipboardList,
  Database,
  FileText,
  GitBranch,
  Layers,
  Moon,
  Play,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Sun,
  X,
} from "lucide-react";
import { api } from "./lib/api";
const pages = [
  ["Overview", Activity],
  ["Agent workspace", Bot],
  ["Knowledge library", BookOpen],
  ["Incident analysis", Search],
  ["RCA investigation", GitBranch],
  ["Execution timeline", Layers],
  ["Analytics & evaluations", Activity],
  ["Provider configuration", Database],
  ["Memory", ClipboardList],
  ["Reports & exports", FileText],
  ["Settings", Settings],
] as const;
export function App() {
  const hub = useHub();
  const {
    page,
    setPage,
    theme,
    setTheme,
    config,
    error,
    setError,
    notice,
    busy,
    confirmAction,
    setConfirmAction,
    refresh,
    act,
    approve,
    waiting,
  } = hub;
  const view = {
    ...hub,
    runPicker: <RunPicker {...hub} />,
    runList: <RunList {...hub} />,
  };
  return (
    <div className="shell">
      <aside>
        <a className="brand" href="#" onClick={() => setPage("Overview")}>
          <span className="brand-symbol">
            <GitBranch size={24} />
          </span>
          <span>
            Integration<span className="brand-sub">HUB</span>
          </span>
        </a>
        <div className="workspace-label">
          OPERATIONS WORKSPACE <span>W3</span>
        </div>
        <nav>
          {pages.map(([label, Icon]) => (
            <button
              key={label}
              className={page === label ? "active" : ""}
              onClick={() => setPage(label)}
            >
              <Icon size={18} />
              {label}
              {label === "RCA investigation" && waiting > 0 && (
                <span className="nav-count">{waiting}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={19} />
          <div>
            Approval required<small>Recovery actions require approval</small>
          </div>
        </div>
        <button
          className="theme"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}{" "}
          {theme === "dark" ? "Light" : "Dark"} appearance
        </button>
      </aside>
      <div className="main">
        <header>
          <div className="breadcrumb">
            Workspace <ChevronRight size={14} /> <span>{page}</span>
          </div>
          <div className="header-right">
            <span className="live-dot" />
            <span>{config.profile || "Connecting"}</span>
            <button
              className="icon-button"
              aria-label="Refresh data"
              onClick={() => void refresh()}
            >
              <RefreshCw size={17} />
            </button>
            <span className="avatar">JK</span>
          </div>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <div className="eyebrow">INTEGRATION HUB</div>
              <h1>{page === "Overview" ? "Investigations" : page}</h1>
              <p>
                {page === "Overview"
                  ? "Review API errors, runbook references and proposed fixes."
                  : "Review the details and decide what to do next."}
              </p>
            </div>
            {page === "Overview" && (
              <button
                className="primary"
                onClick={() => setPage("Agent workspace")}
              >
                <Play size={16} />
                New investigation
              </button>
            )}
          </div>
          {error && (
            <div className="alert error" role="alert">
              {error}
              <button aria-label="Dismiss error" onClick={() => setError("")}>
                <X size={16} />
              </button>
            </div>
          )}
          {notice && (
            <div className="alert success" role="status">
              {notice}
            </div>
          )}
          {page === "Overview" && <OverviewPage {...view} />}
          {page === "Agent workspace" && <WorkspacePage {...view} />}
          {page === "Knowledge library" && <KnowledgePage {...view} />}
          {page === "Incident analysis" && <IncidentsPage {...view} />}
          {page === "RCA investigation" && <InvestigationPage {...view} />}
          {page === "Execution timeline" && <TimelinePage {...view} />}
          {page === "Analytics & evaluations" && <EvaluationsPage {...view} />}
          {page === "Provider configuration" && <ProvidersPage {...view} />}
          {page === "Memory" && <MemoryPage {...view} />}
          {page === "Reports & exports" && <ReportsPage {...view} />}
          {page === "Settings" && <SettingsPage {...view} />}
          <footer>
            Integration Hub <span>Logs, runbooks and recovery plans.</span>
          </footer>
        </main>
      </div>
      {confirmAction && (
        <div className="modal-backdrop">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="confirm-title"
          >
            <ShieldCheck size={30} />
            <h2 id="confirm-title">
              {confirmAction === "approve"
                ? "Approve this recovery plan?"
                : "Delete this memory?"}
            </h2>
            <p>
              {confirmAction === "approve"
                ? "This creates a local ticket and retains the hypothesis shown in this investigation. Review the evidence and uncertainty before continuing."
                : "This removes the memory record. The original investigation and audit trace remain."}
            </p>
            <div className="actions">
              <button onClick={() => setConfirmAction(null)}>Cancel</button>
              <button
                className="primary"
                disabled={busy}
                onClick={() =>
                  confirmAction === "approve"
                    ? void approve(true)
                    : void act(async () => {
                        await api("/memory/" + confirmAction.split(":")[1], {
                          method: "DELETE",
                        });
                        setConfirmAction(null);
                      })
                }
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
