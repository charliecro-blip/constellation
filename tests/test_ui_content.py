import subprocess
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
    assert html.count('name="user_question"') == 1
    assert html.count('name="origin_story"') == 1
    assert 'What kind of connection is this?' in html
    assert 'Optional sample scenario' not in html
    assert 'relationship_sample' not in html
    assert 'Current state' not in html
    assert 'Known themes' not in html
    assert 'name="status"' not in html
    assert 'What are you hoping to understand?' in html
    assert 'Anything important about this connection?' in html


def test_simplified_context_js_uses_safe_field_helpers_and_no_removed_field_values():
    js = Path('packages/astro-core/constellation_core/static/app.js').read_text()
    assert js.count('const defaultState') == 1
    assert js.count('const sample') == 1
    assert js.count('function buildContext') == 1
    assert 'function fieldValue(name, fallback = "")' in js
    assert 'const relationshipType = fieldValue("relationship_type", "romantic")' in js
    assert 'status: inferredStatus(relationshipType)' in js
    assert 'known_themes: []' in js
    assert 'form.elements.status' not in js
    assert 'form.elements.known_themes' not in js
    assert 'relationship_sample' not in js


def test_static_app_javascript_parses():
    result = subprocess.run(
        ['node', '-c', 'packages/astro-core/constellation_core/static/app.js'],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
