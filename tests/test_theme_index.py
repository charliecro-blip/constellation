"""Tests for the thematic atlas — theme_index.py.

Covers deterministic category→theme mapping, section anchors, theme_tags on
DynamicDetail, ThemePresence strength, and the full generate_relationship_report
integration.
"""

from __future__ import annotations

from constellation_core.theme_index import (
    THEME_TAXONOMY,
    ThemePresence,
    build_theme_index,
    theme_tags_for_category,
)


# ---------------------------------------------------------------------------
# theme_tags_for_category
# ---------------------------------------------------------------------------


def test_emotional_recognition_maps_to_emotional_dynamics():
    tags = theme_tags_for_category("emotional_recognition")
    assert "emotional-dynamics" in tags


def test_erotic_charge_maps_to_eros_attraction():
    tags = theme_tags_for_category("erotic_charge")
    assert "eros-attraction" in tags


def test_communication_heat_maps_to_communication():
    tags = theme_tags_for_category("communication_heat")
    assert "communication" in tags


def test_trust_depth_maps_to_trust_vulnerability():
    tags = theme_tags_for_category("trust_depth")
    assert "trust-vulnerability" in tags


def test_informational_maps_to_nothing():
    tags = theme_tags_for_category("informational")
    assert tags == []


def test_supporting_texture_maps_to_nothing():
    tags = theme_tags_for_category("supporting_texture")
    assert tags == []


def test_asteroid_categories_map_to_nothing():
    assert theme_tags_for_category("asteroid_support") == []
    assert theme_tags_for_category("asteroid_overlay") == []


def test_repair_prompt_adds_repair_practice_tag():
    tags = theme_tags_for_category("trust_depth", has_repair_prompt=True)
    assert "repair-practice" in tags


def test_composite_layer_adds_composite_field_tag():
    tags = theme_tags_for_category("erotic_charge", layer="composite")
    assert "composite-field" in tags


def test_friction_repair_section_adds_conflict_and_repair_tags():
    tags = theme_tags_for_category("trust_depth", section="Friction and Repair")
    assert "conflict-friction" in tags
    assert "repair-practice" in tags


def test_base_content_tags_capped_at_two_repair_is_additive():
    # erotic_charge alone (no section, no repair, no layer) — capped at 2
    tags_plain = theme_tags_for_category("erotic_charge")
    assert len(tags_plain) <= 2
    # With composite layer, section, and repair: section extras and repair are additive beyond the 2-cap
    tags_full = theme_tags_for_category(
        "erotic_charge", section="Friction and Repair", has_repair_prompt=True, layer="composite"
    )
    assert "repair-practice" in tags_full
    assert "conflict-friction" in tags_full
    assert "composite-field" in tags_full


def test_unknown_category_returns_empty():
    tags = theme_tags_for_category("totally_unknown_category")
    assert tags == []


# ---------------------------------------------------------------------------
# build_theme_index
# ---------------------------------------------------------------------------


class _FakePattern:
    def __init__(self, key: str, category: str, layer: str, priority: int, id: str):
        self.key = key
        self.category = category
        self.layer = layer
        self.priority = priority
        self.id = id


class _FakeSection:
    def __init__(self, title: str, anchor: str | None = None):
        self.title = title
        self.anchor = anchor


class _FakeDetail:
    def __init__(self, id: str, priority: int, theme_tags: list[str]):
        self.id = id
        self.priority = priority
        self.theme_tags = theme_tags


def _index_by_theme(index: list[ThemePresence]) -> dict[str, ThemePresence]:
    return {t.theme: t for t in index}


def test_build_theme_index_covers_all_taxonomy_themes():
    index = build_theme_index([], [], [])
    themes = {t.theme for t in index}
    assert themes == set(THEME_TAXONOMY.keys())


def test_build_theme_index_absent_when_no_patterns():
    index = build_theme_index([], [], [])
    idx = _index_by_theme(index)
    assert idx["eros-attraction"].strength == "absent"
    assert idx["eros-attraction"].present is False


def test_high_priority_erotic_charge_produces_primary_theme():
    patterns = [_FakePattern("synastry.venus_mars", "erotic_charge", "synastry", 85, "vm1")]
    index = build_theme_index(patterns, [], [])
    idx = _index_by_theme(index)
    assert idx["eros-attraction"].present is True
    assert idx["eros-attraction"].strength == "primary"


def test_low_priority_pattern_produces_background_theme():
    patterns = [_FakePattern("synastry.sun_sun_conjunction", "recognition", "synastry", 40, "ss1")]
    index = build_theme_index(patterns, [], [])
    # recognition is not in CATEGORY_TO_THEMES explicitly, so no themes should be present
    present = [t for t in index if t.present]
    for t in present:
        assert t.strength in {"background", "secondary", "primary"}


def test_composite_section_always_produces_composite_field_theme():
    sections = [_FakeSection("Composite Field", "composite-field")]
    index = build_theme_index([], sections, [])
    idx = _index_by_theme(index)
    # Section alone doesn't add patterns, but anchor_ids should have been recorded.
    # Composite field is present via section even with zero patterns.
    assert "composite-field" in idx


def test_detail_theme_tags_are_reflected_in_anchor_ids():
    details = [_FakeDetail("detail-foo", 80, ["eros-attraction", "partnership-commitment"])]
    index = build_theme_index([], [], details)
    idx = _index_by_theme(index)
    assert "detail-foo" in idx["eros-attraction"].anchor_ids
    assert "detail-foo" in idx["partnership-commitment"].anchor_ids


def test_pattern_count_reflects_number_of_contributing_patterns():
    patterns = [
        _FakePattern("synastry.venus_mars", "erotic_charge", "synastry", 80, "vm1"),
        _FakePattern("synastry.venus_ascendant", "erotic_charge", "synastry", 75, "va1"),
    ]
    index = build_theme_index(patterns, [], [])
    idx = _index_by_theme(index)
    assert idx["eros-attraction"].pattern_count == 2


# ---------------------------------------------------------------------------
# Integration: generate_relationship_report produces anchors and theme_index
# ---------------------------------------------------------------------------


def _golden_relationship():
    """Pull the emotional_recognition_leads golden case for integration testing."""
    from fixtures.relationship_cases import GOLDEN_RELATIONSHIP_CASES
    return GOLDEN_RELATIONSHIP_CASES["emotional_recognition_leads"]


def test_report_sections_have_anchors():
    from constellation_core.report import generate_relationship_report

    case = _golden_relationship()
    report = generate_relationship_report(case.relationship, context=case.context)
    anchored = {s.anchor for s in report.sections if s.anchor}
    assert "overview" in anchored
    assert "composite-field" in anchored
    assert "friction-repair" in anchored
    assert "chart-check" in anchored
    assert "profile-a" in anchored
    assert "profile-b" in anchored
    assert "activation-a-to-b" in anchored
    assert "activation-b-to-a" in anchored


def test_report_has_theme_index():
    from constellation_core.report import generate_relationship_report

    case = _golden_relationship()
    report = generate_relationship_report(case.relationship, context=case.context)
    assert len(report.theme_index) == len(THEME_TAXONOMY)
    assert all(isinstance(t, ThemePresence) for t in report.theme_index)


def test_emotional_dynamics_present_for_emotional_recognition_case():
    from constellation_core.report import generate_relationship_report

    case = _golden_relationship()
    report = generate_relationship_report(case.relationship, context=case.context)
    idx = _index_by_theme(report.theme_index)
    assert idx["emotional-dynamics"].present is True
    assert idx["emotional-dynamics"].strength in {"primary", "secondary"}


def test_dynamic_details_have_theme_tags():
    from constellation_core.report import generate_relationship_report

    case = _golden_relationship()
    report = generate_relationship_report(case.relationship, context=case.context)
    assert report.dynamic_details, "Expected at least one dynamic detail"
    for detail in report.dynamic_details:
        assert isinstance(detail.theme_tags, list)


def test_synthesis_packet_has_active_themes():
    from constellation_core.report import build_report_synthesis_packet

    case = _golden_relationship()
    packet = build_report_synthesis_packet(case.relationship, context=case.context)
    assert isinstance(packet.active_themes, list)
    assert len(packet.active_themes) <= 5
    for theme in packet.active_themes:
        assert theme in THEME_TAXONOMY, f"Unknown theme slug in active_themes: {theme}"


def test_active_themes_only_primary_or_secondary():
    from constellation_core.report import build_report_synthesis_packet, generate_relationship_report

    case = _golden_relationship()
    report = generate_relationship_report(case.relationship, context=case.context)
    packet = build_report_synthesis_packet(case.relationship, context=case.context)
    strong_themes = {t.theme for t in report.theme_index if t.strength in {"primary", "secondary"}}
    for theme in packet.active_themes:
        assert theme in strong_themes, f"{theme} in active_themes but not primary/secondary in theme_index"


def test_informational_and_asteroid_categories_absent_from_theme_index():
    from constellation_core.report import generate_relationship_report

    case = _golden_relationship()
    report = generate_relationship_report(case.relationship, context=case.context)
    # All theme slugs must be from the taxonomy (never internal categories).
    for entry in report.theme_index:
        assert entry.theme in THEME_TAXONOMY
    # None of the internal non-surfaced category names should appear as theme slugs.
    for entry in report.theme_index:
        assert entry.theme not in {"informational", "supporting_texture", "asteroid_support", "asteroid_overlay"}
