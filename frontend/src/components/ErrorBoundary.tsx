import { Component, type ReactNode } from "react";
import { RefreshCw } from "lucide-react";
export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed)
      return (
        <main className="access-gate">
          <section role="alert">
            <span className="eyebrow">WORKSPACE UNAVAILABLE</span>
            <h1>This view could not load.</h1>
            <p>
              Reload the workspace to reconnect. Saved investigations remain on
              the server. You will need your access token again.
            </p>
            <button
              className="primary"
              onClick={() => window.location.reload()}
            >
              <RefreshCw size={16} />
              Reload workspace
            </button>
          </section>
        </main>
      );
    return this.props.children;
  }
}
