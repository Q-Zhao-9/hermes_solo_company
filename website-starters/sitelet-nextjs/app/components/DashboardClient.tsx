"use client";

import { FormEvent, useEffect, useState } from "react";

type TokenRecord = {
  id: string;
  name: string;
  prefix: string;
  createdAt: string;
  lastUsedAt: string | null;
};

type GeneratedPageRecord = {
  id: string;
  title: string;
  source: string;
  createdAt: string;
  generatedUrl: string;
  siteletUrl: string;
  storageFile: string;
  htmlBytes: number;
};

export function DashboardClient({
  email,
  siteletBaseUrl,
  configuredApiToken,
}: {
  email: string;
  siteletBaseUrl: string;
  configuredApiToken: string;
}) {
  const [tokens, setTokens] = useState<TokenRecord[]>([]);
  const [tokenName, setTokenName] = useState("Hermes Discord Bot");
  const [newToken, setNewToken] = useState("");
  const [status, setStatus] = useState("");
  const [history, setHistory] = useState<GeneratedPageRecord[]>([]);
  const [historyStatus, setHistoryStatus] = useState("");

  useEffect(() => {
    void refreshTokens();
    void refreshHistory();
  }, []);

  async function refreshTokens() {
    const response = await fetch("/api/tokens");
    const payload = await response.json();
    if (payload.ok) {
      setTokens(payload.tokens);
    }
  }

  async function refreshHistory() {
    setHistoryStatus("Loading history...");
    const response = await fetch("/api/generated/history");
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setHistoryStatus(payload.error || "Could not load generated page history.");
      return;
    }
    setHistory(payload.pages);
    setHistoryStatus("");
  }

  async function createToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("Creating token...");
    const response = await fetch("/api/tokens", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: tokenName }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setStatus(payload.error || "Could not create token.");
      return;
    }
    setNewToken(payload.token);
    setStatus("Token created. Copy it now; it will not be shown again.");
    await refreshTokens();
  }

  async function revokeToken(id: string) {
    setStatus("Revoking token...");
    const response = await fetch(`/api/tokens/${id}`, { method: "DELETE" });
    const payload = await response.json();
    setStatus(payload.ok ? "Token revoked." : payload.error || "Could not revoke token.");
    await refreshTokens();
  }

  async function signOut() {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/login";
  }

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Sitelet Cloud</p>
          <h1>Preview token dashboard</h1>
          <p className="lede">
            Signed in as {email}. Use an API token from this page in Hermes so
            it can upload generated HTML and return Sitelet preview URLs.
          </p>
        </div>
        <button type="button" className="secondary-button" onClick={signOut}>
          Sign Out
        </button>
      </header>

      <section className="dashboard-grid">
        <div className="dashboard-section">
          <h2>Create Hermes token</h2>
          <form className="auth-form" onSubmit={createToken}>
            <label htmlFor="token-name">Token name</label>
            <input
              id="token-name"
              value={tokenName}
              onChange={(event) => setTokenName(event.target.value)}
              required
            />
            <button type="submit">Create Token</button>
          </form>
          {status ? <p className="form-status">{status}</p> : null}
          {newToken ? (
            <div className="token-secret">
              <span>New token</span>
              <code>{newToken}</code>
            </div>
          ) : null}
        </div>

        <div className="dashboard-section">
          <h2>Hermes setup</h2>
          <p>
            Configure Hermes with this service URL and token, then ask the bot
            to use Sitelet when it generates or modifies a page.
          </p>
          <pre>{`SITELET_BASE_URL=${siteletBaseUrl}
SITELET_API_TOKEN=${newToken || configuredApiToken || "stlt_your_token_here"}`}</pre>
          <p>
            Upload endpoint: <code>/api/generated</code>. The response includes
            <code> generatedUrl </code> and <code> siteletUrl </code>.
          </p>
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-title-row">
          <div>
            <h2>WordPress editing plugin</h2>
            <p>
              Install this plugin on a WordPress site to expose the controlled
              Hermes MCP endpoint used by the WordPress editing skill.
            </p>
          </div>
          <a
            className="download-button"
            href="/downloads/hermes-mcp-wordpress-plugin.zip"
            download
          >
            Download Plugin
          </a>
        </div>
        <p>
          After activation, open <strong>Settings -&gt; Hermes MCP</strong> in
          WordPress, generate an API key, enable the endpoint, and add the
          endpoint URL plus bearer token to Hermes.
        </p>
      </section>

      <section className="dashboard-section">
        <h2>Active tokens</h2>
        <div className="token-list">
          {tokens.length === 0 ? <p>No tokens yet.</p> : null}
          {tokens.map((token) => (
            <div className="token-row" key={token.id}>
              <div>
                <strong>{token.name}</strong>
                <span>
                  {token.prefix}... created {new Date(token.createdAt).toLocaleString()}
                  {token.lastUsedAt
                    ? `, last used ${new Date(token.lastUsedAt).toLocaleString()}`
                    : ""}
                </span>
              </div>
              <button type="button" className="danger-button" onClick={() => revokeToken(token.id)}>
                Revoke
              </button>
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-title-row">
          <div>
            <h2>Sitelet history</h2>
            <p>
              Pages uploaded by Hermes are stored here so you can reopen the
              preview URL or inspect the backing file later.
            </p>
          </div>
          <button type="button" className="secondary-button" onClick={refreshHistory}>
            Refresh
          </button>
        </div>
        {historyStatus ? <p className="form-status">{historyStatus}</p> : null}
        <div className="history-list">
          {history.length === 0 && !historyStatus ? <p>No generated pages yet.</p> : null}
          {history.map((page) => (
            <article className="history-row" key={page.id}>
              <div className="history-main">
                <strong>{page.title}</strong>
                <span>
                  {page.source} · {new Date(page.createdAt).toLocaleString()} · {formatBytes(page.htmlBytes)}
                </span>
                <code>{page.storageFile}</code>
              </div>
              <div className="history-actions">
                <a href={page.siteletUrl} target="_blank" rel="noreferrer">
                  Preview
                </a>
                <a href={page.generatedUrl} target="_blank" rel="noreferrer">
                  HTML
                </a>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}
