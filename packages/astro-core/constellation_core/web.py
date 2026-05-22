"""Internal web UI for the Constellation prototype.

This is still not the final product UI, but it is now a usable browser-first
surface for entering two birth records and generating a Relationship Field Map.
"""

from __future__ import annotations

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Constellation Prototype</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f1e8;
      --panel: #fffaf2;
      --panel-strong: #fff5e7;
      --ink: #211f1b;
      --muted: #6f685f;
      --line: #e4d8c8;
      --button: #211f1b;
      --button-text: #fffaf2;
      --soft: #f0e3d1;
      --accent: #7c6b54;
      --error: #7f1d1d;
      --error-bg: #fee2e2;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.9), transparent 30rem),
        var(--bg);
      color: var(--ink);
    }

    main { width: min(1180px, 100%); margin: 0 auto; padding: 28px; display: grid; gap: 22px; }

    header {
      display: grid; gap: 10px; padding: 28px; border: 1px solid var(--line); border-radius: 28px;
      background: linear-gradient(135deg, #fffaf2, #f7ead8); box-shadow: 0 18px 50px rgba(43, 33, 21, 0.08);
    }

    h1, h2, h3 { margin: 0; line-height: 1.08; }
    h1 { font-size: clamp(2rem, 6vw, 4.25rem); letter-spacing: -0.05em; }
    h2 { font-size: 1.15rem; letter-spacing: -0.02em; }
    h3 { font-size: 0.96rem; color: var(--muted); }
    p { line-height: 1.55; margin: 0; }
    .eyebrow { text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.73rem; font-weight: 800; color: var(--muted); }
    .muted { color: var(--muted); }

    .grid { display: grid; grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr); gap: 22px; align-items: start; }
    .card { background: var(--panel); border: 1px solid var(--line); border-radius: 24px; padding: 20px; box-shadow: 0 10px 30px rgba(43, 33, 21, 0.05); }
    .stack { display: grid; gap: 16px; }
    .tight { display: grid; gap: 10px; }
    .person-grid, .context-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }

    label { display: grid; gap: 6px; color: var(--muted); font-size: 0.78rem; font-weight: 750; }
    input, select, textarea {
      width: 100%; border: 1px solid var(--line); border-radius: 14px; background: #fffdf8; color: var(--ink);
      padding: 11px 12px; font: inherit; font-size: 0.95rem; outline: none;
    }
    input:focus, select:focus, textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(124, 107, 84, 0.15); }
    textarea { min-height: 92px; resize: vertical; }
    input:disabled { opacity: 0.64; background: #f8f1e7; }

    .actions { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
    button { border: 0; border-radius: 999px; padding: 12px 17px; font-weight: 850; cursor: pointer; background: var(--button); color: var(--button-text); box-shadow: 0 10px 18px rgba(33, 31, 27, 0.12); }
    button.secondary { background: var(--soft); color: var(--ink); box-shadow: none; }
    button:disabled { opacity: 0.55; cursor: wait; }

    .tabs { display: flex; gap: 8px; flex-wrap: wrap; padding: 5px; background: var(--soft); border-radius: 999px; width: fit-content; }
    .tab { background: transparent; color: var(--muted); box-shadow: none; padding: 9px 13px; }
    .tab.active { background: var(--panel); color: var(--ink); }

    pre { white-space: pre-wrap; word-break: break-word; background: #fffdf8; border: 1px solid var(--line); border-radius: 18px; padding: 18px; min-height: 520px; overflow: auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.86rem; line-height: 1.55; }
    .output-html { background: #fffdf8; border: 1px solid var(--line); border-radius: 18px; padding: 20px; min-height: 520px; overflow: auto; line-height: 1.56; }
    .output-html h1 { font-size: 2rem; letter-spacing: -0.03em; margin: 0 0 18px; }
    .output-html h2 { margin: 24px 0 10px; font-size: 1.18rem; }
    .output-html h3 { margin: 18px 0 8px; font-size: 1rem; color: var(--ink); }
    .output-html ul { padding-left: 1.15rem; }
    .output-html li { margin: 0.35rem 0; }

    .status { min-height: 22px; font-size: 0.9rem; color: var(--muted); }
    .error { background: var(--error-bg); color: var(--error); border: 1px solid rgba(127, 29, 29, 0.25); border-radius: 14px; padding: 12px; }
    .small-note { font-size: 0.82rem; color: var(--muted); }
    .hint { font-size: 0.78rem; color: var(--muted); line-height: 1.35; }
    .hidden { display: none; }
    .divider { height: 1px; background: var(--line); margin: 3px 0; }

    @media (max-width: 960px) {
      main { padding: 16px; }
      header { padding: 22px; border-radius: 24px; }
      .grid { grid-template-columns: 1fr; }
      .person-grid, .context-grid { grid-template-columns: 1fr; }
      pre, .output-html { min-height: 360px; }
      .tabs { width: 100%; }
      .tab { flex: 1; }
      .actions button { flex: 1; }
    }
  </style>
</head>
<body>
<main>
  <header>
    <div class="eyebrow">Constellation Prototype</div>
    <h1>Relationship Field Map</h1>
    <p class="muted">Enter two birth records, choose the relationship context, and generate a draft map. Place search is not implemented yet, but common place presets can fill coordinates and timezone.</p>
  </header>

  <section class="grid">
    <form id="relationship-form" class="card stack">
      <div class="tight">
        <h2>Person A</h2>
        <div class="person-grid">
          <label>Name<input name="a_name" value="Person A" required /></label>
          <label>Date<input name="a_date" type="date" value="1992-01-03" required /></label>
          <label>Time<input name="a_time" type="time" value="17:37" /></label>
          <label>Time known?
            <select name="a_time_known"><option value="true" selected>Yes</option><option value="false">No</option></select>
          </label>
          <label>Place preset<select name="a_place_preset"><option value="">Manual coordinates</option></select></label>
          <label>Timezone<input name="a_timezone" value="America/Chicago" required /></label>
          <label>Latitude<input name="a_latitude" type="number" step="0.0001" value="29.4252" required /></label>
          <label>Longitude<input name="a_longitude" type="number" step="0.0001" value="-98.4946" required /></label>
        </div>
        <p class="hint">Unknown time uses a local-noon chart. Angles, houses, and overlays become unreliable when time is unknown.</p>
      </div>

      <div class="divider"></div>

      <div class="tight">
        <h2>Person B</h2>
        <div class="person-grid">
          <label>Name<input name="b_name" value="Person B" required /></label>
          <label>Date<input name="b_date" type="date" value="1990-07-15" required /></label>
          <label>Time<input name="b_time" type="time" value="09:15" /></label>
          <label>Time known?
            <select name="b_time_known"><option value="true" selected>Yes</option><option value="false">No</option></select>
          </label>
          <label>Place preset<select name="b_place_preset"><option value="">Manual coordinates</option></select></label>
          <label>Timezone<input name="b_timezone" value="America/New_York" required /></label>
          <label>Latitude<input name="b_latitude" type="number" step="0.0001" value="40.7128" required /></label>
          <label>Longitude<input name="b_longitude" type="number" step="0.0001" value="-74.0060" required /></label>
        </div>
        <p class="hint">Coordinates only need to be approximate for planets, but angles and houses need good location + time accuracy.</p>
      </div>

      <div class="divider"></div>

      <div class="tight">
        <h2>Relationship Context</h2>
        <div class="context-grid">
          <label>Relationship type
            <select name="relationship_type">
              <option value="romantic" selected>Romantic</option><option value="long_term_partner">Long-term partner</option><option value="ex">Ex</option><option value="parent">Parent</option><option value="child">Child</option><option value="sibling">Sibling</option><option value="friend">Friend</option><option value="collaborator">Collaborator</option><option value="admired_figure">Admired figure</option><option value="other">Other</option>
            </select>
          </label>
          <label>Status
            <select name="status"><option value="current" selected>Current</option><option value="past">Past</option><option value="hypothetical">Hypothetical</option><option value="complicated">Complicated</option><option value="unresolved">Unresolved</option><option value="unknown">Unknown</option></select>
          </label>
        </div>
        <label>User question<textarea name="user_question">What is the dynamic between us?</textarea></label>
        <label>Origin story / symbolic context<textarea name="origin_story">We met unexpectedly and the connection felt vivid from the beginning.</textarea></label>
        <label>Known themes, comma separated<input name="known_themes" value="attraction, communication, timing" /></label>
        <label>House system
          <select name="house_system"><option value="whole_sign" selected>Whole Sign</option><option value="placidus">Placidus</option><option value="porphyry">Porphyry</option><option value="regiomontanus">Regiomontanus</option><option value="equal">Equal</option></select>
        </label>
      </div>

      <div class="actions">
        <button id="generate" type="submit">Generate Report</button>
        <button class="secondary" id="sample" type="button">Reset Sample</button>
        <button class="secondary" id="copy" type="button">Copy Markdown</button>
      </div>
      <div id="status" class="status">Ready.</div>
      <p class="small-note">Prototype note: preset places are convenience approximations, not a replacement for real geocoding. Historical timezone handling still needs validation.</p>
    </form>

    <section class="card stack">
      <div class="actions" style="justify-content: space-between; gap: 12px;">
        <div><h2>Report Output</h2><p class="muted">Preview or raw Markdown.</p></div>
        <div class="tabs" role="tablist" aria-label="Output view"><button class="tab active" id="preview-tab" type="button">Preview</button><button class="tab" id="markdown-tab" type="button">Markdown</button></div>
      </div>
      <div id="preview" class="output-html">Generate a report to see the formatted preview.</div>
      <pre id="markdown" class="hidden">Generate a report to see Markdown.</pre>
    </section>
  </section>
</main>

<script>
const form = document.getElementById("relationship-form");
const statusEl = document.getElementById("status");
const preview = document.getElementById("preview");
const markdown = document.getElementById("markdown");
const previewTab = document.getElementById("preview-tab");
const markdownTab = document.getElementById("markdown-tab");
const generateButton = document.getElementById("generate");
let currentMarkdown = "";
let placePresets = [];

const sample = {
  a_name: "Person A", a_date: "1992-01-03", a_time: "17:37", a_time_known: "true", a_place_preset: "san_antonio_tx", a_latitude: "29.4252", a_longitude: "-98.4946", a_timezone: "America/Chicago",
  b_name: "Person B", b_date: "1990-07-15", b_time: "09:15", b_time_known: "true", b_place_preset: "new_york_ny", b_latitude: "40.7128", b_longitude: "-74.0060", b_timezone: "America/New_York",
  relationship_type: "romantic", status: "current", user_question: "What is the dynamic between us?", origin_story: "We met unexpectedly and the connection felt vivid from the beginning.", known_themes: "attraction, communication, timing", house_system: "whole_sign"
};

function setForm(values) { for (const [key, value] of Object.entries(values)) { const field = form.elements[key]; if (field) field.value = value; } updateTimeKnown("a"); updateTimeKnown("b"); }
function updateTimeKnown(prefix) { const known = form.elements[`${prefix}_time_known`].value === "true"; form.elements[`${prefix}_time`].disabled = !known; if (!known) form.elements[`${prefix}_time`].value = ""; }
function applyPreset(prefix, id) { const preset = placePresets.find((place) => place.id === id); if (!preset) return; form.elements[`${prefix}_latitude`].value = preset.latitude; form.elements[`${prefix}_longitude`].value = preset.longitude; form.elements[`${prefix}_timezone`].value = preset.timezone; }

function person(prefix) {
  const timeKnown = form.elements[`${prefix}_time_known`].value === "true";
  const timeValue = form.elements[`${prefix}_time`].value;
  return { name: form.elements[`${prefix}_name`].value, date: form.elements[`${prefix}_date`].value, time: timeKnown && timeValue ? timeValue : null, time_known: timeKnown, latitude: Number(form.elements[`${prefix}_latitude`].value), longitude: Number(form.elements[`${prefix}_longitude`].value), timezone: form.elements[`${prefix}_timezone`].value };
}

function payloadFromForm() {
  const knownThemes = form.elements.known_themes.value.split(",").map((item) => item.trim()).filter(Boolean);
  return { person_a: person("a"), person_b: person("b"), house_system: form.elements.house_system.value, context: { relationship_type: form.elements.relationship_type.value, status: form.elements.status.value, user_question: form.elements.user_question.value || null, origin_story: form.elements.origin_story.value || null, known_themes: knownThemes } };
}

function escapeHtml(value) { return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }
function inlineMarkdown(value) { return escapeHtml(value).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"); }
function markdownToHtml(md) {
  const lines = md.split("\n"); let html = ""; let inList = false;
  function closeList() { if (inList) { html += "</ul>"; inList = false; } }
  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line.trim()) { closeList(); continue; }
    if (line.startsWith("# ")) { closeList(); html += `<h1>${inlineMarkdown(line.slice(2))}</h1>`; }
    else if (line.startsWith("## ")) { closeList(); html += `<h2>${inlineMarkdown(line.slice(3))}</h2>`; }
    else if (line.startsWith("### ")) { closeList(); html += `<h3>${inlineMarkdown(line.slice(4))}</h3>`; }
    else if (line.startsWith("- ")) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inlineMarkdown(line.slice(2))}</li>`; }
    else { closeList(); html += `<p>${inlineMarkdown(line)}</p>`; }
  }
  closeList(); return html;
}

function showError(message) { preview.innerHTML = `<div class="error">${escapeHtml(message)}</div>`; markdown.textContent = message; }
function setTab(which) { const showPreview = which === "preview"; preview.classList.toggle("hidden", !showPreview); markdown.classList.toggle("hidden", showPreview); previewTab.classList.toggle("active", showPreview); markdownTab.classList.toggle("active", !showPreview); }

async function loadPlaces() {
  try {
    const response = await fetch("/places");
    placePresets = await response.json();
    for (const prefix of ["a", "b"]) {
      const select = form.elements[`${prefix}_place_preset`];
      for (const place of placePresets) {
        const option = document.createElement("option"); option.value = place.id; option.textContent = place.label; select.appendChild(option);
      }
    }
    setForm(sample);
  } catch (error) { statusEl.textContent = "Place presets unavailable; manual coordinates still work."; }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault(); statusEl.textContent = "Generating…"; generateButton.disabled = true;
  try {
    const response = await fetch("/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payloadFromForm()) });
    const data = await response.json();
    if (!response.ok) { showError(JSON.stringify(data, null, 2)); statusEl.textContent = "Error."; return; }
    currentMarkdown = data.markdown; markdown.textContent = currentMarkdown; preview.innerHTML = markdownToHtml(currentMarkdown); setTab("preview"); statusEl.textContent = "Report generated.";
  } catch (error) { showError(String(error)); statusEl.textContent = "Error."; }
  finally { generateButton.disabled = false; }
});

document.getElementById("sample").addEventListener("click", () => { setForm(sample); applyPreset("a", sample.a_place_preset); applyPreset("b", sample.b_place_preset); statusEl.textContent = "Sample restored."; });
document.getElementById("copy").addEventListener("click", async () => { if (!currentMarkdown) { statusEl.textContent = "No report to copy yet."; return; } await navigator.clipboard.writeText(currentMarkdown); statusEl.textContent = "Markdown copied."; });
previewTab.addEventListener("click", () => setTab("preview")); markdownTab.addEventListener("click", () => setTab("markdown"));
form.elements.a_time_known.addEventListener("change", () => updateTimeKnown("a")); form.elements.b_time_known.addEventListener("change", () => updateTimeKnown("b"));
form.elements.a_place_preset.addEventListener("change", (event) => applyPreset("a", event.target.value)); form.elements.b_place_preset.addEventListener("change", (event) => applyPreset("b", event.target.value));

setForm(sample);
loadPlaces();
</script>
</body>
</html>
"""
