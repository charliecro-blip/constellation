"""Thematic atlas: deterministic mapping from pattern categories to reader-facing themes.

Theme tags are derived from pattern categories, sections, and layers — never from
prose parsing and never invented by AI. The frontend uses ThemePresence to build
jump navigation without touching report text.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ThemeStrength = Literal["primary", "secondary", "background", "absent"]

THEME_TAXONOMY: dict[str, str] = {
    "emotional-dynamics": "Emotional Dynamics",
    "eros-attraction": "Eros & Attraction",
    "romance-play": "Romance & Play",
    "partnership-commitment": "Partnership / Commitment",
    "trust-vulnerability": "Trust & Vulnerability",
    "communication": "Communication",
    "conflict-friction": "Conflict / Friction",
    "repair-practice": "Repair Practices",
    "home-roots": "Home / Roots",
    "unconscious-spiritual": "Unconscious / Spiritual",
    "composite-field": "Composite Field",
    "chart-check": "Technical Chart Check",
}

# Maps internal pattern categories to one or two reader-facing theme slugs.
# Order matters: first slug is the primary theme for this category.
CATEGORY_TO_THEMES: dict[str, list[str]] = {
    # Emotional dynamics cluster
    "emotional_recognition": ["emotional-dynamics"],
    "emotional_translation": ["emotional-dynamics"],
    "emotional_structure": ["emotional-dynamics", "conflict-friction"],
    "stability_container": ["emotional-dynamics", "partnership-commitment"],
    "emotional_body": ["emotional-dynamics"],
    "emotional_activation": ["emotional-dynamics"],
    "emotional_variability": ["emotional-dynamics", "conflict-friction"],
    "emotional_intensity": ["emotional-dynamics", "conflict-friction"],
    # Eros / attraction cluster
    "erotic_charge": ["eros-attraction"],
    "desire": ["eros-attraction"],
    "attraction": ["eros-attraction"],
    "attraction_intensity": ["eros-attraction"],
    # Romance / play
    "romance_creativity": ["romance-play"],
    "play": ["romance-play"],
    # Partnership / commitment cluster
    "devotion_contract": ["partnership-commitment"],
    "familiar_pull": ["partnership-commitment"],
    "bond_structure": ["partnership-commitment", "conflict-friction"],
    "relationship_structure": ["partnership-commitment"],
    "fated_axis": ["partnership-commitment"],
    "partnership": ["partnership-commitment"],
    # Trust / vulnerability
    "trust_depth": ["trust-vulnerability"],
    "wounding_healing": ["trust-vulnerability"],
    "projection_mirror": ["trust-vulnerability", "unconscious-spiritual"],
    "idealization": ["trust-vulnerability"],
    # Communication
    "communication": ["communication"],
    "communication_heat": ["communication"],
    # Conflict / friction (no primary non-communication overlaps above)
    "volatility": ["conflict-friction"],
    "action_structure": ["conflict-friction"],
    "intensity": ["conflict-friction"],
    "embodied_activation": ["conflict-friction"],
    # Home / roots
    "private_roots": ["home-roots"],
    "home_roots": ["home-roots"],
    "daily_life": ["home-roots"],
    # Unconscious / spiritual
    "hidden_field": ["unconscious-spiritual"],
    "nodal_axis": ["unconscious-spiritual"],
    "angle_luminary": ["eros-attraction"],  # falls to eros/recognition; refined by section below
    "angle_structure": ["chart-check"],
    # Composite cluster — section-based, see build_theme_index
    "composite_concentration": ["composite-field"],
    # Public life — no reader theme; routes to chart-check
    "public_life": ["chart-check"],
    "public_direction": ["chart-check"],
    "identity_body": ["chart-check"],
    "relationship_identity": ["chart-check"],
    # Informational / supporting — never surfaced in theme index
    "informational": [],
    "supporting_texture": [],
    "asteroid_support": [],
    "asteroid_overlay": [],
}

# Section-level theme overrides: some sections always tag certain themes.
SECTION_EXTRA_THEMES: dict[str, list[str]] = {
    "Composite Field": ["composite-field"],
    "Friction and Repair": ["conflict-friction", "repair-practice"],
    "Calculated chart check": ["chart-check"],
}


def theme_tags_for_category(
    category: str,
    section: str = "",
    *,
    has_repair_prompt: bool = False,
    layer: str = "",
) -> list[str]:
    """Return up to 2 reader-facing theme slugs for a pattern category + section."""
    base = list(CATEGORY_TO_THEMES.get(category, []))

    # Composite layer always tags composite-field.
    if layer == "composite" and "composite-field" not in base:
        base = ["composite-field"] + base

    # Cap category-derived tags at 2 before adding section/repair extras.
    base = base[:2]

    # Section extras are additive (not counted toward the 2-cap).
    for extra in SECTION_EXTRA_THEMES.get(section, []):
        if extra not in base:
            base.append(extra)

    # Details with repair prompts always carry repair-practice.
    if has_repair_prompt and "repair-practice" not in base:
        base.append("repair-practice")

    return base


class ThemePresence(BaseModel):
    """Reader-facing theme presence entry for the thematic atlas navigation index."""

    theme: str
    label: str
    present: bool
    strength: ThemeStrength
    anchor_ids: list[str] = Field(default_factory=list)
    pattern_count: int = 0


def build_theme_index(
    weighted_patterns: list,  # list[Pattern] — avoiding circular import
    sections: list,  # list[ReportSection]
    dynamic_details: list,  # list[DynamicDetail]
) -> list[ThemePresence]:
    """Compute the theme index from weighted patterns, sections, and dynamic details.

    Must receive the same weighted, ranked patterns that generated the report.
    Never uses raw pre-weighted patterns.
    """
    from .pattern_registry import convergence_category_for

    # Accumulate theme hits: theme_slug -> list of (priority, anchor_id)
    theme_hits: dict[str, list[tuple[int, str]]] = {slug: [] for slug in THEME_TAXONOMY}

    # Patterns contribute to themes.
    for pattern in weighted_patterns:
        category = convergence_category_for(pattern)
        tags = theme_tags_for_category(category, layer=pattern.layer)
        for tag in tags:
            if tag in theme_hits:
                anchor = f"detail-{pattern.id}"
                theme_hits[tag].append((pattern.priority, anchor))

    # Section anchors: sections with fixed themes add their anchor.
    section_anchor_map = {
        "Overview": "overview",
        "Composite Field": "composite-field",
        "Friction and Repair": "friction-repair",
        "Calculated chart check": "chart-check",
    }
    for section in sections:
        anchor = section_anchor_map.get(section.title) or getattr(section, "anchor", None)
        if anchor is None:
            continue
        for tag in SECTION_EXTRA_THEMES.get(section.title, []):
            if tag in theme_hits and anchor not in [a for _, a in theme_hits[tag]]:
                theme_hits[tag].append((0, anchor))

    # Dynamic details carry their own theme_tags.
    for detail in dynamic_details:
        tags = getattr(detail, "theme_tags", [])
        for tag in tags:
            if tag in theme_hits:
                anchor = detail.id
                if anchor not in [a for _, a in theme_hits[tag]]:
                    theme_hits[tag].append((detail.priority, anchor))

    result: list[ThemePresence] = []
    for slug, label in THEME_TAXONOMY.items():
        hits = theme_hits[slug]
        count = len(hits)
        top_priorities = sorted((p for p, _ in hits), reverse=True)
        anchor_ids = list(dict.fromkeys(a for _, a in sorted(hits, key=lambda x: -x[0])))[:6]

        if count == 0:
            strength: ThemeStrength = "absent"
            present = False
        else:
            high_priority_count = sum(1 for p in top_priorities if p >= 65)
            max_priority = top_priorities[0] if top_priorities else 0
            if high_priority_count >= 2 or max_priority >= 80:
                strength = "primary"
            elif high_priority_count >= 1 or max_priority >= 55:
                strength = "secondary"
            else:
                strength = "background"
            present = True

        result.append(
            ThemePresence(
                theme=slug,
                label=label,
                present=present,
                strength=strength,
                anchor_ids=anchor_ids,
                pattern_count=count,
            )
        )

    return result
