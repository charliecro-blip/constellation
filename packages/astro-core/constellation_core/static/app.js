const form = document.getElementById("relationship-form");
const statusEl = document.getElementById("status");
const preview = document.getElementById("preview");
const markdown = document.getElementById("markdown");
const previewTab = document.getElementById("preview-tab");
const markdownTab = document.getElementById("markdown-tab");
const generateButton = document.getElementById("generate");
const providerStatus = document.getElementById("provider-status");
const downloadLink = document.getElementById("download");
const saveRelationshipButton = document.getElementById("save_relationship");
const refreshConstellationButton = document.getElementById("refresh_constellation");
const constellationEl = document.getElementById("constellation");
let currentMarkdown = "";
let currentDownloadUrl = "";
let currentSavedRelationship = null;
let placePresets = [];
let searchResults = { a: [], b: [] };
const draftKey = "constellation.relationshipForm.v1";

const sample = { a_name: "Person A", a_date: "1992-01-03", a_time: "17:37", a_time_known: "true", a_place_preset: "san_antonio_tx", a_place_query: "San Antonio, TX", a_latitude: "29.4252", a_longitude: "-98.4946", a_timezone: "America/Chicago", b_name: "Person B", b_date: "1990-07-15", b_time: "09:15", b_time_known: "true", b_place_preset: "new_york_ny", b_place_query: "New York, NY", b_latitude: "40.7128", b_longitude: "-74.0060", b_timezone: "America/New_York", relationship_type: "romantic", status: "current", user_question: "What is the dynamic between us?", origin_story: "We met unexpectedly and the connection felt vivid from the beginning.", known_themes: "attraction, communication, timing", house_system: "whole_sign" };

function setForm(values) { for (const [key, value] of Object.entries(values)) { const field = form.elements[key]; if (field) field.value = value; } updateTimeKnown("a"); updateTimeKnown("b"); }
function formValues() { const values = {}; for (const element of Array.from(form.elements)) { if (element.name) values[element.name] = element.value; } return values; }
function saveDraft() { localStorage.setItem(draftKey, JSON.stringify(formValues())); }
function restoreDraft() { const raw = localStorage.getItem(draftKey); if (!raw) { statusEl.textContent = "No browser draft saved yet."; return; } setForm(JSON.parse(raw)); statusEl.textContent = "Browser draft restored."; }
function updateTimeKnown(prefix) { const known = form.elements[`${prefix}_time_known`].value === "true"; form.elements[`${prefix}_time`].disabled = !known; if (!known) form.elements[`${prefix}_time`].value = ""; }
function applyPlace(prefix, place) { form.elements[`${prefix}_latitude`].value = Number(place.latitude).toFixed(4); form.elements[`${prefix}_longitude`].value = Number(place.longitude).toFixed(4); form.elements[`${prefix}_timezone`].value = place.timezone; form.elements[`${prefix}_place_query`].value = place.label; }
function applyPreset(prefix, id) { const preset = placePresets.find((place) => place.id === id); if (!preset) return; applyPlace(prefix, preset); }
function populateSearchResults(prefix, results) { const select = form.elements[`${prefix}_place_result`]; select.innerHTML = '<option value="">Choose a search result</option>'; searchResults[prefix] = results; for (let index = 0; index < results.length; index++) { const place = results[index]; const option = document.createElement("option"); option.value = String(index); option.textContent = `${place.label} — ${place.timezone}`; select.appendChild(option); } }
async function searchPlace(prefix) { const query = form.elements[`${prefix}_place_query`].value.trim(); if (!query) { statusEl.textContent = "Enter a place search first."; return; } statusEl.textContent = `Searching ${query}…`; try { const response = await fetch(`/places/search?q=${encodeURIComponent(query)}`); const payload = await response.json(); populateSearchResults(prefix, payload.results || []); if (payload.results && payload.results.length) { applyPlace(prefix, payload.results[0]); statusEl.textContent = payload.provider_available ? "Place found." : (payload.message || "Preset result found."); } else { statusEl.textContent = payload.message || "No place results found."; } } catch (error) { statusEl.textContent = "Place search failed; manual coordinates still work."; } }

function person(prefix) { const timeKnown = form.elements[`${prefix}_time_known`].value === "true"; const timeValue = form.elements[`${prefix}_time`].value; return { display_name: form.elements[`${prefix}_name`].value, birth_date: form.elements[`${prefix}_date`].value, birth_time: timeKnown && timeValue ? timeValue : null, time_known: timeKnown, latitude: Number(form.elements[`${prefix}_latitude`].value), longitude: Number(form.elements[`${prefix}_longitude`].value), timezone: form.elements[`${prefix}_timezone`].value, birthplace_label: form.elements[`${prefix}_place_query`].value || null }; }
function buildContext() { return { relationship_type: form.elements.relationship_type.value, status: form.elements.status.value, user_question: form.elements.user_question.value || null, origin_story: form.elements.origin_story.value || null, known_themes: form.elements.known_themes.value.split(",").map((item) => item.trim()).filter(Boolean), house_system: form.elements.house_system.value }; }
function relationshipPayload(personAId, personBId) { const context = buildContext(); return { person_a_id: personAId, person_b_id: personBId, ...context }; }
function escapeHtml(value) { return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }
function inlineMarkdown(value) { return escapeHtml(value).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"); }
function markdownToHtml(md) { const lines = md.split("\n"); let html = ""; let inList = false; function closeList() { if (inList) { html += "</ul>"; inList = false; } } for (const rawLine of lines) { const line = rawLine.trimEnd(); if (!line.trim()) { closeList(); continue; } if (line.startsWith("# ")) { closeList(); html += `<h1>${inlineMarkdown(line.slice(2))}</h1>`; } else if (line.startsWith("## ")) { closeList(); html += `<h2>${inlineMarkdown(line.slice(3))}</h2>`; } else if (line.startsWith("### ")) { closeList(); html += `<h3>${inlineMarkdown(line.slice(4))}</h3>`; } else if (line.startsWith("- ")) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inlineMarkdown(line.slice(2))}</li>`; } else { closeList(); html += `<p>${inlineMarkdown(line)}</p>`; } } closeList(); return html; }
function setTab(which) { const showPreview = which === "preview"; preview.classList.toggle("hidden", !showPreview); markdown.classList.toggle("hidden", showPreview); previewTab.classList.toggle("active", showPreview); markdownTab.classList.toggle("active", !showPreview); }
function updateDownload(markdownText) { if (currentDownloadUrl) URL.revokeObjectURL(currentDownloadUrl); const blob = new Blob([markdownText], { type: "text/markdown" }); currentDownloadUrl = URL.createObjectURL(blob); downloadLink.href = currentDownloadUrl; downloadLink.classList.remove("hidden"); }

async function createBirthProfile(prefix) {
  const response = await fetch("/birth-profiles", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(person(prefix)) });
  if (!response.ok) throw new Error(`Could not save person ${prefix.toUpperCase()}`);
  return response.json();
}

async function createSavedRelationship() {
  const [personA, personB] = await Promise.all([createBirthProfile("a"), createBirthProfile("b")]);
  const response = await fetch("/saved-relationships", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(relationshipPayload(personA.id, personB.id)) });
  if (!response.ok) throw new Error("Could not save relationship");
  currentSavedRelationship = await response.json();
  return currentSavedRelationship;
}

async function generateSavedReport(relationshipId) {
  const response = await fetch(`/saved-relationships/${relationshipId}/report`, { method: "POST" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Could not generate saved report");
  currentMarkdown = payload.markdown;
  markdown.textContent = currentMarkdown;
  preview.innerHTML = markdownToHtml(currentMarkdown);
  updateDownload(currentMarkdown);
  setTab("preview");
}

function relationshipLabel(item) { return `${item.relationship_type} • ${item.status}`; }

async function loadConstellation() {
  constellationEl.innerHTML = "Loading saved relationships…";
  const relResponse = await fetch("/saved-relationships");
  if (!relResponse.ok) { constellationEl.innerHTML = '<div class="error">Could not load constellation.</div>'; return; }
  const relationships = await relResponse.json();
  if (!relationships.length) { constellationEl.innerHTML = "No saved relationships yet. Save one to start your constellation."; return; }
  constellationEl.innerHTML = "";
  for (const rel of relationships.slice(0, 12)) {
    const node = document.createElement("div");
    node.className = "constellation-node";
    node.innerHTML = `<strong>${escapeHtml(relationshipLabel(rel))}</strong><div class="small-note">${new Date(rel.created_at).toLocaleString()}</div><div class="small-note">themes: ${escapeHtml(rel.known_themes.join(", ") || "none")}</div>`;
    const action = document.createElement("button");
    action.type = "button";
    action.className = "secondary";
    action.textContent = "Generate Report";
    action.addEventListener("click", async () => {
      statusEl.textContent = "Generating report from saved relationship…";
      try { await generateSavedReport(rel.id); statusEl.textContent = "Saved relationship report generated."; }
      catch (error) { statusEl.textContent = error.message; }
    });
    node.appendChild(action);
    constellationEl.appendChild(node);
  }
}

async function loadPlaces() { const response = await fetch("/places"); placePresets = await response.json(); for (const prefix of ["a", "b"]) { const select = form.elements[`${prefix}_place_preset`]; for (const place of placePresets) { const option = document.createElement("option"); option.value = place.id; option.textContent = place.label; select.appendChild(option); } } const raw = localStorage.getItem(draftKey); setForm(raw ? JSON.parse(raw) : sample); }
async function loadProviderStatus() { const response = await fetch("/geocoding/status"); const payload = await response.json(); providerStatus.textContent = payload.message; providerStatus.className = payload.provider_configured ? "notice" : "small-note"; }

form.addEventListener("submit", async (event) => { event.preventDefault(); statusEl.textContent = "Saving relationship and generating report…"; generateButton.disabled = true; try { const relationship = await createSavedRelationship(); await generateSavedReport(relationship.id); await loadConstellation(); saveDraft(); statusEl.textContent = "Saved + generated. Your constellation is updated."; } catch (error) { statusEl.textContent = error.message || "Request failed"; } finally { generateButton.disabled = false; } });
saveRelationshipButton.addEventListener("click", async () => { statusEl.textContent = "Saving relationship only…"; try { await createSavedRelationship(); await loadConstellation(); saveDraft(); statusEl.textContent = "Relationship saved."; } catch (error) { statusEl.textContent = error.message; } });
refreshConstellationButton.addEventListener("click", loadConstellation);

document.getElementById("save").addEventListener("click", () => { saveDraft(); statusEl.textContent = "Browser draft saved."; });
document.getElementById("restore").addEventListener("click", restoreDraft);
document.getElementById("sample").addEventListener("click", () => { setForm(sample); applyPreset("a", sample.a_place_preset); applyPreset("b", sample.b_place_preset); statusEl.textContent = "Base sample restored."; });
document.getElementById("copy").addEventListener("click", async () => { if (!currentMarkdown) return; await navigator.clipboard.writeText(currentMarkdown); statusEl.textContent = "Markdown copied."; });
previewTab.addEventListener("click", () => setTab("preview")); markdownTab.addEventListener("click", () => setTab("markdown"));
form.elements.a_time_known.addEventListener("change", () => updateTimeKnown("a")); form.elements.b_time_known.addEventListener("change", () => updateTimeKnown("b"));
form.elements.a_place_preset.addEventListener("change", (event) => applyPreset("a", event.target.value)); form.elements.b_place_preset.addEventListener("change", (event) => applyPreset("b", event.target.value));
form.elements.a_place_result.addEventListener("change", (event) => { const place = searchResults.a[Number(event.target.value)]; if (place) applyPlace("a", place); });
form.elements.b_place_result.addEventListener("change", (event) => { const place = searchResults.b[Number(event.target.value)]; if (place) applyPlace("b", place); });
document.getElementById("a_search_button").addEventListener("click", () => searchPlace("a")); document.getElementById("b_search_button").addEventListener("click", () => searchPlace("b"));

setForm(sample);
loadProviderStatus().catch(() => {});
loadPlaces().catch(() => {});
loadConstellation().catch(() => { constellationEl.innerHTML = "Constellation view unavailable."; });
