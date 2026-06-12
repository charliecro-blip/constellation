"""Explicit registry for relationship-pattern report prioritization doctrine.

See docs/astrology_doctrine/pattern_taxonomy.md and
docs/astrology_doctrine/report_prioritization.md for the doctrine behind
categories, tiers, and lead eligibility.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .scoring_weights import LEAD_ELIGIBLE_CATEGORIES, TIER_WEIGHTS


@dataclass(frozen=True)
class PatternMetadata:
    key: str
    tier: int
    category: str
    base_weight: int
    lead_eligible: bool
    default_section: str
    description: str


def _metadata(
    key: str,
    tier: int,
    category: str,
    default_section: str,
    description: str,
    *,
    lead_eligible: bool | None = None,
) -> PatternMetadata:
    return PatternMetadata(
        key=key,
        tier=tier,
        category=category,
        base_weight=TIER_WEIGHTS[tier],
        lead_eligible=(category in LEAD_ELIGIBLE_CATEGORIES if lead_eligible is None else lead_eligible),
        default_section=default_section,
        description=description,
    )


PATTERN_REGISTRY: dict[str, PatternMetadata] = {
    # Tier 1: report-leading signatures.
    "synastry.sun_moon": _metadata(
        "synastry.sun_moon",
        1,
        "emotional_recognition",
        "central",
        "Core luminary recognition between identity and emotional body.",
    ),
    "synastry.moon_moon": _metadata(
        "synastry.moon_moon",
        1,
        "emotional_recognition",
        "central",
        "Shared or strongly activated emotional rhythm between both Moons.",
    ),
    "synastry.venus_mars": _metadata(
        "synastry.venus_mars",
        1,
        "erotic_charge",
        "central",
        "Classic attraction signature linking desire, receptivity, and pursuit.",
    ),
    "synastry.venus_ascendant": _metadata(
        "synastry.venus_ascendant",
        1,
        "erotic_charge",
        "central",
        "Venus activates the Ascendant field through attraction, ease, and embodiment.",
    ),
    "synastry.angle_ascendant_sun": _metadata(
        "synastry.angle_ascendant_sun",
        1,
        "emotional_recognition",
        "central",
        "Solar identity contacts the Ascendant and makes recognition immediate.",
    ),
    "synastry.angle_ascendant_moon": _metadata(
        "synastry.angle_ascendant_moon",
        1,
        "emotional_recognition",
        "central",
        "Lunar feeling contacts the Ascendant and makes the bond somatically noticeable.",
    ),
    "synastry.moon_saturn": _metadata(
        "synastry.moon_saturn",
        1,
        "stability_container",
        "friction_repair",
        "Saturn contacts the Moon, emphasizing emotional responsibility, pressure, and repair.",
    ),
    "synastry.venus_saturn": _metadata(
        "synastry.venus_saturn",
        1,
        "devotion_contract",
        "friction_repair",
        "Saturn contacts Venus, emphasizing affection under commitment, limits, or tests.",
    ),
    "synastry.mars_saturn": _metadata(
        "synastry.mars_saturn",
        1,
        "stability_container",
        "friction_repair",
        "Saturn contacts Mars, emphasizing pacing, inhibition, endurance, and responsibility.",
    ),
    # Tier 2: major relationship signatures.
    "synastry.venus_pluto": _metadata(
        "synastry.venus_pluto",
        2,
        "projection_mirror",
        "central",
        "Venus-Pluto intensifies attraction, attachment, projection, and transformation themes.",
        lead_eligible=False,
    ),
    "synastry.mars_pluto": _metadata(
        "synastry.mars_pluto",
        2,
        "erotic_charge",
        "friction_repair",
        "Mars-Pluto concentrates desire, will, intensity, and power dynamics.",
    ),
    "synastry.moon_venus": _metadata(
        "synastry.moon_venus",
        2,
        "emotional_recognition",
        "central",
        "Moon-Venus links emotional safety with affection, warmth, and care.",
    ),
    "synastry.moon_mars": _metadata(
        "synastry.moon_mars",
        2,
        "erotic_charge",
        "friction_repair",
        "Moon-Mars activates feeling through desire, irritation, and embodied responsiveness.",
    ),
    "synastry.moon_pluto": _metadata(
        "synastry.moon_pluto",
        2,
        "trust_depth",
        "friction_repair",
        "Moon-Pluto intensifies vulnerability, attachment, fear, and emotional truth-telling.",
        lead_eligible=False,
    ),
    "house_overlay": _metadata(
        "house_overlay",
        2,
        "familiar_pull",
        "supporting",
        "House overlays show where one person's planets land in the other's lived field.",
        lead_eligible=False,
    ),
    "overlay.house_1": _metadata(
        "overlay.house_1",
        2,
        "projection_mirror",
        "supporting",
        "First-house overlays emphasize embodiment, identity, and immediate presence.",
        lead_eligible=False,
    ),
    "overlay.house_4": _metadata(
        "overlay.house_4",
        2,
        "private_roots",
        "supporting",
        "Fourth-house overlays emphasize home, memory, family patterning, and roots.",
        lead_eligible=False,
    ),
    "overlay.house_5": _metadata(
        "overlay.house_5",
        2,
        "erotic_charge",
        "supporting",
        "Fifth-house overlays emphasize romance, play, pleasure, and creative charge.",
        lead_eligible=False,
    ),
    "overlay.house_7": _metadata(
        "overlay.house_7",
        2,
        "devotion_contract",
        "supporting",
        "Seventh-house overlays emphasize partnership mirroring and relational choice.",
        lead_eligible=False,
    ),
    "overlay.house_8": _metadata(
        "overlay.house_8",
        2,
        "trust_depth",
        "supporting",
        "Eighth-house overlays emphasize intimacy, exposure, trust, and entanglement.",
        lead_eligible=False,
    ),
    "composite.stellium": _metadata(
        "composite.stellium",
        2,
        "projection_mirror",
        "composite",
        "Composite stelliums concentrate the relationship field around a specific sign or topic.",
        lead_eligible=False,
    ),
    "composite.conjunction_cluster": _metadata(
        "composite.conjunction_cluster",
        2,
        "projection_mirror",
        "composite",
        "Composite conjunction clusters make several relationship functions operate as one circuit.",
        lead_eligible=False,
    ),
    "composite.venus_mars": _metadata(
        "composite.venus_mars",
        2,
        "erotic_charge",
        "composite",
        "Composite Venus-Mars describes shared attraction mechanics.",
    ),
    "composite.mars_pluto": _metadata(
        "composite.mars_pluto",
        2,
        "erotic_charge",
        "friction_repair",
        "Composite Mars-Pluto concentrates shared intensity and power dynamics.",
    ),
    "composite.venus_saturn": _metadata(
        "composite.venus_saturn",
        2,
        "devotion_contract",
        "friction_repair",
        "Composite Venus-Saturn describes affection shaped by commitment or limits.",
    ),
    "composite.sun_saturn": _metadata(
        "composite.sun_saturn",
        2,
        "stability_container",
        "friction_repair",
        "Composite Sun-Saturn describes the relationship identity under structure, duty, and time.",
    ),
    "composite.moon_saturn": _metadata(
        "composite.moon_saturn",
        2,
        "stability_container",
        "friction_repair",
        "Composite Moon-Saturn describes emotional containment, pressure, and reliability work.",
    ),
    "composite.moon_uranus": _metadata(
        "composite.moon_uranus",
        2,
        "volatility",
        "friction_repair",
        "Composite Moon-Uranus describes emotional variability, space needs, and nervous-system charge.",
        lead_eligible=False,
    ),
    # Tier 3: supporting signatures and texture.
    "synastry.mercury_mars": _metadata(
        "synastry.mercury_mars",
        3,
        "communication_heat",
        "supporting",
        "Mercury-Mars describes fast, sharp, activating, or argumentative communication.",
        lead_eligible=False,
    ),
    "synastry.mercury_mercury": _metadata(
        "synastry.mercury_mercury",
        3,
        "communication_heat",
        "supporting",
        "Mercury-Mercury describes conversational rhythm, translation, and mental rapport.",
        lead_eligible=False,
    ),
    "overlay.house_10": _metadata(
        "overlay.house_10",
        3,
        "public_life",
        "supporting",
        "Tenth-house overlays emphasize public life, reputation, vocation, and direction.",
        lead_eligible=False,
    ),
    "synastry.angle_midheaven_sun": _metadata(
        "synastry.angle_midheaven_sun",
        3,
        "public_life",
        "supporting",
        "Sun-Midheaven contacts emphasize visibility and life direction.",
        lead_eligible=False,
    ),
    "synastry.angle_midheaven_moon": _metadata(
        "synastry.angle_midheaven_moon",
        3,
        "public_life",
        "supporting",
        "Moon-Midheaven contacts connect private feeling with public path.",
        lead_eligible=False,
    ),
    "synastry.angle_midheaven_venus": _metadata(
        "synastry.angle_midheaven_venus",
        3,
        "public_life",
        "supporting",
        "Venus-Midheaven contacts emphasize admiration, aesthetics, and social visibility.",
        lead_eligible=False,
    ),
    "composite.nodes_on_mc_ic": _metadata(
        "composite.nodes_on_mc_ic",
        3,
        "public_life",
        "composite",
        "Composite nodes on MC/IC emphasize public direction and private-root themes.",
        lead_eligible=False,
    ),
}

ALIASES = {
    "sun_moon": "synastry.sun_moon",
    "moon_moon": "synastry.moon_moon",
    "venus_mars": "synastry.venus_mars",
    "moon_venus": "synastry.moon_venus",
    "moon_mars": "synastry.moon_mars",
    "venus_pluto": "synastry.venus_pluto",
    "mars_pluto": "synastry.mars_pluto",
    "moon_saturn": "synastry.moon_saturn",
    "venus_saturn": "synastry.venus_saturn",
    "mars_saturn": "synastry.mars_saturn",
    "mercury_mars": "synastry.mercury_mars",
    "mercury_mercury": "synastry.mercury_mercury",
    "moon_pluto": "synastry.moon_pluto",
    "venus_ascendant": "synastry.venus_ascendant",
    "sun_ascendant": "synastry.angle_ascendant_sun",
    "moon_ascendant": "synastry.angle_ascendant_moon",
    "composite.mars_venus": "composite.venus_mars",
    "composite.saturn_venus": "composite.venus_saturn",
    "composite.saturn_sun": "composite.sun_saturn",
}

FALLBACK_PATTERN_METADATA = PatternMetadata(
    key="unknown",
    tier=4,
    category="supporting_texture",
    base_weight=TIER_WEIGHTS[4],
    lead_eligible=False,
    default_section="supporting",
    description="Unregistered or emerging pattern; keep as supporting texture until classified.",
)


def get_pattern_metadata(pattern_key: str) -> PatternMetadata:
    """Return registry metadata for a detected pattern key.

    Prefix families such as ``composite.stellium.<sign>`` and house overlay
    variants resolve to their doctrine-level registry entries.
    """
    canonical_key = ALIASES.get(pattern_key, pattern_key)
    if canonical_key in PATTERN_REGISTRY:
        return PATTERN_REGISTRY[canonical_key]
    if canonical_key.startswith("composite.stellium."):
        return PATTERN_REGISTRY["composite.stellium"]
    if canonical_key.startswith("overlay.house_"):
        return PATTERN_REGISTRY.get(canonical_key, PATTERN_REGISTRY["house_overlay"])
    return replace(FALLBACK_PATTERN_METADATA, key=pattern_key)


def convergence_category_for(pattern) -> str:
    """Return the report-prioritization theme used for convergence checks."""
    key = getattr(pattern, "key", str(pattern))
    metadata = get_pattern_metadata(key)
    title = getattr(pattern, "title", "").lower()
    evidence = " ".join(getattr(pattern, "evidence", [])).lower()
    text = f"{title} {evidence}"

    if key in {"synastry.venus_pluto", "synastry.mars_pluto", "synastry.moon_pluto", "composite.mars_pluto"}:
        return "trust_depth"
    if key.startswith("composite.stellium."):
        if ".scorpio" in key or " scorpio" in text or "pluto" in text:
            return "trust_depth"
        if "venus" in text and "mars" in text:
            return "erotic_charge"
        if "moon" in text and "saturn" in text:
            return "stability_container"
    if key == "composite.conjunction_cluster":
        if "pluto" in text or "scorpio" in text:
            return "trust_depth"
        if "venus" in text and "mars" in text:
            return "erotic_charge"
        if "moon" in text and "saturn" in text:
            return "stability_container"
    return metadata.category


def planet_pair_for(pattern) -> tuple[str, str] | None:
    """Return the normalized planet pair for aspect-like relationship patterns."""
    key = getattr(pattern, "key", str(pattern))
    canonical_key = ALIASES.get(key, key)
    pair_by_key = {
        "synastry.sun_moon": ("moon", "sun"),
        "synastry.moon_moon": ("moon", "moon"),
        "synastry.venus_mars": ("mars", "venus"),
        "synastry.moon_venus": ("moon", "venus"),
        "synastry.moon_mars": ("mars", "moon"),
        "synastry.mercury_mars": ("mars", "mercury"),
        "synastry.mercury_mercury": ("mercury", "mercury"),
        "synastry.moon_saturn": ("moon", "saturn"),
        "synastry.moon_pluto": ("moon", "pluto"),
        "synastry.venus_pluto": ("pluto", "venus"),
        "synastry.mars_pluto": ("mars", "pluto"),
        "synastry.venus_saturn": ("saturn", "venus"),
        "synastry.mars_saturn": ("mars", "saturn"),
        "composite.venus_mars": ("mars", "venus"),
        "composite.mars_pluto": ("mars", "pluto"),
        "composite.venus_saturn": ("saturn", "venus"),
        "composite.sun_saturn": ("saturn", "sun"),
        "composite.moon_saturn": ("moon", "saturn"),
        "composite.moon_uranus": ("moon", "uranus"),
    }
    return pair_by_key.get(canonical_key)
