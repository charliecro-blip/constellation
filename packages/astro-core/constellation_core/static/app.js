const form = document.getElementById("relationship-form");
const statusEl = document.getElementById("status");
const preview = document.getElementById("preview");
const markdown = document.getElementById("markdown");
const markdownTab = document.getElementById("markdown-tab");
const generateButton = document.getElementById("generate");
const providerStatus = document.getElementById("provider-status");
const reportStatusEl = document.getElementById("report_status");
const downloadLink = document.getElementById("download");
const refreshConstellationButton = document.getElementById("refresh_constellation");
const constellationEl = document.getElementById("constellation");
let currentMarkdown = "";
let currentDownloadUrl = "";
let currentSavedRelationship = null;
let currentSynthesisPacket = null;
let enhancementRequestId = 0;
let searchResults = { a: [], b: [] };
let placeSelections = { a: null, b: null };
let shouldScrollToReport = false;
const draftKey = "constellation.relationshipForm.v1";
const constellationPatternsEmptyState = "Save two or more relationships to see recurring patterns across your constellation.";

const defaultState = {
  a_name: "",
  a_date: "",
  a_time: "",
  a_time_known: "true",
  a_place_query: "",
  a_latitude: "",
  a_longitude: "",
  a_timezone: "",
  b_name: "",
  b_date: "",
  b_time: "",
  b_time_known: "true",
  b_place_query: "",
  b_latitude: "",
  b_longitude: "",
  b_timezone: "",
  relationship_type: "romantic",
  user_question: "",
  origin_story: "",
  house_system: "placidus",
};

const sample = {
  a_name: "You",
  a_date: "1992-01-03",
  a_time: "17:37",
  a_time_known: "true",
  a_place_query: "San Antonio, TX",
  a_latitude: "29.4252",
  a_longitude: "-98.4946",
  a_timezone: "America/Chicago",
  b_name: "Someone",
  b_date: "1990-07-15",
  b_time: "09:15",
  b_time_known: "true",
  b_place_query: "New York, NY",
  b_latitude: "40.7128",
  b_longitude: "-74.0060",
  b_timezone: "America/New_York",
  relationship_type: "romantic",
  user_question: "What is the dynamic between us?",
  origin_story: "We met unexpectedly and the connection felt vivid from the beginning.",
  house_system: "placidus",
};

function fieldValue(name, fallback = "") {
  const field = form.elements[name];
  return field ? field.value : fallback;
}

function setForm(values) {
  for (const [key, value] of Object.entries(values)) {
    const field = form.elements[key];
    if (field) field.value = value;
  }
  updateTimeKnown("a");
  updateTimeKnown("b");
}

function formValues() {
  const values = {};
  for (const element of Array.from(form.elements)) {
    if (element.name) values[element.name] = element.value;
  }
  return values;
}

function saveDraft() {
  localStorage.setItem(draftKey, JSON.stringify(formValues()));
}

function restoreDraft() {
  const raw = localStorage.getItem(draftKey);
  if (!raw) {
    statusEl.textContent = "No browser draft saved yet.";
    return;
  }
  setForm(JSON.parse(raw));
  statusEl.textContent = "Browser draft restored.";
}

function updateTimeKnown(prefix) {
  const known = fieldValue(`${prefix}_time_known`, "true") === "true";
  const timeField = form.elements[`${prefix}_time`];
  if (!timeField) return;
  timeField.disabled = !known;
  if (!known) timeField.value = "";
}

function setPlaceWarning(prefix, message) {
  const warning = document.getElementById(`${prefix}_place_warning`);
  if (!warning) return;
  warning.textContent = message;
  warning.classList.toggle("hidden", !message);
}

function clearPlaceSelection(prefix) {
  form.elements[`${prefix}_latitude`].value = "";
  form.elements[`${prefix}_longitude`].value = "";
  form.elements[`${prefix}_timezone`].value = "";
  const select = form.elements[`${prefix}_place_result`];
  const label = document.getElementById(`${prefix}_place_result_label`);
  if (select) select.innerHTML = '<option value="">Search to see options</option>';
  if (label) label.classList.add("hidden");
  searchResults[prefix] = [];
  placeSelections[prefix] = null;
  setPlaceWarning(prefix, "Birthplace changed. Search again and select a result before generating.");
}

function applyPlace(prefix, place) {
  form.elements[`${prefix}_latitude`].value = Number(place.latitude).toFixed(4);
  form.elements[`${prefix}_longitude`].value = Number(place.longitude).toFixed(4);
  form.elements[`${prefix}_timezone`].value = place.timezone;
  form.elements[`${prefix}_place_query`].value = place.label;
  placeSelections[prefix] = { label: place.label, latitude: Number(place.latitude), longitude: Number(place.longitude), timezone: place.timezone };
  setPlaceWarning(prefix, "");
}

function populateSearchResults(prefix, results) {
  const select = form.elements[`${prefix}_place_result`];
  const label = document.getElementById(`${prefix}_place_result_label`);
  select.innerHTML = '<option value="">Select the closest birthplace</option>';
  searchResults[prefix] = results;
  select.value = "";
  label.classList.toggle("hidden", results.length === 0);
  for (let index = 0; index < results.length; index++) {
    const place = results[index];
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${place.label} — ${place.timezone}`;
    select.appendChild(option);
  }
}

async function searchPlace(prefix) {
  const query = fieldValue(`${prefix}_place_query`).trim();
  if (!query) {
    statusEl.textContent = "Enter a birthplace search first.";
    return;
  }
  searchResults[prefix] = [];
  statusEl.textContent = `Searching for \"${query}\"…`;
  try {
    const response = await fetch(`/places/search?q=${encodeURIComponent(query)}`);
    const payload = await response.json();
    const results = payload.results || [];
    populateSearchResults(prefix, results);
    if (results.length) {
      applyPlace(prefix, results[0]);
      statusEl.textContent = payload.provider_available
        ? "Birthplace found. Choose this city or pick another nearby option."
        : (payload.message || "Closest birthplace found from fallback data.");
      return;
    }
    statusEl.textContent = payload.message || "No birthplace options found. Try a broader search or use advanced manual details.";
  } catch {
    statusEl.textContent = "Birthplace search is unavailable right now. You can still use advanced manual details.";
  }
}

function hasCompletePlaceDetails(prefix) {
  return fieldValue(`${prefix}_latitude`) && fieldValue(`${prefix}_longitude`) && fieldValue(`${prefix}_timezone`);
}

function placeSelectionIsStale(prefix) {
  const query = fieldValue(`${prefix}_place_query`).trim();
  const selection = placeSelections[prefix];
  return query && hasCompletePlaceDetails(prefix) && selection && selection.label !== query;
}

function person(prefix) {
  const timeKnown = fieldValue(`${prefix}_time_known`, "true") === "true";
  const timeValue = fieldValue(`${prefix}_time`);
  if (fieldValue(`${prefix}_place_query`).trim() && !hasCompletePlaceDetails(prefix)) {
    setPlaceWarning(prefix, "Birthplace changed. Search again and select a result before generating.");
    throw new Error("Please search and select the birthplace before generating.");
  }
  if (placeSelectionIsStale(prefix)) {
    setPlaceWarning(prefix, "Birthplace details may be stale. Search again and select the matching result.");
    throw new Error("Please reselect the birthplace that matches the visible city text.");
  }
  return {
    display_name: fieldValue(`${prefix}_name`),
    birth_date: fieldValue(`${prefix}_date`),
    birth_time: timeKnown && timeValue ? timeValue : null,
    time_known: timeKnown,
    latitude: Number(fieldValue(`${prefix}_latitude`)),
    longitude: Number(fieldValue(`${prefix}_longitude`)),
    timezone: fieldValue(`${prefix}_timezone`),
    birthplace_label: fieldValue(`${prefix}_place_query`) || null,
  };
}

function inferredStatus(relationshipType) {
  if (relationshipType === "ex") return "past";
  if (relationshipType === "unresolved_connection") return "unresolved";
  return "current";
}

function buildContext() {
  const relationshipType = fieldValue("relationship_type", "romantic");
  return {
    relationship_type: relationshipType,
    status: inferredStatus(relationshipType),
    user_question: fieldValue("user_question", "") || null,
    origin_story: fieldValue("origin_story", "") || null,
    known_themes: [],
    house_system: fieldValue("house_system", "placidus"),
  };
}

function relationshipPayload(personAId, personBId) {
  const context = buildContext();
  return { person_a_id: personAId, person_b_id: personBId, ...context };
}

function escapeHtml(value) {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function inlineMarkdown(value) {
  return escapeHtml(value).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

function markdownToHtml(md) {
  const lines = md.split("\n");
  let html = "";
  let inList = false;
  let inDetails = false;
  const defaultOpenSections = new Set(["Overview", "Composite Field"]);
  function closeList() {
    if (inList) {
      html += "</ul>";
      inList = false;
    }
  }
  function closeDetails() {
    closeList();
    if (inDetails) {
      html += "</details>";
      inDetails = false;
    }
  }
  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line.trim()) {
      closeList();
      continue;
    }
    if (line.startsWith("# ")) {
      closeDetails();
      html += `<h1>${inlineMarkdown(line.slice(2))}</h1>`;
    } else if (line.startsWith("## ")) {
      closeDetails();
      const title = line.slice(3);
      const openAttr = defaultOpenSections.has(title) ? " open" : "";
      html += `<details class="report-section"${openAttr}><summary>${inlineMarkdown(title)}</summary>`;
      inDetails = true;
    } else if (line.startsWith("### ")) {
      closeList();
      html += `<h3>${inlineMarkdown(line.slice(4))}</h3>`;
    } else if (line.startsWith("- ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${inlineMarkdown(line.slice(2))}</li>`;
    } else {
      closeList();
      html += `<p>${inlineMarkdown(line)}</p>`;
    }
  }
  closeDetails();
  return html;
}

function setTab(which) {
  const showMarkdown = which === "markdown";
  preview.classList.remove("hidden");
  markdown.classList.toggle("hidden", !showMarkdown);
  markdownTab.classList.toggle("active", showMarkdown);
  markdownTab.textContent = showMarkdown ? "Hide Markdown" : "View Markdown";
}

function setReportMarkdown(markdownText) {
  currentMarkdown = markdownText;
  markdown.textContent = currentMarkdown;
  preview.innerHTML = markdownToHtml(currentMarkdown);
  updateDownload(currentMarkdown);
}

function scrollReportIntoViewOnce() {
  if (!shouldScrollToReport) return;
  shouldScrollToReport = false;
  document.getElementById("report-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function updateDownload(markdownText) {
  if (currentDownloadUrl) URL.revokeObjectURL(currentDownloadUrl);
  const blob = new Blob([markdownText], { type: "text/markdown" });
  currentDownloadUrl = URL.createObjectURL(blob);
  downloadLink.href = currentDownloadUrl;
  downloadLink.classList.remove("hidden");
}

async function createBirthProfile(prefix) {
  const response = await fetch("/birth-profiles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(person(prefix)),
  });
  if (!response.ok) throw new Error("Could not save birth profile");
  return response.json();
}

async function createSavedRelationship() {
  const [personA, personB] = await Promise.all([createBirthProfile("a"), createBirthProfile("b")]);
  const response = await fetch("/saved-relationships", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(relationshipPayload(personA.id, personB.id)),
  });
  if (!response.ok) throw new Error("Could not save relationship");
  currentSavedRelationship = await response.json();
  return currentSavedRelationship;
}

function setReportStatus(message) {
  if (reportStatusEl) reportStatusEl.textContent = message;
}

async function generateSavedReport(relationshipId) {
  setReportStatus("Preparing your map…");
  const response = await fetch(`/saved-relationships/${relationshipId}/report`, { method: "POST" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Could not generate saved report");
  const standardMarkdown = payload.markdown;
  currentSynthesisPacket = payload.synthesis_packet || null;
  setReportMarkdown(standardMarkdown);
  setTab("preview");
  setReportStatus("Relationship Map ready.");
  scrollReportIntoViewOnce();
  void enhanceReportMarkdown(standardMarkdown, currentSynthesisPacket);
}

async function enhanceReportMarkdown(standardMarkdown, synthesisPacket = null) {
  const requestId = enhancementRequestId + 1;
  enhancementRequestId = requestId;
  setReportStatus("Writing your reading…");
  try {
    const response = await fetch("/report/enhance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ markdown: standardMarkdown, context: buildContext(), synthesis_packet: synthesisPacket }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Reading refinement failed.");
    if (requestId !== enhancementRequestId) return;
    setReportMarkdown(payload.markdown);
    setTab("preview");
    setReportStatus("Relationship Map ready.");
  } catch (error) {
    if (requestId !== enhancementRequestId) return;
    setReportMarkdown(standardMarkdown);
    setReportStatus("Relationship Map ready.");
  }
}

function relationshipLabel(item) {
  return `${item.relationship_type} • ${item.status}`;
}

async function fetchConstellationPatterns() {
  try {
    const response = await fetch("/constellation-patterns");
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

function renderCountList(items, labelKey) {
  if (!items.length) return '<p class="small-note">No repeated items are visible yet.</p>';
  return `<ul class="pattern-list">${items.map((item) => `<li><span>${escapeHtml(item[labelKey])}</span><strong>${item.count}</strong></li>`).join("")}</ul>`;
}

function renderConstellationPatterns(summary) {
  if (!summary) {
    return `<section class="pattern-summary"><h3>Constellation Patterns</h3><p class="small-note">Pattern synthesis is unavailable right now. Saved relationship snapshots are still shown below.</p></section>`;
  }
  if (!summary.has_enough_data) {
    return `<section class="pattern-summary"><h3>Constellation Patterns</h3><p class="small-note">${escapeHtml(summary.empty_state || constellationPatternsEmptyState)}</p></section>`;
  }

  const motifCards = summary.recurring_motifs.length
    ? summary.recurring_motifs.map((motif) => `<div class="pattern-card"><strong>${escapeHtml(motif.label)}</strong><div class="small-note">Appears in: ${escapeHtml(motif.people.join(", "))}</div></div>`).join("")
    : '<p class="small-note">No report motifs repeat across saved maps yet. As more relationships are added, this pattern may clarify.</p>';
  const themeLine = summary.known_theme_counts.length
    ? `<p class="small-note">Recurring named themes: ${escapeHtml(summary.known_theme_counts.map((item) => item.theme).join(", "))}.</p>`
    : '<p class="small-note">No recurring named themes have been saved yet.</p>';

  return `
    <section class="pattern-summary">
      <h3>Constellation Patterns</h3>
      <p class="small-note">${summary.relationship_count} saved relationships analyzed.</p>
      <p>${escapeHtml(summary.plain_language_summary)}</p>
      <div class="pattern-grid">
        <div>
          <h4>Relationship types</h4>
          ${renderCountList(summary.relationship_type_counts, "label")}
        </div>
        <div>
          <h4>Recurring themes</h4>
          ${themeLine}
        </div>
      </div>
      <div>
        <h4>Repeated motifs</h4>
        <div class="pattern-card-list">${motifCards}</div>
      </div>
    </section>`;
}

async function loadConstellation() {
  constellationEl.innerHTML = "Loading saved relationships…";
  const [relResponse, patternSummary] = await Promise.all([
    fetch("/saved-relationships"),
    fetchConstellationPatterns(),
  ]);
  if (!relResponse.ok) {
    constellationEl.innerHTML = '<div class="error">Could not load constellation.</div>';
    return;
  }
  const relationships = await relResponse.json();
  if (!relationships.length) {
    constellationEl.innerHTML = `${renderConstellationPatterns(patternSummary)}<p class="small-note">No saved relationships yet. Save one to start your constellation.</p>`;
    return;
  }
  constellationEl.innerHTML = renderConstellationPatterns(patternSummary);
  for (const rel of relationships.slice(0, 12)) {
    const node = document.createElement("div");
    node.className = "constellation-node";
    node.innerHTML = `<strong>${escapeHtml(relationshipLabel(rel))}</strong><div class="small-note">${new Date(rel.created_at).toLocaleString()}</div><div class="small-note">themes: ${escapeHtml(rel.known_themes.join(", ") || "none")}</div>`;
    const action = document.createElement("button");
    action.type = "button";
    action.className = "secondary";
    action.textContent = "Generate Relationship Map";
    action.addEventListener("click", async () => {
      statusEl.textContent = "Generating report from saved relationship…";
      try {
        await generateSavedReport(rel.id);
        statusEl.textContent = "Saved relationship report generated.";
      } catch (error) {
        statusEl.textContent = error.message;
      }
    });
    node.appendChild(action);
    constellationEl.appendChild(node);
  }
}

async function loadPlaces() {
  const raw = localStorage.getItem(draftKey);
  setForm(raw ? JSON.parse(raw) : defaultState);
}

async function loadProviderStatus() {
  if (!providerStatus) return;
  try {
    await fetch("/geocoding/status");
    providerStatus.textContent = "Birthplace search is ready.";
    providerStatus.className = "hint";
  } catch {
    providerStatus.textContent = "Start typing a birthplace and choose the closest match.";
    providerStatus.className = "hint";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  shouldScrollToReport = true;
  setReportStatus("Preparing your map…");
  statusEl.textContent = "Saving relationship and generating report…";
  generateButton.disabled = true;
  try {
    const relationship = await createSavedRelationship();
    await generateSavedReport(relationship.id);
    await loadConstellation();
    saveDraft();
    statusEl.textContent = "Relationship mapped. Your constellation is updated.";
  } catch (error) {
    statusEl.textContent = error.message || "Request failed";
  } finally {
    generateButton.disabled = false;
  }
});

refreshConstellationButton.addEventListener("click", loadConstellation);
document.getElementById("save").addEventListener("click", () => { saveDraft(); statusEl.textContent = "Browser draft saved."; });
document.getElementById("restore").addEventListener("click", restoreDraft);
document.getElementById("sample").addEventListener("click", () => { setForm(sample); statusEl.textContent = "Sample relationship restored."; });
document.getElementById("copy").addEventListener("click", async () => { if (!currentMarkdown) return; await navigator.clipboard.writeText(currentMarkdown); statusEl.textContent = "Markdown copied."; });
markdownTab.addEventListener("click", () => setTab(markdown.classList.contains("hidden") ? "markdown" : "preview"));
form.elements.a_time_known.addEventListener("change", () => updateTimeKnown("a"));
form.elements.b_time_known.addEventListener("change", () => updateTimeKnown("b"));
form.elements.a_place_query.addEventListener("input", () => clearPlaceSelection("a"));
form.elements.b_place_query.addEventListener("input", () => clearPlaceSelection("b"));
form.elements.a_place_result.addEventListener("change", (event) => { const place = searchResults.a[Number(event.target.value)]; if (place) applyPlace("a", place); });
form.elements.b_place_result.addEventListener("change", (event) => { const place = searchResults.b[Number(event.target.value)]; if (place) applyPlace("b", place); });
document.getElementById("a_search_button").addEventListener("click", () => searchPlace("a"));
document.getElementById("b_search_button").addEventListener("click", () => searchPlace("b"));

setForm(defaultState);
loadProviderStatus();
loadPlaces().catch(() => {});
loadConstellation().catch(() => { constellationEl.innerHTML = "Constellation view unavailable."; });
