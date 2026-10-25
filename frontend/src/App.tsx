import { useState } from "react";
import { AccessGate } from "./components/AccessGate";
import { ConfirmDialog } from "./components/ConfirmDialog";
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
  ChevronRight,
  GitBranch,
  Moon,
  Plus,
  RefreshCw,
  ShieldCheck,
  Sun,
  X,
  Menu,
  Radio,
} from "lucide-react";
import { api } from "./lib/api";
import { navigation } from "./lib/navigation";
export function App() {
  const hub = useHub();
  const [menuOpen, setMenuOpen] = useState(false);
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
    connection,
    lastUpdated,
    refreshing,
  } = hub;
  if (hub.authenticationRequired)
    return (
      <AccessGate error={hub.connectionError || error} refresh={refresh} />
    );
  const view = {
    ...hub,
    runPicker: <RunPicker {...hub} />,
    runList: <RunList {...hub} />,
  };
  const current =
    navigation.find((item) => item.label === page) || navigation[0];
  const navigate = (label: string) => {
    setPage(label);
    setMenuOpen(false);
  };
  return (
    <div className="shell">
      <a className="skip-link" href="#workspace-content">
        Skip to main content
      </a>
      <aside className={menuOpen ? "navigation-open" : ""}>
        <div className="brand-row">
          <a
            className="brand"
            href="#overview"
            onClick={(event) => {
              event.preventDefault();
              navigate("Overview");
            }}
          >
            <span className="brand-symbol">
              <GitBranch size={24} />
            </span>
            <span>
              Integration<span className="brand-sub">HUB / OPERATIONS</span>
            </span>
          </a>
          <button
            className="mobile-menu icon-button"
            aria-label="Toggle navigation"
            aria-expanded={menuOpen}
            aria-controls="workspace-navigation"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
        <nav id="workspace-navigation" aria-label="Main navigation">
          {["Workspace", "Intelligence", "Administration"].map((group) => (
            <div className="nav-group" key={group}>
              <span className="nav-group-label">{group}</span>
              {navigation
                .filter((item) => item.group === group)
                .map(({ label, icon: Icon }) => (
                  <button
                    key={label}
                    aria-current={page === label ? "page" : undefined}
                    className={page === label ? "active" : ""}
                    onClick={() => navigate(label)}
                  >
                    <Icon size={18} />
                    <span>{label}</span>
                    {label === "RCA investigation" && waiting > 0 && (
                      <span
                        className="nav-count"
                        aria-label={`${waiting} awaiting review`}
                      >
                        {waiting}
                      </span>
                    )}
                  </button>
                ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={20} />
          <div>
            Human-controlled recovery
            <small>Review every proposed action.</small>
          </div>
        </div>
        <button
          className="theme"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          {theme === "dark" ? "Light" : "Dark"} appearance
        </button>
      </aside>
      <div className="main">
        <header>
          <div className="breadcrumb">
            {current.group}
            <ChevronRight size={14} />
            <span>{page}</span>
          </div>
          <div className="header-right">
            <span className="profile-chip">
              <Radio size={14} />
              {String(config.profile || "Connecting").replaceAll("_", " ")}
            </span>
            <span
              className={`connection ${connection}`}
              role="status"
              title={
                lastUpdated
                  ? `Last successful sync: ${new Date(lastUpdated).toLocaleString()}`
                  : "No successful sync yet"
              }
            >
              <span className="connection-dot" />
              {connection === "connected"
                ? "Connected"
                : connection === "stale"
                  ? "Sync unavailable"
                  : "Connecting"}
            </span>
            <button
              className="icon-button"
              aria-label="Refresh data"
              disabled={refreshing}
              onClick={() => void refresh()}
            >
              <RefreshCw size={17} className={refreshing ? "spin" : ""} />
            </button>
          </div>
        </header>
        <main id="workspace-content" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <div className="eyebrow">{current.group}</div>
              <h1>{current.title}</h1>
              <p>{current.description}</p>
            </div>
            {page === "Overview" && (
              <button
                className="primary"
                onClick={() => navigate("Agent workspace")}
              >
                <Plus size={18} />
                New investigation
              </button>
            )}
          </div>
          {error && (
            <div className="alert error" role="alert">
              <span>{error}</span>
              <button aria-label="Dismiss error" onClick={() => setError("")}>
                <X size={18} />
              </button>
            </div>
          )}
          {connection === "stale" && (
            <div className="alert" role="status">
              Showing previously loaded data.{" "}
              {lastUpdated &&
                `Last synced ${new Date(lastUpdated).toLocaleTimeString()}.`}{" "}
              Reconnecting automatically.
              <button onClick={() => void refresh()}>Retry now</button>
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
            <span>Integration Hub</span>
            <span>Evidence first. Human decision. Traceable outcome.</span>
          </footer>
        </main>
      </div>
      {confirmAction && (
        <ConfirmDialog
          title={
            confirmAction === "approve"
              ? "Approve this recovery plan?"
              : "Delete this memory?"
          }
          busy={busy}
          onClose={() => setConfirmAction(null)}
          onConfirm={() =>
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
          <p>
            {confirmAction === "approve"
              ? "This creates a local ticket and retains the hypothesis shown in this investigation. It does not change an external system. Review the evidence and uncertainty before continuing."
              : "This removes the memory record. The original investigation and audit trace remain."}
          </p>
          {confirmAction === "approve" && hub.finding && (
            <div className="decision-preview">
              <strong>{hub.run?.incident.title}</strong>
              <p>{hub.finding.hypothesis}</p>
              <small>
                {hub.finding.citations.length} cited passages · Review the
                proposed recovery steps in the investigation.
              </small>
            </div>
          )}
        </ConfirmDialog>
      )}
    </div>
  );
}
