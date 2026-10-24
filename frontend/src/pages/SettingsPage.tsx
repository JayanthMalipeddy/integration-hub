import type { PageState } from "../hooks/useHub";
import { setAccessToken } from "../lib/api";
export function SettingsPage({
  theme,
  setTheme,
  setError,
  token,
  setToken,
  refresh,
}: Pick<
  PageState,
  "theme" | "setTheme" | "setError" | "token" | "setToken" | "refresh"
>) {
  return (
    <div className="two-columns">
      <section>
        <h2>Connection</h2>
        <p>
          Single-user, local development mode. If the backend has API_TOKEN
          configured, enter it here for this browser session.
        </p>
        <label>
          API access token
          <input
            type="password"
            autoComplete="off"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
        </label>
        <button
          onClick={() => {
            setAccessToken(token);
            setToken("");
            setError("");
            void refresh();
          }}
        >
          Connect
        </button>
        <h3>Appearance</h3>
        <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
          Switch to {theme === "dark" ? "light" : "dark"} theme
        </button>
      </section>
      <section>
        <h2>About this build</h2>
        <p>Week 3 · Integration Hub</p>
        <p>
          React + TypeScript · FastAPI · LangGraph · Ollama · Chroma · SQLite
        </p>
        <p>
          Investigations run locally. Approval creates a local ticket; it does
          not change an external system.
        </p>
        <p className="muted">
          Synthetic examples support demonstration and evaluation. Production
          readiness requires organization-specific authentication, retention,
          and operational review.
        </p>
      </section>
    </div>
  );
}
