from pathlib import Path


def test_relationship_type_options_include_ex_and_unresolved_separately():
    html = Path('packages/astro-core/constellation_core/static/index.html').read_text()
    assert '>Ex<' in html
    assert 'Unresolved connection' in html
    assert 'Ex / unresolved' not in html


def test_metadata_not_prominent_report_section_label():
    source = Path('packages/astro-core/constellation_core/report.py').read_text()
    assert 'Report Metadata' not in source
    assert 'Optional Technical Details' in source
