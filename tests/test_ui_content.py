from pathlib import Path


def test_relationship_type_options_include_ex_and_unresolved_separately():
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()
    assert ">Ex<" in html
    assert "Unresolved connection" in html
    assert "Ex / unresolved" not in html


def test_metadata_not_prominent_report_section_label():
    source = Path("packages/astro-core/constellation_core/report.py").read_text()
    assert "Report Metadata" not in source
    assert "Optional Technical Details" not in source


def test_homepage_hero_subtitle_updated_without_repeated_observatory():
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()
    assert "Your relationship observatory" in html
    assert (
        "Map the people who shape your life through astrology, timing, and relational patterning."
        in html
    )
    assert "An observatory for all your human relationships." not in html
    tagline = html.split('<p class="tagline">')[1].split("</p>")[0]
    assert "observatory" not in tagline.lower()


def test_primary_ui_has_single_relationship_type_dropdown_and_no_sample_or_current_state():
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()
    assert html.count('name="relationship_type"') == 1
    assert "What kind of connection is this?" in html
    assert "Optional sample scenario" not in html
    assert "relationship_sample" not in html
    assert "Current state" not in html
    assert 'name="status"' not in html
    assert "What are you hoping to understand?" in html
    assert "Anything important about this connection?" in html


def test_preview_renderer_uses_details_but_markdown_export_stays_plain():
    source = Path("packages/astro-core/constellation_core/static/app.js").read_text()
    report_source = Path("packages/astro-core/constellation_core/report.py").read_text()
    assert '<details class="report-section"' in source
    assert "<summary>" in source
    assert 'new Blob([markdownText], { type: "text/markdown" })' in source
    assert "<details" not in report_source
    assert "<summary>" not in report_source


def test_primary_report_flow_is_simplified_and_ai_runs_automatically():
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()
    source = Path("packages/astro-core/constellation_core/static/app.js").read_text()

    assert html.count('id="download"') == 1
    assert html.count('id="report_status"') == 1
    assert 'aria-live="polite"' in html
    assert 'id="generate"' in html
    assert "Generate Relationship Map" in html
    assert 'id="enhance_prose"' not in html
    assert 'id="enhance_ai"' not in html
    assert "Enhance prose with AI" not in html
    assert "Enhance with AI" not in html
    assert "Save without generating" not in html
    assert "/static/app.js?v=report-flow-chart-check-20260610" in html
    assert "/static/styles.css?v=report-flow-chart-check-20260610" in html
    assert "Interpretive prose may be refined using AI. Chart calculations remain deterministic." in html
    assert "How readings are prepared" not in html
    assert "Export / developer tools" in html
    report_panel = html.split('<section id="report-section"')[1].split("</section>")[0]
    assert "Preview</button>" not in report_panel
    assert "View Markdown" in report_panel
    assert "Copy Markdown" in report_panel
    assert "Download Markdown" not in report_panel.split("Export / developer tools")[0]
    assert "Preparing your map" in source
    assert "Writing your reading" in source
    assert "Relationship Map ready" in source
    for forbidden in (
        "Standard report",
        "Enhanced report",
        "Enhanced prose unavailable",
        "Writing enhanced report",
        "standard report",
        "enhanced report",
        "Enhanced prose",
        "AI enhancement",
        "The standard report appears first",
        "automatically tries to polish",
    ):
        assert forbidden not in html
        assert forbidden not in source
    assert 'fetch("/report/enhance"' in source
    assert "void enhanceReportMarkdown(standardMarkdown)" in source
    assert "setReportMarkdown(standardMarkdown)" in source
    assert "const standardMarkdown = payload.markdown" in source
    assert "synthesis_packet: currentSynthesisPacket" in source
    assert 'new Blob([markdownText], { type: "text/markdown" })' in source
    assert "updateDownload(currentMarkdown)" in source
    assert '<details class="report-section"' in source


def test_birthplace_select_is_hidden_until_results_can_render():
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()
    source = Path("packages/astro-core/constellation_core/static/app.js").read_text()

    assert "Choose birthplace" not in html
    assert 'name="a_place_result"' in html
    assert 'name="b_place_result"' in html
    assert 'id="a_place_result_label" class="place-result hidden"' in html
    assert 'id="b_place_result_label" class="place-result hidden"' in html
    assert "Select matching birthplace" in html
    assert 'label.classList.toggle("hidden", results.length === 0)' in source
    assert 'select.appendChild(option)' in source


def test_orphaned_birthplace_helper_removed_from_header():
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()
    header = html.split("</header>")[0]
    you_section = html.split('<div id="you-section" class="tight">')[1].split('<div class="divider"></div>')[0]

    assert "Search for the city where you were born." not in header
    assert "Search for the city where you were born." in you_section


def test_header_styles_are_compact_and_prevent_overflow():
    css = Path("packages/astro-core/constellation_core/static/styles.css").read_text()

    assert "overflow-x: hidden" in css
    assert "overflow-wrap: anywhere" in css
    assert "clamp(1.8rem, 4.2vw, 3rem)" in css
    assert "clamp(2rem, 6vw, 4rem)" not in css


def test_constellation_patterns_ui_content_is_present_and_safe():
    source = Path("packages/astro-core/constellation_core/static/app.js").read_text()

    assert "Constellation Patterns" in source
    assert "Save two or more relationships to see recurring patterns across your constellation." in source
    assert 'fetch("/constellation-patterns")' in source
    assert "saved relationships analyzed" in source
    assert "Relationship types" in source
    assert "Recurring named themes" in source
    assert "Repeated motifs" in source
    pattern_source = source.split("function renderConstellationPatterns")[1].split("async function loadConstellation")[0]
    assert "compatibility score" not in pattern_source.lower()
    assert "meant to be" not in pattern_source.lower()
    assert "deterministic fate" not in pattern_source.lower()


def test_birthplace_edits_clear_stale_place_selection_and_warn_user():
    source = Path("packages/astro-core/constellation_core/static/app.js").read_text()
    html = Path("packages/astro-core/constellation_core/static/index.html").read_text()

    assert "function clearPlaceSelection(prefix)" in source
    assert 'form.elements.b_place_query.addEventListener("input", () => clearPlaceSelection("b"))' in source
    assert 'form.elements[`${prefix}_latitude`].value = ""' in source
    assert 'form.elements[`${prefix}_longitude`].value = ""' in source
    assert 'form.elements[`${prefix}_timezone`].value = ""' in source
    assert "placeSelections[prefix] = null" in source
    assert "Please search and select the birthplace" in source
    assert "Please reselect the birthplace" in source
    assert 'id="b_place_warning"' in html


def test_report_scrolls_once_after_standard_report():
    source = Path("packages/astro-core/constellation_core/static/app.js").read_text()

    assert "let shouldScrollToReport = false" in source
    assert "function scrollReportIntoViewOnce()" in source
    assert 'document.getElementById("report-section")?.scrollIntoView({ behavior: "smooth", block: "start" })' in source
    standard_flow = source.split("async function generateSavedReport")[1].split("async function enhanceReportMarkdown")[0]
    enhancement_flow = source.split("async function enhanceReportMarkdown")[1].split("function relationshipLabel")[0]
    assert "scrollReportIntoViewOnce()" in standard_flow
    assert "scrollReportIntoViewOnce()" not in enhancement_flow
