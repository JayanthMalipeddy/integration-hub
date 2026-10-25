import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./style.css";
import "./enterprise.css";
import { ErrorBoundary } from "./components/ErrorBoundary";
createRoot(document.getElementById("root")!).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>,
);
