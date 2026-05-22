const form = document.getElementById("relationship-form");
const statusEl = document.getElementById("status");
const preview = document.getElementById("preview");
const markdown = document.getElementById("markdown");
const previewTab = document.getElementById("preview-tab");
const markdownTab = document.getElementById("markdown-tab");
const generateButton = document.getElementById("generate");
const providerStatus = document.getElementById("provider-status");
const downloadLink = document.getElementById("download");
let currentMarkdown = "";
let currentDownloadUrl = "";
let placePresets = [];
let searchResults = { a: [], b: [] };
const draftKey = "constellation.relationshipForm.v1";

const baseSample = { a_name: "Person A", a_date: "1992-01-03", a_time: "17:37", a_time_known: "true", a_place_preset: "san_antonio_tx", a_place_query: "San Antonio, TX", a_latitude: "29.4252", a_longitude: "-98.4946", a_timezone: "America/Chicago", b_name: "Person B", b_date: "1990-07-15", b_time: "09:15", b_time_known: "true", b_place_preset: "new_york_ny", b_place_query: "New York, NY", b_latitude: "40.7128", b_longitude: "-74.0060", b_timezone: "America/New_York", relationship_type: "romantic", status: "current", user_question: "What is the dynamic between us?", origin_story: "We met unexpectedly and the connection felt vivid from the beginning.", known_themes: "attraction, communication, timing", house_system: "whole_sign" };
const relationshipSamples = {
  romantic_current: { relationship_type: "romantic", status: "current", user_question: "How do we sustain intensity without losing emotional safety?", origin_story: "We are currently together and the bond is vivid, magnetic, and sometimes overwhelming.", known_themes: "attraction, communication, pacing" },
  ex_unresolved: { relationship_type: "ex", status: "unresolved", user_question: "What keeps us psychologically unfinished?", origin_story: "We are no longer together but remain emotionally entangled and reactive.", known_themes: "unfinished business, grief, attachment" },
  friend: { relationship_type: "friend", status: "current", user_question: "What supports trust and longevity in this friendship?", origin_story: "We became close through shared vulnerability and recurring life transitions.", known_themes: "loyalty, emotional support, boundaries" },
  collaborator: { relationship_type: "collaborator", status: "current", user_question: "How can we align vision and execution without burnout?", origin_story: "We work closely and create strong momentum, but coordination pressure is rising.", known_themes: "creative flow, roles, communication" },
  family: { relationship_type: "parent", status: "complicated", user_question: "How do we repair while respecting history and limits?", origin_story: "This family tie has deep familiarity, recurring triggers, and moments of care.", known_themes: "legacy patterns, duty, repair" },
  admired_figure: { relationship_type: "admired_figure", status: "hypothetical", user_question: "What is being projected and what is genuinely resonant?", origin_story: "This connection is mostly symbolic and directional, with strong aspirational charge.", known_themes: "projection, desire, growth" }
};
const sample = baseSample;

function setForm(values) { for (const [key, value] of Object.entries(values)) { const field = form.elements[key]; if (field) field.value = value; } updateTimeKnown("a"); updateTimeKnown("b"); }
function formValues() { const values = {}; for (const element of Array.from(form.elements)) { if (element.name) values[element.name] = element.value; } return values; }
function saveDraft() { localStorage.setItem(draftKey, JSON.stringify(formValues())); statusEl.textContent = "Browser draft saved."; }
function restoreDraft() { const raw = localStorage.getItem(draftKey); if (!raw) { statusEl.textContent = "No browser draft saved yet."; return; } setForm(JSON.parse(raw)); statusEl.textContent = "Browser draft restored."; }
function updateTimeKnown(prefix) { const known = form.elements[`${prefix}_time_known`].value === "true"; form.elements[`${prefix}_time`].disabled = !known; if (!known) form.elements[`${prefix}_time`].value = ""; }
function applyPlace(prefix, place) { form.elements[`${prefix}_latitude`].value = Number(place.latitude).toFixed(4); form.elements[`${prefix}_longitude`].value = Number(place.longitude).toFixed(4); form.elements[`${prefix}_timezone`].value = place.timezone; form.elements[`${prefix}_place_query`].value = place.label; }
function applyPreset(prefix, id) { const preset = placePresets.find((place) => place.id === id); if (!preset) return; applyPlace(prefix, preset); }
function populateSearchResults(prefix, results) { const select = form.elements[`${prefix}_place_result`]; select.innerHTML = '<option value="">Choose a search result</option>'; searchResults[prefix] = results; for (let index = 0; index < results.length; index++) { const place = results[index]; const option = document.createElement("option"); option.value = String(index); option.textContent = `${place.label} — ${place.timezone}`; select.appendChild(option); } }
async function searchPlace(prefix) { const query = form.elements[`${prefix}_place_query`].value.trim(); if (!query) { statusEl.textContent = "Enter a place search first."; return; } statusEl.textContent = `Searching ${query}…`; try { const response = await fetch(`/places/search?q=${encodeURIComponent(query)}`); const payload = await response.json(); populateSearchResults(prefix, payload.results || []); if (payload.results && payload.results.length) { applyPlace(prefix, payload.results[0]); statusEl.textContent = payload.provider_available ? "Place found." : (payload.message || "Preset result found."); } else { statusEl.textContent = payload.message || "No place results found."; } } catch (error) { statusEl.textContent = "Place search failed; manual coordinates still work."; } }

function person(prefix) { const timeKnown = form.elements[`${prefix}_time_known`].value === "true"; const timeValue = form.elements[`${prefix}_time`].value; return { name: form.elements[`${prefix}_name`].value, date: form.elements[`${prefix}_date`].value, time: timeKnown && timeValue ? timeValue : null, time_known: timeKnown, latitude: Number(form.elements[`${prefix}_latitude`].value), longitude: Number(form.elements[`${prefix}_longitude`].value), timezone: form.elements[`${prefix}_timezone`].value }; }
function payloadFromForm() { const knownThemes = form.elements.known_themes.value.split(",").map((item) => item.trim()).filter(Boolean); return { person_a: person("a"), person_b: person("b"), house_system: form.elements.house_system.value, context: { relationship_type: form.elements.relationship_type.value, status: form.elements.status.value, user_question: form.elements.user_question.value || null, origin_story: form.elements.origin_story.value || null, known_themes: knownThemes } }; }
function escapeHtml(value) { return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }
function inlineMarkdown(value) { return escapeHtml(value).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"); }
function markdownToHtml(md) { const lines = md.split("\n"); let html = ""; let inList = false; function closeList() { if (inList) { html += "</ul>"; inList = false; } } for (const rawLine of lines) { const line = rawLine.trimEnd(); if (!line.trim()) { closeList(); continue; } if (line.startsWith("# ")) { closeList(); html += `<h1>${inlineMarkdown(line.slice(2))}</h1>`; } else if (line.startsWith("## ")) { closeList(); html += `<h2>${inlineMarkdown(line.slice(3))}</h2>`; } else if (line.startsWith("### ")) { closeList(); html += `<h3>${inlineMarkdown(line.slice(4))}</h3>`; } else if (line.startsWith("- ")) { if (!inList) { html += "<ul>"; inList = true; } html += `<li>${inlineMarkdown(line.slice(2))}</li>`; } else { closeList(); html += `<p>${inlineMarkdown(line)}</p>`; } } closeList(); return html; }
function formatApiError(payload) {
  if (!payload) return "An unknown error occurred.";
  if (payload.detail && Array.isArray(payload.detail)) {
    const lines = payload.detail.map((item) => {
      const path = Array.isArray(item.loc) ? item.loc.slice(1).join(" → ") : "field";
      return `- ${path || "field"}: ${item.msg}`;
    });
    return `Please fix the following and try again:\n${lines.join("\n")}`;
  }
  return payload.message || payload.detail || "Request failed. Please verify date, time, timezone, and coordinates.";
}
function showError(message) { preview.innerHTML = `<div class="error">${escapeHtml(message)}</div>`; markdown.textContent = message; }
function setTab(which) { const showPreview = which === "preview"; preview.classList.toggle("hidden", !showPreview); markdown.classList.toggle("hidden", showPreview); previewTab.classList.toggle("active", showPreview); markdownTab.classList.toggle("active", !showPreview); }
function updateDownload(markdownText) { if (currentDownloadUrl) URL.revokeObjectURL(currentDownloadUrl); const blob = new Blob([markdownText], { type: "text/markdown" }); currentDownloadUrl = URL.createObjectURL(blob); downloadLink.href = currentDownloadUrl; downloadLink.classList.remove("hidden"); }
async function loadPlaces() { try { const response = await fetch("/places"); placePresets = await response.json(); for (const prefix of ["a", "b"]) { const select = form.elements[`${prefix}_place_preset`]; for (const place of placePresets) { const option = document.createElement("option"); option.value = place.id; option.textContent = place.label; select.appendChild(option); } } const raw = localStorage.getItem(draftKey); setForm(raw ? JSON.parse(raw) : sample); } catch (error) { statusEl.textContent = "Place presets unavailable; manual coordinates still work."; } }
async function loadProviderStatus() { try { const response = await fetch("/geocoding/status"); const payload = await response.json(); providerStatus.textContent = payload.message; providerStatus.className = payload.provider_configured ? "notice" : "small-note"; } catch (error) { providerStatus.textContent = "Geocoding status unavailable; presets/manual coordinates still work."; providerStatus.className = "small-note"; } }

form.addEventListener("submit", async (event) => { event.preventDefault(); statusEl.textContent = "Generating…"; generateButton.disabled = true; try { const response = await fetch("/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payloadFromForm()) }); const data = await response.json(); if (!response.ok) { showError(formatApiError(data)); statusEl.textContent = "Please fix form errors."; return; } currentMarkdown = data.markdown; markdown.textContent = currentMarkdown; preview.innerHTML = markdownToHtml(currentMarkdown); updateDownload(currentMarkdown); saveDraft(); setTab("preview"); statusEl.textContent = "Report generated and draft saved."; } catch (error) { showError("Report generation failed. Please try again."); statusEl.textContent = "Network or server error."; } finally { generateButton.disabled = false; } });
document.getElementById("sample").addEventListener("click", () => { setForm(sample); applyPreset("a", sample.a_place_preset); applyPreset("b", sample.b_place_preset); statusEl.textContent = "Base sample restored."; });
document.getElementById("relationship_sample").addEventListener("change", (event) => { const selected = relationshipSamples[event.target.value]; if (!selected) return; setForm({ ...formValues(), ...selected }); statusEl.textContent = "Sample context applied. Click Generate when ready."; });
document.getElementById("save").addEventListener("click", saveDraft); document.getElementById("restore").addEventListener("click", restoreDraft);
document.getElementById("copy").addEventListener("click", async () => { if (!currentMarkdown) { statusEl.textContent = "No report to copy yet."; return; } await navigator.clipboard.writeText(currentMarkdown); statusEl.textContent = "Markdown copied."; });
previewTab.addEventListener("click", () => setTab("preview")); markdownTab.addEventListener("click", () => setTab("markdown"));
form.elements.a_time_known.addEventListener("change", () => updateTimeKnown("a")); form.elements.b_time_known.addEventListener("change", () => updateTimeKnown("b"));
form.elements.a_place_preset.addEventListener("change", (event) => applyPreset("a", event.target.value)); form.elements.b_place_preset.addEventListener("change", (event) => applyPreset("b", event.target.value));
form.elements.a_place_result.addEventListener("change", (event) => { const place = searchResults.a[Number(event.target.value)]; if (place) applyPlace("a", place); });
form.elements.b_place_result.addEventListener("change", (event) => { const place = searchResults.b[Number(event.target.value)]; if (place) applyPlace("b", place); });
document.getElementById("a_search_button").addEventListener("click", () => searchPlace("a")); document.getElementById("b_search_button").addEventListener("click", () => searchPlace("b"));
setForm(sample); loadProviderStatus(); loadPlaces();
