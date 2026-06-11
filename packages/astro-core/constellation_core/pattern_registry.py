"""Registry metadata for relationship patterns.

The detector records concrete signatures. This registry adds synthesis metadata
that can be reused by weighting/report layers without changing detector output.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PatternMetadata:
    convergence_category: str
    planet_pair: tuple[str, str] | None = None


PATTERN_REGISTRY: dict[str, PatternMetadata] = {
    "synastry.venus_mars": PatternMetadata("erotic_charge", ("venus", "mars")),
    "composite.venus_mars": PatternMetadata("erotic_charge", ("venus", "mars")),
    "synastry.mercury_mars": PatternMetadata("communication_heat", ("mercury", "mars")),
    "synastry.mercury_mercury": PatternMetadata("communication_heat", ("mercury", "mercury")),
    "synastry.sun_moon": PatternMetadata("emotional_recognition", ("sun", "moon")),
    "synastry.moon_moon": PatternMetadata("emotional_recognition", ("moon", "moon")),
    "synastry.moon_venus": PatternMetadata("emotional_recognition", ("moon", "venus")),
    "synastry.moon_saturn": PatternMetadata("stability_container", ("moon", "saturn")),
    "composite.moon_saturn": PatternMetadata("stability_container", ("moon", "saturn")),
    "synastry.venus_saturn": PatternMetadata("devotion_contract", ("venus", "saturn")),
    "composite.venus_saturn": PatternMetadata("devotion_contract", ("venus", "saturn")),
    "synastry.mars_saturn": PatternMetadata("stability_container", ("mars", "saturn")),
    "synastry.venus_pluto": PatternMetadata("trust_depth", ("venus", "pluto")),
    "composite.venus_pluto": PatternMetadata("trust_depth", ("venus", "pluto")),
    "synastry.mars_pluto": PatternMetadata("trust_depth", ("mars", "pluto")),
    "composite.mars_pluto": PatternMetadata("trust_depth", ("mars", "pluto")),
    "synastry.moon_pluto": PatternMetadata("trust_depth", ("moon", "pluto")),
    "composite.moon_uranus": PatternMetadata("volatility", ("moon", "uranus")),
}

CATEGORY_CONVERGENCE_ALIASES = {
    "angle_luminary": "emotional_recognition",
    "recognition": "emotional_recognition",
    "emotional_translation": "emotional_recognition",
    "affection": "emotional_recognition",
    "emotional_body": "emotional_recognition",
    "desire": "erotic_charge",
    "attraction": "erotic_charge",
    "attraction_intensity": "trust_depth",
    "emotional_intensity": "trust_depth",
    "intensity": "trust_depth",
    "intimacy_depth": "trust_depth",
    "emotional_structure": "stability_container",
    "relationship_structure": "stability_container",
    "angle_structure": "stability_container",
    "action_structure": "stability_container",
    "bond_structure": "devotion_contract",
    "emotional_variability": "volatility",
    "communication": "communication_heat",
    "home_roots": "private_roots",
    "partnership": "projection_mirror",
    "fated_axis": "familiar_pull",
}

SIGN_CONVERGENCE_ALIASES = {
    "scorpio": "trust_depth",
    "capricorn": "stability_container",
    "cancer": "private_roots",
    "gemini": "communication_heat",
    "aries": "erotic_charge",
    "taurus": "devotion_contract",
}

HOUSE_CONVERGENCE_ALIASES = {
    "overlay.house_3": "communication_heat",
    "overlay.house_4": "private_roots",
    "overlay.house_7": "projection_mirror",
    "overlay.house_8": "trust_depth",
}


def registry_metadata(pattern_key: str) -> PatternMetadata | None:
    """Return exact or prefix metadata for a detected pattern key."""
    if pattern_key in PATTERN_REGISTRY:
        return PATTERN_REGISTRY[pattern_key]
    if pattern_key.startswith("synastry.angle_ascendant_") or pattern_key == "synastry.venus_ascendant":
        return PatternMetadata("emotional_recognition")
    if pattern_key.startswith("composite.stellium."):
        sign = pattern_key.rsplit(".", 1)[-1]
        return PatternMetadata(SIGN_CONVERGENCE_ALIASES.get(sign, "projection_mirror"))
    if pattern_key == "composite.conjunction_cluster":
        return PatternMetadata("projection_mirror")
    if pattern_key in HOUSE_CONVERGENCE_ALIASES:
        return PatternMetadata(HOUSE_CONVERGENCE_ALIASES[pattern_key])
    if pattern_key.startswith("synastry.asteroid.juno") or pattern_key.startswith("composite.asteroid.juno"):
        return PatternMetadata("devotion_contract")
    if pattern_key.startswith("synastry.asteroid.eros") or pattern_key.startswith("composite.asteroid.eros"):
        return PatternMetadata("erotic_charge")
    return None


def convergence_category_for(pattern_key: str, category: str) -> str:
    """Return the synthesis category used for convergence weighting."""
    metadata = registry_metadata(pattern_key)
    if metadata is not None:
        return metadata.convergence_category
    return CATEGORY_CONVERGENCE_ALIASES.get(category, category)


def planet_pair_for(pattern_key: str) -> tuple[str, str] | None:
    metadata = registry_metadata(pattern_key)
    if metadata is None or metadata.planet_pair is None:
        return None
    return tuple(sorted(metadata.planet_pair))
