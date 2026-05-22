"""Tiny internal web UI for the prototype API.

This is not the final product UI. It is a developer/tester surface that makes
it possible to paste JSON and generate a report without writing curl commands.
"""

from __future__ import annotations

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Constellation Prototype</title>
  <style>
    :root { font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f1f1f; background: #f7f3ed; }
    body { margin: 0; padding: 32px; }
    main { max-width: 1100px; margin: 0 auto; display: grid; gap: 24px; }
    h1 { margin-bottom: 0; font-size: 2rem; }
    p { line-height: 1.5; }
    textarea { width: 100%; min-height: 420px; padding: 16px; border: 1px solid #d7d0c7; border-radius: 14px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; box-sizing: border-box; background: #fffdf9; }
    button { border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 700; cursor: pointer; background: #1f1f1f; color: white; }
    pre { white-space: pre-wrap; background: #fffdf9; border: 1px solid #d7d0c7; border-radius: 14px; padding: 18px; min-height: 240px; overflow: auto; }
    .grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 24px; }
    .card { background: #fff8ef; border: 1px solid #e3d8cb; border-radius: 22px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
    .muted { color: #666; }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } body { padding: 18px; } }
  </style>
</head>
<body>
<main>
  <section class="card">
    <h1>Constellation Prototype</h1>
    <p class="muted">Paste a relationship request JSON, then generate a draft Relationship Field Map. Coordinates and timezone are still required directly until geocoding is added.</p>
  </section>
  <section class="grid">
    <div class="card">
      <h2>Request JSON</h2>
      <textarea id="request"></textarea>
      <p><button id="generate">Generate Report</button></p>
    </div>
    <div class="card">
      <h2>Markdown Report</h2>
      <pre id="output">Waiting for input…</pre>
    </div>
  </section>
</main>
<script>
const example = {
  person_a: {
    name: "Person A",
    date: "1992-01-03",
    time: "17:37",
    time_known: true,
    latitude: 29.4252,
    longitude: -98.4946,
    timezone: "America/Chicago"
  },
  person_b: {
    name: "Person B",
    date: "1990-07-15",
    time: "09:15",
    time_known: true,
    latitude: 40.7128,
    longitude: -74.0060,
    timezone: "America/New_York"
  },
  house_system: "whole_sign",
  context: {
    relationship_type: "romantic",
    status: "current",
    user_question: "What is the dynamic between us?",
    origin_story: "We met unexpectedly and the connection felt vivid from the beginning.",
    known_themes: ["attraction", "communication", "timing"]
  }
};

document.getElementById("request").value = JSON.stringify(example, null, 2);

document.getElementById("generate").addEventListener("click", async () => {
  const output = document.getElementById("output");
  output.textContent = "Generating…";
  try {
    const payload = JSON.parse(document.getElementById("request").value);
    const response = await fetch("/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) {
      output.textContent = JSON.stringify(data, null, 2);
      return;
    }
    output.textContent = data.markdown;
  } catch (error) {
    output.textContent = String(error);
  }
});
</script>
</body>
</html>
"""
