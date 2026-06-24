const form = document.getElementById("relationship-form");
const statusEl = document.getElementById("status");
const preview = document.getElementById("preview");
const markdown = document.getElementById("markdown");
const markdownTab = document.getElementById("markdown-tab");
const generateButton = document.getElementById("generate");
const saveRelationshipButton = document.getElementById("save_relationship");
const regenerateRelationshipButton = document.getElementById("regenerate_relationship");
const deleteRelationshipButton = document.getElementById("delete_relationship");
const newRelationshipButton = document.getElementById("new_relationship");
const newRelationshipTopButton = document.getElementById("new_relationship_top");
const relationshipModeTitle = document.getElementById("relationship_mode_title");
const relationshipModeDetail = document.getElementById("relationship_mode_detail");
const providerStatus = document.getElementById("provider-status");
const reportStatusEl = document.getElementById("report_status");
const downloadLink = document.getElementById("download");
const diagnosticsPanel = document.getElementById("diagnostics-panel");
const diagnosticsEl = document.getElementById("diagnostics");
const feedbackPanel = document.getElementById("feedback-panel");
const feedbackForm = document.getElementById("feedback-form");
const feedbackStatus = document.getElementById("feedback_status");
const feedbackSummaryPanel = document.getElementById("feedback-summary-panel");
const feedbackSummary = document.getElementById("feedback-summary");
const refreshConstellationButton = document.getElementById("refresh_constellation");
const constellationEl = document.getElementById("constellation");
let currentMarkdown = "";
let currentDownloadUrl = "";
let currentSavedRelationship = null;
let currentSynthesisPacket = null;
let currentDynamicDetails = [];
let currentDiagnostics = null;
let currentSavedReportId = null;
let enhancementRequestId = 0;
let searchResults = { a: [], b: [] };
let placeSelections = { a: null, b: null };
let shouldScrollToReport = false;
let currentThemeIndex = [];
let savedBirthProfiles = [];
let activeThemeFilter = null;
let currentReportTitle = "Latest Relationship Map";
const draftKey = "constellation.relationshipForm.v1";

// Relationship type config for type grid (PR 3)
const RELATIONSHIP_TYPES = {
  romantic: { label: "Romantic", color: "#C47A8A" },
  long_term_partner: { label: "Committed", color: "#A86080" },
  dating_exploring: { label: "Dating", color: "#C47A8A" },
  ex: { label: "Ex", color: "#505A72" },
  unresolved_connection: { label: "Unresolved", color: "#505A72" },
  friend: { label: "Friendship", color: "#6A9BC4" },
  collaborator: { label: "Work", color: "#7A8B9B" },
  parent: { label: "Family", color: "#5AADA0" },
  sibling: { label: "Family", color: "#5AADA0" },
  child: { label: "Family", color: "#5AADA0" },
  family_other: { label: "Family", color: "#5AADA0" },
  admired_figure: { label: "Mentor", color: "#7A8B9B" },
};
const constellationPatternsEmptyState = "Your constellation is still forming. Save relationships to begin seeing recurring patterns across your field.";
const noReportsForSavedRelationshipsEmptyState = "Generate maps for your saved relationships to begin seeing what repeats.";
const oneMapActiveEmptyState = "One map is active. Add more saved maps to see broader patterns in your constellation.";
const noConstellationPatternsEmptyState = "Patterns will appear here once you’ve generated and saved more maps.";
const categoryDescriptions = {
  emotional_recognition: "Where someone feels familiar, legible, or emotionally known.",
  erotic_charge: "Where attraction, pursuit, chemistry, or creative heat concentrates.",
  stability_container: "Where commitment, time, limits, or responsibility shape the bond.",
  trust_depth: "Where vulnerability, honesty, and deeper psychological contact are emphasized.",
  communication_heat: "Where language, timing, nervous systems, or conflict patterns matter.",
  private_roots: "Where home, family patterns, memory, or attachment history are activated.",
  devotion_contract: "Where loyalty, vows, care, or relational obligation become central.",
  projection_mirror: "Where the other person reflects disowned or amplified parts of the self.",
  repair_capacity: "Where the bond shows pathways for working through friction.",
};
const diagnosticsEnabled = new URLSearchParams(window.location.search).get("include_diagnostics") === "true" || localStorage.getItem("constellation.includeDiagnostics") === "true";

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
  syncPlaceSelectionFromForm("a");
  syncPlaceSelectionFromForm("b");
  syncTypeGrid(values.relationship_type || fieldValue("relationship_type", "romantic"));
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
  const note = document.getElementById(`${prefix}_time_note`);
  if (note) note.classList.toggle("visible", !known);
}

// PR 3: Type grid sync
function syncTypeGrid(type) {
  for (const card of document.querySelectorAll(".type-card")) {
    card.classList.toggle("selected", card.dataset.type === type);
  }
}

// PR 4: Vault picker rendering
function renderVaultItem(prefix, profile) {
  const item = document.createElement("div");
  item.className = "vault-item";
  item.innerHTML = `<div><div class="vault-item-name">${escapeHtml(profile.display_name || "Unknown")}</div><div class="vault-item-meta">${escapeHtml(profile.birth_date || "")}${profile.birthplace_label ? " · " + escapeHtml(profile.birthplace_label) : ""}</div></div>`;
  item.addEventListener("click", () => {
    setForm({ ...formValues(), ...birthProfileToFormValues(prefix, profile) });
    statusEl.textContent = `${escapeHtml(profile.display_name || "Profile")} filled in.`;
  });
  return item;
}

function renderVaultPicker(prefix, profiles) {
  const section = document.getElementById(`${prefix}_vault_section`);
  const list = document.getElementById(`${prefix}_vault_list`);
  if (!section || !list) return;
  if (!profiles.length) { section.classList.add("hidden"); return; }
  list.innerHTML = "";
  for (const profile of profiles.slice(0, 6)) {
    list.appendChild(renderVaultItem(prefix, profile));
  }
  section.classList.remove("hidden");
}

async function loadBirthProfiles() {
  try {
    const response = await fetch("/birth-profiles");
    if (!response.ok) return;
    savedBirthProfiles = await response.json();
    renderVaultPicker("a", savedBirthProfiles);
    renderVaultPicker("b", savedBirthProfiles);
  } catch { /* vault unavailable — silent */ }
}

function setPlaceWarning(prefix, message) {
  const warning = document.getElementById(`${prefix}_place_warning`);
  if (!warning) return;
  warning.textContent = message;
  warning.classList.toggle("hidden", !message);
}

function clearPlaceSelection(prefix) {
  const query = fieldValue(`${prefix}_place_query`).trim();
  form.elements[`${prefix}_latitude`].value = "";
  form.elements[`${prefix}_longitude`].value = "";
  form.elements[`${prefix}_timezone`].value = "";
  const select = form.elements[`${prefix}_place_result`];
  const label = document.getElementById(`${prefix}_place_result_label`);
  if (select) select.innerHTML = '<option value="">Search to see options</option>';
  if (label) label.classList.add("hidden");
  searchResults[prefix] = [];
  placeSelections[prefix] = null;
  setPlaceWarning(prefix, query ? "Birthplace changed. Search again and select a result before generating." : "");
}

function applyPlace(prefix, place) {
  form.elements[`${prefix}_latitude`].value = Number(place.latitude).toFixed(4);
  form.elements[`${prefix}_longitude`].value = Number(place.longitude).toFixed(4);
  form.elements[`${prefix}_timezone`].value = place.timezone;
  form.elements[`${prefix}_place_query`].value = place.label;
  placeSelections[prefix] = { label: place.label, latitude: Number(place.latitude), longitude: Number(place.longitude), timezone: place.timezone };
  setPlaceWarning(prefix, "");
}

function syncPlaceSelectionFromForm(prefix) {
  const label = fieldValue(`${prefix}_place_query`).trim();
  if (label && hasCompletePlaceDetails(prefix)) {
    placeSelections[prefix] = {
      label,
      latitude: Number(fieldValue(`${prefix}_latitude`)),
      longitude: Number(fieldValue(`${prefix}_longitude`)),
      timezone: fieldValue(`${prefix}_timezone`),
    };
    setPlaceWarning(prefix, "");
    return;
  }
  placeSelections[prefix] = null;
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

// ── PR 2: Structured report renderer ─────────────────────────────────────────

function signalDots(priority) {
  const filled = priority >= 80 ? 5 : priority >= 65 ? 4 : priority >= 50 ? 3 : priority >= 35 ? 2 : 1;
  return Array.from({ length: 5 }, (_, i) =>
    `<span class="signal-dot${i < filled ? " filled" : ""}"></span>`
  ).join("");
}

function frameTagFromDetail(detail) {
  const tags = detail.theme_tags || [];
  if (tags.includes("repair-practice")) return "Where repair opens";
  if (tags.includes("conflict-friction")) return "What's harder";
  if (tags.includes("eros-attraction")) return "The attraction";
  if (tags.includes("trust-vulnerability")) return "Where it deepens";
  if (tags.includes("communication")) return "How you talk";
  if (tags.includes("romance-play")) return "What feels playful";
  if (tags.includes("partnership-commitment")) return "The structure";
  if (tags.includes("unconscious-spiritual")) return "The undercurrent";
  if (tags.includes("home-roots")) return "What's underneath";
  if (tags.includes("composite-field")) return "In the shared field";
  if (tags.includes("emotional-dynamics")) return "What's familiar";
  if (tags.includes("chart-check")) return "Chart note";
  return "What's present";
}

function patternCardHtml(detail) {
  const frame = frameTagFromDetail(detail);
  const priority = detail.priority || 0;
  const tags = detail.theme_tags || [];
  const isHard = tags.includes("conflict-friction") && !tags.includes("repair-practice");
  const themeAttrs = tags.length ? `data-themes="${tags.join(",")}"` : "";
  const cardClass = isHard ? "pattern-card-beta pattern-card-hard" : "pattern-card-beta";
  const factors = (detail.technical_factors || []).map((item) => `<li>${inlineMarkdown(item)}</li>`).join("");
  const related = (detail.related_dynamics || []).slice(0, 4).map((item) => `<li>${inlineMarkdown(item)}</li>`).join("");
  const factorsBlock = factors ? `<h4>Technical factors</h4><ul>${factors}</ul>` : "";
  const relatedBlock = related ? `<h4>Related dynamics</h4><ul>${related}</ul>` : "";
  const repair = detail.repair_prompt ? `<p class="repair-prompt"><strong>Repair:</strong> ${inlineMarkdown(detail.repair_prompt)}</p>` : "";
  const detailId = detail.id ? ` id="${escapeHtml(detail.id)}"` : "";
  return `
    <article class="${cardClass}"${detailId} ${themeAttrs}>
      <div class="pattern-card-header">
        <span class="frame-tag">${escapeHtml(frame)}</span>
        <span class="signal-dots" aria-label="Signal strength ${Math.round(priority / 20)} of 5">${signalDots(priority)}</span>
      </div>
      <h3 class="pattern-card-title">${inlineMarkdown(detail.title || "")}</h3>
      <p class="pattern-card-summary">${inlineMarkdown(detail.summary || "")}</p>
      <details class="read-more-detail">
        <summary>Read more</summary>
        <div class="read-more-content">
          <p>${inlineMarkdown(detail.read_more || detail.summary || "")}</p>
          ${factorsBlock}${relatedBlock}${repair}
        </div>
      </details>
    </article>`;
}

function parseReportSections(md) {
  const sections = [];
  let current = null;
  let currentPattern = null;
  for (const rawLine of md.split("\n")) {
    const line = rawLine.trimEnd();
    if (line.startsWith("## ")) {
      if (current) sections.push(current);
      current = { title: line.slice(3), leadLines: [], patterns: [] };
      currentPattern = null;
    } else if (line.startsWith("### ") && current) {
      currentPattern = { title: line.slice(4), lines: [] };
      current.patterns.push(currentPattern);
    } else if (current) {
      if (currentPattern) currentPattern.lines.push(line);
      else current.leadLines.push(line);
    }
  }
  if (current) sections.push(current);
  return sections;
}

function renderReportStructured(md, dynamicDetails = []) {
  const sections = parseReportSections(md);
  const detailsByTitle = new Map((dynamicDetails || []).map((d) => [d.title, d]));
  let html = "";

  for (const section of sections) {
    const lead = section.leadLines.filter((l) => l.trim()).join(" ").trim();
    const patternCards = section.patterns
      .map((p) => {
        const detail = detailsByTitle.get(p.title);
        return detail ? patternCardHtml(detail) : `<h3>${inlineMarkdown(p.title)}</h3>`;
      })
      .join("");

    if (section.title === "Overview") {
      if (lead) {
        const bondLabel = fieldValue("a_name") && fieldValue("b_name")
          ? `${escapeHtml(fieldValue("a_name"))} &amp; ${escapeHtml(fieldValue("b_name"))}`
          : "";
        const eyebrow = bondLabel ? `<div class="bond-eyebrow">${bondLabel}</div>` : "";
        html += `<div class="bond-card">${eyebrow}<p>${inlineMarkdown(lead)}</p></div>`;
      }
      if (patternCards) {
        html += `<div class="pattern-card-list-beta">${patternCards}</div>`;
      }
    } else {
      const isOpen = section.title === "Composite Field" ? " open" : "";
      const sectionLead = lead ? `<p>${inlineMarkdown(lead)}</p>` : "";
      const sectionCards = patternCards ? `<div class="pattern-card-list-beta">${patternCards}</div>` : "";
      html += `<details class="report-section"${isOpen}><summary>${escapeHtml(section.title)}</summary>${sectionLead}${sectionCards}</details>`;
    }
  }
  return html || markdownToHtml(md, dynamicDetails);
}

// PR 6: Theme pills rendering
function renderThemePills(themeIndex) {
  const pillsSection = document.getElementById("theme-pills-section");
  const pillsContainer = document.getElementById("theme-pills");
  if (!pillsSection || !pillsContainer) return;
  const present = themeIndex.filter((t) => t.present);
  if (!present.length) { pillsSection.classList.add("hidden"); return; }

  pillsContainer.innerHTML = "";
  const allBtn = document.createElement("button");
  allBtn.type = "button";
  allBtn.className = "theme-pill active";
  allBtn.textContent = "All";
  allBtn.dataset.theme = "";
  allBtn.addEventListener("click", () => applyThemeFilter(null, themeIndex));
  pillsContainer.appendChild(allBtn);

  const sorted = [...themeIndex].sort((a, b) => {
    const order = { primary: 0, secondary: 1, background: 2, absent: 3 };
    return (order[a.strength] ?? 3) - (order[b.strength] ?? 3);
  });

  for (const theme of sorted) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = theme.present ? "theme-pill" : "theme-pill absent";
    btn.textContent = theme.label;
    btn.dataset.theme = theme.theme;
    if (theme.present) {
      btn.addEventListener("click", () => applyThemeFilter(theme.theme, themeIndex));
    }
    pillsContainer.appendChild(btn);
  }
  pillsSection.classList.remove("hidden");
}

function applyThemeFilter(themeSlug, themeIndex) {
  activeThemeFilter = themeSlug;
  const allCards = document.querySelectorAll(".pattern-card-beta");
  const allPills = document.querySelectorAll(".theme-pill");

  for (const pill of allPills) {
    pill.classList.toggle("active", pill.dataset.theme === (themeSlug || ""));
  }

  if (!themeSlug) {
    for (const card of allCards) card.style.display = "";
    return;
  }

  for (const card of allCards) {
    const tags = (card.dataset.themes || "").split(",").filter(Boolean);
    card.style.display = tags.includes(themeSlug) ? "" : "none";
  }
}

function dynamicDetailHtml(detail) {
  const factors = (detail.technical_factors || []).map((item) => `<li>${inlineMarkdown(item)}</li>`).join("");
  const related = (detail.related_dynamics || []).slice(0, 4).map((item) => `<li>${inlineMarkdown(item)}</li>`).join("");
  const factorsBlock = factors ? `<h4>Technical factors</h4><ul>${factors}</ul>` : "";
  const relatedBlock = related ? `<h4>Related dynamics</h4><ul>${related}</ul>` : "";
  const repair = detail.repair_prompt ? `<p><strong>Repair prompt:</strong> ${inlineMarkdown(detail.repair_prompt)}</p>` : "";
  return `<details class="dynamic-detail"><summary>Read more</summary><p>${inlineMarkdown(detail.read_more || detail.summary || "")}</p>${factorsBlock}${relatedBlock}${repair}</details>`;
}

function markdownToHtml(md, dynamicDetails = []) {
  const lines = md.split("\n");
  let html = "";
  let inList = false;
  let inDetails = false;
  const defaultOpenSections = new Set(["Overview", "Composite Field"]);
  const detailsByTitle = new Map((dynamicDetails || []).map((detail) => [detail.title, detail]));
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
      const heading = line.slice(4);
      html += `<h3>${inlineMarkdown(heading)}</h3>`;
      const detail = detailsByTitle.get(heading);
      if (detail) html += dynamicDetailHtml(detail);
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


function renderDiagnostics(diagnostics) {
  currentDiagnostics = diagnostics || null;
  if (!diagnosticsPanel || !diagnosticsEl) return;
  diagnosticsPanel.classList.toggle("hidden", !diagnosticsEnabled || !currentDiagnostics);
  if (!diagnosticsEnabled || !currentDiagnostics) {
    diagnosticsEl.textContent = "Diagnostics are disabled.";
    return;
  }
  const compact = {
    lead_pattern: currentDiagnostics.selected_lead_pattern,
    top_ranked_patterns: currentDiagnostics.top_ranked_patterns,
    included_asteroids: currentDiagnostics.asteroid_policy_summary?.included_asteroid_patterns || [],
    suppressed_asteroids: currentDiagnostics.asteroid_policy_summary?.suppressed_asteroid_patterns || [],
    advanced_asteroids_suppressed: currentDiagnostics.asteroid_policy_summary?.advanced_asteroids_suppressed || [],
    persisted_motifs: currentDiagnostics.motif_persistence_summary || [],
    house_system: currentDiagnostics.house_system,
    chart_sanity: {
      person_a: currentDiagnostics.person_a_chart_sanity,
      person_b: currentDiagnostics.person_b_chart_sanity,
    },
  };
  diagnosticsEl.textContent = JSON.stringify(compact, null, 2);
}

function resetFeedbackState() {
  if (feedbackPanel) feedbackPanel.classList.add("hidden");
  if (feedbackSummaryPanel) feedbackSummaryPanel.classList.add("hidden");
  if (feedbackSummary) feedbackSummary.textContent = "No tester feedback yet.";
  if (feedbackStatus) feedbackStatus.textContent = "";
  feedbackForm?.reset();
}

function showFeedbackForCurrentReport() {
  if (!feedbackPanel) return;
  feedbackPanel.classList.remove("hidden");
  if (feedbackStatus) feedbackStatus.textContent = "";
  feedbackForm?.reset();
  void loadFeedbackSummary();
}

function optionalInteger(value) {
  return value ? Number.parseInt(value, 10) : null;
}

function feedbackFormPayload() {
  const data = new FormData(feedbackForm);
  return {
    relationship_id: currentSavedRelationship?.id || null,
    saved_report_id: currentSavedReportId,
    usefulness_rating: optionalInteger(data.get("usefulness_rating")),
    accuracy_rating: optionalInteger(data.get("accuracy_rating")),
    clarity_rating: optionalInteger(data.get("clarity_rating")),
    felt_seen_rating: optionalInteger(data.get("felt_seen_rating")),
    too_long: data.has("too_long"),
    too_intense: data.has("too_intense"),
    too_technical: data.has("too_technical"),
    what_landed: data.get("what_landed") || null,
    what_felt_off: data.get("what_felt_off") || null,
    central_theme_feedback: data.get("central_theme_feedback") || null,
    freeform_comment: data.get("freeform_comment") || null,
    tester_label: data.get("tester_label") || null,
    report_version_metadata: {
      source: "relationship_map_ui",
      has_synthesis_packet: Boolean(currentSynthesisPacket),
      has_diagnostics: Boolean(currentDiagnostics),
    },
  };
}

async function submitFeedback(event) {
  event.preventDefault();
  if (!feedbackForm) return;
  if (feedbackStatus) feedbackStatus.textContent = "Sending feedback…";
  const response = await fetch("/report-feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(feedbackFormPayload()),
  });
  const payload = await response.json();
  if (!response.ok) {
    if (feedbackStatus) feedbackStatus.textContent = payload.detail || "Could not save feedback.";
    return;
  }
  if (feedbackStatus) feedbackStatus.textContent = "Thank you — feedback saved.";
  await loadFeedbackSummary();
}

async function loadFeedbackSummary() {
  if (!currentSavedRelationship || !feedbackSummaryPanel || !feedbackSummary) return;
  const response = await fetch(`/saved-relationships/${currentSavedRelationship.id}/feedback`);
  if (!response.ok) return;
  const payload = await response.json();
  feedbackSummaryPanel.classList.toggle("hidden", payload.response_count === 0);
  if (!payload.response_count) {
    feedbackSummary.textContent = "No tester feedback yet.";
    return;
  }
  const clarity = payload.average_clarity ? ` Average clarity: ${payload.average_clarity}.` : "";
  const recent = payload.most_recent ? ` Most recent: “${payload.most_recent}”` : "";
  feedbackSummary.textContent = `${payload.response_count} response${payload.response_count === 1 ? "" : "s"}.${clarity}${recent}`;
}

function setTab(which) {
  const showMarkdown = which === "markdown";
  preview.classList.remove("hidden");
  markdown.classList.toggle("hidden", !showMarkdown);
  markdownTab.classList.toggle("active", showMarkdown);
  markdownTab.textContent = showMarkdown ? "Hide Markdown" : "View Markdown";
}

function setReportMarkdown(markdownText, dynamicDetails = currentDynamicDetails) {
  currentMarkdown = markdownText;
  currentDynamicDetails = dynamicDetails || [];
  markdown.textContent = currentMarkdown;
  preview.innerHTML = currentDynamicDetails.length
    ? renderReportStructured(currentMarkdown, currentDynamicDetails)
    : markdownToHtml(currentMarkdown, currentDynamicDetails);
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
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Could not save relationship");
  currentSavedRelationship = payload;
  updateRelationshipMode();
  return currentSavedRelationship;
}

function updateSavedRelationshipPayload() {
  return { person_a: person("a"), person_b: person("b"), ...buildContext() };
}

async function updateSavedRelationship() {
  if (!currentSavedRelationship) return createSavedRelationship();
  const response = await fetch(`/saved-relationships/${currentSavedRelationship.id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updateSavedRelationshipPayload()),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Could not update relationship");
  currentSavedRelationship = payload;
  updateRelationshipMode();
  return currentSavedRelationship;
}

function clearReportState() {
  enhancementRequestId += 1;
  currentMarkdown = "";
  currentSynthesisPacket = null;
  currentDynamicDetails = [];
  currentThemeIndex = [];
  activeThemeFilter = null;
  currentSavedReportId = null;
  document.getElementById("theme-pills-section")?.classList.add("hidden");
  currentReportTitle = "Latest Relationship Map";
  const reportHeading = document.querySelector("#report-section h2");
  if (reportHeading) reportHeading.textContent = currentReportTitle;
  renderDiagnostics(null);
  resetFeedbackState();
  markdown.textContent = "Generate a relationship map to see Markdown.";
  preview.innerHTML = `<div class="empty-state"><strong>Start with two people to generate a Relationship Map.</strong><p>The map will show central themes, friction points, repair paths, and the larger field between the charts.</p></div>`;
  setReportStatus("");
  if (currentDownloadUrl) URL.revokeObjectURL(currentDownloadUrl);
  currentDownloadUrl = "";
  downloadLink.removeAttribute("href");
  downloadLink.classList.add("hidden");
}

function updateRelationshipMode() {
  const editing = Boolean(currentSavedRelationship);
  relationshipModeTitle.textContent = editing ? "Editing saved relationship" : "New Relationship";
  relationshipModeDetail.textContent = editing ? "Update the saved birth data or context, then regenerate the map when ready." : "Start a clean relationship map.";
  generateButton.textContent = editing ? "Update and Regenerate Map" : "Generate Relationship Map";
  saveRelationshipButton.textContent = editing ? "Update Relationship" : "Save Relationship";
  regenerateRelationshipButton.classList.toggle("hidden", !editing);
  deleteRelationshipButton.classList.toggle("hidden", !editing);
}

function resetPlaceSearchState(prefix) {
  const select = form.elements[`${prefix}_place_result`];
  const label = document.getElementById(`${prefix}_place_result_label`);
  if (select) select.innerHTML = '<option value="">Search to see options</option>';
  if (label) label.classList.add("hidden");
  searchResults[prefix] = [];
  placeSelections[prefix] = null;
  setPlaceWarning(prefix, "");
}

function startNewRelationship() {
  currentSavedRelationship = null;
  setForm(defaultState);
  resetPlaceSearchState("a");
  resetPlaceSearchState("b");
  clearReportState();
  updateRelationshipMode();
  statusEl.textContent = "New Relationship ready.";
  document.getElementById("you-section")?.scrollIntoView({ behavior: "smooth", block: "start" });
  form.elements.a_name?.focus();
}

function setReportStatus(message) {
  if (reportStatusEl) reportStatusEl.textContent = message;
}

async function generateSavedReport(relationshipId) {
  setReportStatus("Preparing your map…");
  const diagnosticsQuery = diagnosticsEnabled ? "?include_diagnostics=true" : "";
  const response = await fetch(`/saved-relationships/${relationshipId}/report${diagnosticsQuery}`, { method: "POST" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Could not generate saved report");
  const standardMarkdown = payload.markdown;
  currentSavedReportId = payload.id || null;
  currentSynthesisPacket = payload.synthesis_packet || null;
  currentDynamicDetails = payload.dynamic_details || [];
  currentThemeIndex = payload.theme_index || [];
  renderDiagnostics(payload.diagnostics || null);
  setReportMarkdown(standardMarkdown);
  renderThemePills(currentThemeIndex);
  const nameA = fieldValue("a_name");
  const nameB = fieldValue("b_name");
  if (nameA && nameB) {
    currentReportTitle = `${nameA} & ${nameB}`;
    const reportHeading = document.querySelector("#report-section h2");
    if (reportHeading) reportHeading.textContent = currentReportTitle;
  }
  setTab("preview");
  setReportStatus("Relationship Map ready.");
  showFeedbackForCurrentReport();
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
    setReportMarkdown(payload.markdown, currentDynamicDetails);
    setTab("preview");
    setReportStatus("Relationship Map ready.");
  } catch (error) {
    if (requestId !== enhancementRequestId) return;
    setReportMarkdown(standardMarkdown, currentDynamicDetails);
    setReportStatus("Relationship Map ready.");
  }
}

function birthProfileToFormValues(prefix, profile) {
  const values = {};
  values[`${prefix}_name`] = profile.display_name || "";
  values[`${prefix}_date`] = profile.birth_date || "";
  values[`${prefix}_time`] = profile.birth_time ? profile.birth_time.slice(0, 5) : "";
  values[`${prefix}_time_known`] = String(profile.time_known !== false);
  values[`${prefix}_place_query`] = profile.birthplace_label || "";
  values[`${prefix}_latitude`] = profile.latitude ?? "";
  values[`${prefix}_longitude`] = profile.longitude ?? "";
  values[`${prefix}_timezone`] = profile.timezone || "";
  return values;
}

async function openSavedRelationship(relationshipId) {
  statusEl.textContent = "Opening saved relationship…";
  const relationshipResponse = await fetch(`/saved-relationships/${relationshipId}`);
  const relationship = await relationshipResponse.json();
  if (!relationshipResponse.ok) throw new Error(relationship.detail || "Could not open saved relationship");
  const [personAResponse, personBResponse] = await Promise.all([
    fetch(`/birth-profiles/${relationship.person_a_id}`),
    fetch(`/birth-profiles/${relationship.person_b_id}`),
  ]);
  const [personA, personB] = await Promise.all([personAResponse.json(), personBResponse.json()]);
  if (!personAResponse.ok || !personBResponse.ok) throw new Error("Could not load saved birth data");
  currentSavedRelationship = relationship;
  setForm({
    ...defaultState,
    ...birthProfileToFormValues("a", personA),
    ...birthProfileToFormValues("b", personB),
    relationship_type: relationship.relationship_type || "romantic",
    user_question: relationship.user_question || "",
    origin_story: relationship.origin_story || "",
    house_system: relationship.house_system || "placidus",
  });
  resetPlaceSearchState("a");
  resetPlaceSearchState("b");
  syncPlaceSelectionFromForm("a");
  syncPlaceSelectionFromForm("b");
  clearReportState();
  updateRelationshipMode();
  statusEl.textContent = "Editing saved relationship.";
  document.getElementById("relationship-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function deleteCurrentRelationship() {
  if (!currentSavedRelationship) return;
  if (!window.confirm("Delete this saved relationship? This removes its saved maps from your constellation.")) return;
  const deletedId = currentSavedRelationship.id;
  const response = await fetch(`/saved-relationships/${deletedId}`, { method: "DELETE" });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Could not delete relationship");
  startNewRelationship();
  await loadConstellation();
  statusEl.textContent = "Relationship deleted. Your constellation is updated.";
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

function categoryDescription(category, fallback = "") {
  return fallback || categoryDescriptions[category] || "A recurring relationship motif that may become clearer as more maps are generated.";
}

function categoryLabel(motif) {
  return motif.category_label || motif.label || (motif.category || "motif").replaceAll("_", " ");
}

function savedMapCountLabel(count) {
  return count === 1 ? "Appears in 1 saved map" : `Appears in ${count} saved maps`;
}

function renderEvidence(evidence) {
  const snippets = Array.isArray(evidence) ? evidence.filter(Boolean).slice(0, 2) : (evidence ? [evidence] : []);
  if (!snippets.length) return "";
  return `<div class="motif-evidence" aria-label="Evidence snippets">${snippets.map((snippet) => `<p>${escapeHtml(snippet)}</p>`).join("")}</div>`;
}

function renderRecurringMotifCard(motif) {
  const people = (motif.people || []).filter(Boolean);
  const category = motif.category || motif.id || "motif";
  const description = categoryDescription(category, motif.description);
  return `
    <article class="motif-card">
      <div class="motif-card-header">
        <div>
          <h4>${escapeHtml(motif.label)}</h4>
          <p class="motif-category">${escapeHtml(categoryLabel(motif))}</p>
        </div>
        <span class="motif-count">${escapeHtml(String(motif.count))}</span>
      </div>
      <p class="motif-map-count">${escapeHtml(savedMapCountLabel(motif.count))}</p>
      <p class="motif-people"><span>Appears in:</span> ${escapeHtml(people.join(" · ") || "Saved maps")}</p>
      <p>${escapeHtml(description)}</p>
      ${renderEvidence(motif.evidence)}
    </article>`;
}

function renderCategoryChips(categories) {
  if (!categories || !categories.length) {
    return `<p class="small-note">${noReportsForSavedRelationshipsEmptyState}</p>`;
  }
  return `<div class="category-chip-list">${categories.map((item) => `
    <div class="category-chip">
      <strong>${escapeHtml(item.label)}</strong>
      <span>${escapeHtml(categoryDescription(item.category, item.description))}</span>
    </div>`).join("")}</div>`;
}

function renderRelationshipMotifGroups(groups) {
  if (!groups || !groups.length) return "";
  return `
    <section class="relationship-motif-section">
      <h3>Relationship-specific motifs</h3>
      <p class="small-note">A smaller view of motifs inside individual maps. These are not ordered as better or worse.</p>
      <div class="relationship-motif-list">${groups.map((group) => `
        <div class="relationship-motif-group">
          <h4>${escapeHtml(group.label)}</h4>
          <ul>${(group.motifs || []).map((motif) => `
            <li>
              <strong>${escapeHtml(motif.title)}</strong>
              <span>${escapeHtml(motif.category_label || categoryLabel(motif))}</span>
            </li>`).join("")}</ul>
        </div>`).join("")}</div>
    </section>`;
}

function renderConstellationPatterns(summary) {
  if (!summary) {
    return `<section class="pattern-summary"><h3>Constellation Patterns</h3><p class="small-note">Pattern synthesis is unavailable right now. Saved relationship snapshots are still shown below.</p></section>`;
  }

  if (!summary.relationship_count) {
    return `<section class="pattern-summary constellation-empty"><h3>Constellation Patterns</h3><h4>Your constellation is still forming.</h4><p class="small-note">${constellationPatternsEmptyState}</p><p class="small-note">${noConstellationPatternsEmptyState}</p></section>`;
  }

  if (!summary.has_enough_data) {
    return `<section class="pattern-summary constellation-empty"><h3>Constellation Patterns</h3><h4>Still forming</h4><p class="small-note">${oneMapActiveEmptyState}</p><p class="small-note">${noConstellationPatternsEmptyState}</p></section>`;
  }

  const hasMotifs = (summary.recurring_motifs && summary.recurring_motifs.length) || (summary.top_motif_categories && summary.top_motif_categories.length);
  const motifCards = summary.recurring_motifs && summary.recurring_motifs.length
    ? summary.recurring_motifs.map(renderRecurringMotifCard).join("")
    : `<p class="small-note">${noReportsForSavedRelationshipsEmptyState}</p>`;
  const themeLine = summary.known_theme_counts.length
    ? `<p class="small-note">Recurring named themes: ${escapeHtml(summary.known_theme_counts.map((item) => item.theme).join(", "))}.</p>`
    : '<p class="small-note">No recurring named themes have been saved yet.</p>';

  return `
    <section class="pattern-summary">
      <div class="pattern-kicker">Constellation Patterns</div>
      <h3>What keeps showing up in your relational field?</h3>
      <p class="small-note">${summary.relationship_count} saved relationships analyzed.</p>

      <section class="pattern-section">
        <h3>Currently emerging</h3>
        <p>${escapeHtml(summary.plain_language_summary || "Your saved maps are beginning to form a constellation.")}</p>
        ${renderCategoryChips(summary.top_motif_categories)}
      </section>

      <section class="pattern-section">
        <h3>Recurring motifs</h3>
        <div class="motif-card-list">${motifCards}</div>
      </section>

      ${renderRelationshipMotifGroups(summary.relationship_motifs)}

      <section class="pattern-section pattern-grid">
        <div>
          <h3>Relationship types</h3>
          ${renderCountList(summary.relationship_type_counts, "label")}
        </div>
        <div>
          <h3>Recurring themes</h3>
          ${themeLine}
        </div>
      </section>

      <section class="pattern-section still-forming">
        <h3>Still forming</h3>
        <p class="small-note">${hasMotifs ? "Generate more Relationship Maps to clarify what repeats." : noReportsForSavedRelationshipsEmptyState}</p>
      </section>
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
    constellationEl.innerHTML = `${renderConstellationPatterns(patternSummary)}<p class="small-note">${constellationPatternsEmptyState}</p>`;
    return;
  }
  constellationEl.innerHTML = renderConstellationPatterns(patternSummary);
  for (const rel of relationships.slice(0, 12)) {
    const node = document.createElement("div");
    node.className = "constellation-node";
    node.innerHTML = `<strong>${escapeHtml(relationshipLabel(rel))}</strong><div class="small-note">${new Date(rel.created_at).toLocaleString()}</div><div class="small-note">themes: ${escapeHtml(rel.known_themes.join(", ") || "none")}</div>`;
    const actions = document.createElement("div");
    actions.className = "actions";
    const openAction = document.createElement("button");
    openAction.type = "button";
    openAction.className = "secondary";
    openAction.textContent = "View Latest Map";
    openAction.addEventListener("click", async () => {
      try {
        await openSavedRelationship(rel.id);
      } catch (error) {
        statusEl.textContent = error.message;
      }
    });
    const action = document.createElement("button");
    action.type = "button";
    action.className = "secondary";
    action.textContent = "Regenerate Map";
    action.addEventListener("click", async () => {
      statusEl.textContent = "Regenerating saved relationship map…";
      shouldScrollToReport = true;
      try {
        currentSavedRelationship = rel;
        updateRelationshipMode();
        await generateSavedReport(rel.id);
        await loadConstellation();
        statusEl.textContent = "Saved relationship map regenerated.";
      } catch (error) {
        statusEl.textContent = error.message;
      }
    });
    actions.appendChild(openAction);
    actions.appendChild(action);
    node.appendChild(actions);
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
  statusEl.textContent = currentSavedRelationship ? "Updating relationship and regenerating map…" : "Saving relationship and generating map…";
  generateButton.disabled = true;
  try {
    const relationship = currentSavedRelationship ? await updateSavedRelationship() : await createSavedRelationship();
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

feedbackForm?.addEventListener("submit", submitFeedback);
refreshConstellationButton.addEventListener("click", loadConstellation);
newRelationshipButton.addEventListener("click", startNewRelationship);
newRelationshipTopButton.addEventListener("click", startNewRelationship);
saveRelationshipButton.addEventListener("click", async () => {
  saveRelationshipButton.disabled = true;
  const wasEditing = Boolean(currentSavedRelationship);
  statusEl.textContent = wasEditing ? "Updating relationship…" : "Saving relationship…";
  try {
    await updateSavedRelationship();
    await loadConstellation();
    saveDraft();
    statusEl.textContent = wasEditing ? "Relationship updated." : "Relationship saved.";
  } catch (error) {
    statusEl.textContent = error.message || "Save failed";
  } finally {
    saveRelationshipButton.disabled = false;
  }
});
regenerateRelationshipButton.addEventListener("click", async () => {
  if (!currentSavedRelationship) return;
  regenerateRelationshipButton.disabled = true;
  shouldScrollToReport = true;
  statusEl.textContent = "Regenerating map from latest saved data…";
  try {
    const relationship = await updateSavedRelationship();
    await generateSavedReport(relationship.id);
    await loadConstellation();
    statusEl.textContent = "Relationship map regenerated.";
  } catch (error) {
    statusEl.textContent = error.message || "Regeneration failed";
  } finally {
    regenerateRelationshipButton.disabled = false;
  }
});
deleteRelationshipButton.addEventListener("click", async () => {
  deleteRelationshipButton.disabled = true;
  try {
    await deleteCurrentRelationship();
  } catch (error) {
    statusEl.textContent = error.message || "Delete failed";
  } finally {
    deleteRelationshipButton.disabled = false;
  }
});
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

// PR 3: Type card selection
for (const card of document.querySelectorAll(".type-card")) {
  card.addEventListener("click", () => {
    const type = card.dataset.type;
    const select = document.getElementById("relationship_type_select");
    if (select) select.value = type;
    syncTypeGrid(type);
  });
}

setForm(defaultState);
updateRelationshipMode();
loadProviderStatus();
loadPlaces().catch(() => {});
loadConstellation().catch(() => { constellationEl.innerHTML = "Constellation view unavailable."; });
loadBirthProfiles().catch(() => {});
