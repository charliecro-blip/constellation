"""Relationship-type weighting for detected patterns.

The detector identifies what is present. Weighting decides what should be
emphasized for this particular relationship type.
"""

from __future__ import annotations

import re

from .context import RelationshipContext
from .patterns import Pattern


ROMANTIC_BOOSTS = {
    "attraction": 8,
    "desire": 8,
    "affection": 6,
    "attraction_intensity": 6,
    "partnership": 6,
    "intimacy_depth": 6,
    "bond_structure": 4,
}

LONG_TERM_PARTNER_BOOSTS = {
    "partnership": 8,
    "bond_structure": 8,
    "relationship_structure": 8,
    "daily_life": 6,
    "home_roots": 6,
    "emotional_structure": 6,
    "emotional_body": 4,
}

FAMILY_BOOSTS = {
    "home_roots": 10,
    "emotional_body": 8,
    "emotional_structure": 8,
    "emotional_translation": 6,
    "daily_life": 6,
    "hidden_field": 4,
}

FRIEND_COLLABORATOR_BOOSTS = {
    "communication": 8,
    "public_direction": 6,
    "daily_life": 4,
    "relationship_identity": 4,
}

ADMIRED_FIGURE_BOOSTS = {
    "public_direction": 8,
    "identity_body": 6,
    "recognition": 4,
    "hidden_field": 4,
}


def boosts_for_context(context: RelationshipContext | None) -> dict[str, int]:
    if context is None:
        return {}

    relationship_type = context.relationship_type
    if relationship_type == "romantic" or relationship_type == "ex":
        return ROMANTIC_BOOSTS
    if relationship_type == "long_term_partner":
        return LONG_TERM_PARTNER_BOOSTS
    if relationship_type in {"parent", "child", "sibling"}:
        return FAMILY_BOOSTS
    if relationship_type in {"friend", "collaborator"}:
        return FRIEND_COLLABORATOR_BOOSTS
    if relationship_type == "admired_figure":
        return ADMIRED_FIGURE_BOOSTS
    return {}


def weight_patterns(patterns: list[Pattern], context: RelationshipContext | None = None) -> list[Pattern]:
    """Return patterns with relationship-type priority adjustments applied."""
    boosts = boosts_for_context(context)
    weighted: list[Pattern] = []
    for pattern in patterns:
        boost = boosts.get(pattern.category, 0)
        tier_boost = 0
        # Tier 1: central signatures
        if pattern.category == "angle_luminary":
            tier_boost += 18
        if pattern.key in {"synastry.venus_ascendant", "synastry.sun_moon", "synastry.moon_moon", "synastry.moon_venus"}:
            tier_boost += 12
        if pattern.category in {"fated_axis", "angle_structure"}:
            tier_boost += 8
        if pattern.key in {"synastry.venus_mars", "synastry.moon_saturn"}:
            tier_boost += 6
        if pattern.layer == "house_overlay":
            tier_boost -= 14

        # Tier 2: mechanics
        if pattern.key in {"synastry.mercury_mars", "synastry.venus_saturn", "synastry.mars_pluto", "synastry.venus_pluto", "synastry.mars_saturn", "composite.sun_saturn", "composite.moon_uranus", "composite.moon_saturn"}:
            tier_boost += 4

        # Tier 3 texture + down-rank exactness-only overclaims
        if pattern.key == "composite.mars_pluto":
            tier_boost -= 8

        orb_adjustment = 0
        ev = " ".join(pattern.evidence)
        orb_match = re.search(r"orb\s+([0-9]+(?:\.[0-9]+)?)", ev)
        if orb_match:
            orb = float(orb_match.group(1))
            if orb <= 1.0:
                orb_adjustment += 4
            elif orb <= 2.0:
                orb_adjustment += 2
            elif orb >= 5.0:
                orb_adjustment -= 2

        new_priority = min(100, max(0, pattern.priority + boost + tier_boost + orb_adjustment))
        weighted.append(pattern.model_copy(update={"priority": new_priority}))
    return sorted(weighted, key=lambda pattern: pattern.priority, reverse=True)
