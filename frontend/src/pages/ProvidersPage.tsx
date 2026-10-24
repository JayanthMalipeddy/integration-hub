import type { PageState } from "../hooks/useHub";
import { Database } from "lucide-react";
import { Badge } from "../components/common";
import type { Item } from "../types";
export function ProvidersPage({ config }: Pick<PageState, "config">) {
  return (
    <>
      <section>
        <div className="section-heading">
          <h2>Active environment</h2>
          <Badge value={config.profile || "loading"} />
        </div>
        <p>
          Choose local_free, hybrid or sponsored using AI_PROFILE in the project
          .env file. Restart the backend to apply changes. Credentials stay on
          the server.
        </p>
        <div className="provider-grid">
          {Object.entries(config.providers).map(([name, p]) => (
            <div className="provider-card" key={name}>
              <Database size={20} />
              <h3>{name.replaceAll("_", " ")}</h3>
              <p>{(p as Item).provider}</p>
              {(p as Item).endpoint && (
                <p style={{ overflowWrap: "anywhere" }}>
                  {(p as Item).mode}: {(p as Item).endpoint}
                </p>
              )}
              {(p as Item).collection && (
                <p style={{ overflowWrap: "anywhere" }}>
                  Collection: {(p as Item).collection}
                </p>
              )}
              <Badge value={(p as Item).status} />
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2>Provider options</h2>
        <table>
          <thead>
            <tr>
              <th>AI_PROFILE</th>
              <th>Model</th>
              <th>Setup</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>local_free</td>
              <td>Ollama</td>
              <td>No paid API calls</td>
            </tr>
            <tr>
              <td>hybrid</td>
              <td>OpenRouter :free</td>
              <td>API key and cloud data consent</td>
            </tr>
            <tr>
              <td>sponsored</td>
              <td>Nebius</td>
              <td>API key, paid/data consent and a configured budget</td>
            </tr>
          </tbody>
        </table>
        <p>
          Set VECTOR_STORE=chroma to keep your local Chroma server with any
          profile. Use VECTOR_STORE=auto for the profile default, or pinecone
          with sponsored for cloud vectors. These settings take effect after
          restarting the backend.
        </p>
      </section>
      <section>
        <h2>Consent and limits</h2>
        <dl>
          <dt>Cloud data consent</dt>
          <dd>{config.cloud_data_consent ? "Enabled" : "Disabled"}</dd>
          <dt>Paid inference</dt>
          <dd>{config.paid_enabled ? "Enabled" : "Disabled"}</dd>
          <dt>Configured spend cap</dt>
          <dd>${config.max_cost_usd || 0}</dd>
          <dt>Local fallback</dt>
          <dd>{config.local_fallback ? "Explicitly enabled" : "Disabled"}</dd>
          <dt>Step / token limit</dt>
          <dd>
            {config.max_steps} / {config.max_tokens}
          </dd>
        </dl>
      </section>
    </>
  );
}
