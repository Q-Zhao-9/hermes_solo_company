"use client";

import { FormEvent, useMemo, useState } from "react";

const examples = [
  "https://www.easiio.com/",
  "https://example.com/",
  "http://localhost:3000/",
];

export default function HomePage() {
  const [input, setInput] = useState(examples[0]);
  const [activeUrl, setActiveUrl] = useState(examples[0]);
  const [generatedTitle, setGeneratedTitle] = useState("Generated Sitelet Page");
  const [generatedHtml, setGeneratedHtml] = useState(sampleGeneratedHtml);
  const [generatorStatus, setGeneratorStatus] = useState("");

  const previewUrl = useMemo(() => {
    return `/sitelet?url=${encodeURIComponent(activeUrl)}`;
  }, [activeUrl]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setActiveUrl(input.trim());
  }

  async function createGeneratedPage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setGeneratorStatus("Creating generated page...");

    const response = await fetch("/api/generated", {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        title: generatedTitle,
        html: generatedHtml,
        source: "sitelet-ui",
      }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setGeneratorStatus(payload.error || "Could not create generated page.");
      return;
    }

    setInput(payload.generatedUrl);
    setActiveUrl(payload.generatedUrl);
    setGeneratorStatus(`Generated page ready: ${payload.id}`);
  }

  return (
    <main className="sitelet-app">
      <aside className="sitelet-sidebar">
        <div>
          <p className="eyebrow">Hermes Website Preview</p>
          <h1>Sitelet</h1>
          <p className="lede">
            Render a remote or local website through this Next.js server, keep
            links and forms usable, and capture the result for Discord review.
          </p>
          <div className="nav-actions">
            <a href="/dashboard">Token Dashboard</a>
            <a href="/login">Sign In</a>
          </div>
        </div>

        <form className="url-form" onSubmit={submit}>
          <label htmlFor="target-url">Target URL</label>
          <input
            id="target-url"
            type="url"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="https://www.example.com/"
            required
          />
          <button type="submit">Preview Site</button>
        </form>

        <div className="examples">
          <span>Examples</span>
          {examples.map((url) => (
            <button
              key={url}
              type="button"
              onClick={() => {
                setInput(url);
                setActiveUrl(url);
              }}
            >
              {url}
            </button>
          ))}
        </div>

        <div className="notes">
          <h2>Workflow</h2>
          <ol>
            <li>Open a target page.</li>
            <li>Navigate or submit forms inside the preview.</li>
            <li>Ask Hermes to screenshot this page for Discord.</li>
          </ol>
        </div>

        <form className="generator-form" onSubmit={createGeneratedPage}>
          <div>
            <h2>Generated Page</h2>
            <p>
              Paste generated HTML here after signing in. Hermes can also post
              generated pages to this same endpoint with a bearer token.
            </p>
          </div>
          <label htmlFor="generated-title">Title</label>
          <input
            id="generated-title"
            value={generatedTitle}
            onChange={(event) => setGeneratedTitle(event.target.value)}
          />
          <label htmlFor="generated-html">HTML</label>
          <textarea
            id="generated-html"
            value={generatedHtml}
            onChange={(event) => setGeneratedHtml(event.target.value)}
            rows={10}
          />
          <button type="submit">Create Sitelet Preview</button>
          {generatorStatus ? <p className="generator-status">{generatorStatus}</p> : null}
        </form>
      </aside>

      <section className="sitelet-preview" aria-label="Website preview">
        <header className="preview-toolbar">
          <div>
            <span>Previewing</span>
            <strong>{activeUrl}</strong>
          </div>
          <a href={previewUrl} target="_blank" rel="noreferrer">
            Open proxied page
          </a>
        </header>
        <iframe title="Sitelet preview" src={previewUrl} />
      </section>
    </main>
  );
}

const sampleGeneratedHtml = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Generated Landing Page</title>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f6f8fb; }
    main { min-height: 100vh; display: grid; place-items: center; padding: 48px; }
    section { width: min(920px, 100%); padding: 48px; border-radius: 18px; background: #fff; box-shadow: 0 20px 60px rgba(23,32,51,.12); }
    h1 { margin: 0 0 16px; font-size: clamp(36px, 6vw, 72px); line-height: 1; }
    p { max-width: 620px; color: #5d6b82; font-size: 18px; line-height: 1.6; }
    form { display: flex; gap: 10px; margin-top: 28px; flex-wrap: wrap; }
    input { flex: 1 1 260px; padding: 13px; border: 1px solid #d9e0ea; border-radius: 8px; }
    button { padding: 13px 18px; border: 0; border-radius: 8px; color: #fff; background: #16756f; font-weight: 700; }
  </style>
</head>
<body>
  <main>
    <section>
      <h1>Generated page preview</h1>
      <p>This page is stored by Sitelet and rendered through the preview server so Hermes can capture it for Discord.</p>
      <form action="/thanks" method="post">
        <input name="email" type="email" placeholder="Email address">
        <button type="submit">Test form</button>
      </form>
    </section>
  </main>
</body>
</html>`;
