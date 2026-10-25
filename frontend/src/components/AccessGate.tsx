import { useState } from "react";
import { GitBranch, ArrowRight, ShieldCheck } from "lucide-react";
import { setAccessToken } from "../lib/api";

export function AccessGate({
  error,
  refresh,
}: {
  error: string;
  refresh: () => Promise<void>;
}) {
  const [token, setToken] = useState("");
  const [connecting, setConnecting] = useState(false);
  return (
    <main className="access-gate">
      <section>
        <span className="access-logo">
          <GitBranch size={30} />
        </span>
        <div className="eyebrow">INTEGRATION HUB</div>
        <h1>Your operations workspace.</h1>
        <p>
          Enter your access token to open the workspace. It stays in memory for
          this browser tab.
        </p>
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            setConnecting(true);
            setAccessToken(token);
            setToken("");
            try {
              await refresh();
            } finally {
              setConnecting(false);
            }
          }}
        >
          <label htmlFor="access-token">Access token</label>
          <input
            id="access-token"
            type="password"
            autoComplete="off"
            required
            value={token}
            onChange={(event) => setToken(event.target.value)}
          />
          <button className="primary" type="submit" disabled={connecting}>
            {connecting ? "Connecting…" : "Connect to workspace"}
            <ArrowRight size={17} />
          </button>
        </form>
        {error && <p role="alert">{error}</p>}
        <div className="access-assurance">
          <ShieldCheck size={16} />
          Human approval before recovery writes
        </div>
        <p className="muted">
          For this local workspace, use API_TOKEN from your project's private
          .env file.
        </p>
      </section>
    </main>
  );
}
