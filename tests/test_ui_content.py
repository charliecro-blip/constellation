from pathlib import Path


def test_relationship_type_options_include_ex_and_unresolved_separately():
    html = Path('packages/astro-core/constellation_core/static/index.html').read_text()
    assert '>Ex<' in html
    assert 'Unresolved connection' in html
    assert 'Ex / unresolved' not in html


def test_metadata_not_prominent_report_section_label():
    source = Path('packages/astro-core/constellation_core/report.py').read_text()
    assert 'Report Metadata' not in source
    assert 'Optional Technical Details' not in source


def test_homepage_hero_subtitle_updated_without_repeated_observatory():
    html = Path('packages/astro-core/constellation_core/static/index.html').read_text()
    assert 'Your relationship observatory' in html
    assert 'Map the people who shape your life through astrology, timing, and relational patterning.' in html
    assert 'An observatory for all your human relationships.' not in html
    tagline = html.split('<p class="tagline">')[1].split('</p>')[0]
    assert 'observatory' not in tagline.lower()


def test_primary_ui_has_single_relationship_type_dropdown_and_no_sample_or_current_state():
    html = Path('packages/astro-core/constellation_core/static/index.html').read_text()
    assert html.count('name="relationship_type"') == 1
    assert 'What kind of connection is this?' in html
    assert 'Optional sample scenario' not in html
    assert 'relationship_sample' not in html
    assert 'Current state' not in html
    assert 'name="status"' not in html
    assert 'What are you hoping to understand?' in html
    assert 'Anything important about this connection?' in html


def test_preview_renderer_uses_details_but_markdown_export_stays_plain():
    source = Path('packages/astro-core/constellation_core/static/app.js').read_text()
    report_source = Path('packages/astro-core/constellation_core/report.py').read_text()
    assert '<details class="report-section"' in source
    assert '<summary>' in source
    assert 'new Blob([markdownText], { type: "text/markdown" })' in source
    assert '<details' not in report_source
    assert '<summary>' not in report_source
