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
    assert "/static/app.js?v=simplified-report-flow-20260609" in html
    assert "/static/styles.css?v=simplified-report-flow-20260609" in html
    assert "Interpretive prose may be refined using AI. Chart calculations remain deterministic." in html
    assert "How readings are prepared" in html
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
    assert 'body: JSON.stringify({ markdown: standardMarkdown, context: buildContext() })' in source
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
