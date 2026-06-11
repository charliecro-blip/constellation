"""Relationship-type weighting for detected patterns.

The detector identifies what is present. Weighting decides what should be
emphasized for this particular relationship type.
"""

from __future__ import annotations

import re

from .context import RelationshipContext
from .patterns import Pattern
from .pattern_registry import convergence_category_for, planet_pair_for


CAREER_KEYWORDS = {"career", "work", "public", "vocation", "reputation", "visibility", "calling", "ambition"}
COMMUNICATION_KEYWORDS = {"communication", "talk", "text", "words", "argue", "argument", "conversation", "message"}


CONVERGENCE_MULTIPLIERS = {
    "same_category_once": 1.12,
    "same_category_twice": 1.25,
    "synastry_plus_composite": 1.25,
    "double_whammy": 1.30,
    "natal_echo": 1.15,
    "cap": 1.60,
}


def _synastry_direction(pattern: Pattern) -> str | None:
    if pattern.layer != "synastry":
        return None
    match = re.match(
        r"^(?P<left>.+)'s .+? (?:conjunct|opposite|square|trine|sextile|quincunx) (?P<right>.+)'s .+$",
        pattern.title,
    )
    if match is None:
        return None
    return f"{match.group('left').strip()}->{match.group('right').strip()}"


def _has_double_whammy(pattern: Pattern, all_patterns: list[Pattern]) -> bool:
    pair = planet_pair_for(pattern.key)
    direction = _synastry_direction(pattern)
    if pair is None or direction is None:
        return False
    left, right = direction.split("->", 1)
    reciprocal = f"{right}->{left}"
    return any(
        other is not pattern
        and other.layer == "synastry"
        and planet_pair_for(other.key) == pair
        and _synastry_direction(other) == reciprocal
        for other in all_patterns
    )


def _has_natal_echo(pattern: Pattern, all_patterns: list[Pattern]) -> bool:
    category = convergence_category_for(pattern.key, pattern.category)
    return any(
        other is not pattern
        and other.layer == "natal"
        and convergence_category_for(other.key, other.category) == category
        for other in all_patterns
    )


def convergence_multiplier(pattern: Pattern, all_patterns: list[Pattern]) -> float:
    """Return a conservative multiplier for themes repeated across layers.

    Isolated patterns stay at 1.0. Echoes are based on registry convergence
    categories rather than raw detector categories, so a synastry Venus/Pluto
    pattern can echo a composite Scorpio concentration as trust-depth material.
    """
    category = convergence_category_for(pattern.key, pattern.category)
    echoes = [
        other
        for other in all_patterns
        if other is not pattern and convergence_category_for(other.key, other.category) == category
    ]

    multiplier = 1.0
    if len(echoes) >= 2:
        multiplier *= CONVERGENCE_MULTIPLIERS["same_category_twice"]
    elif len(echoes) == 1:
        multiplier *= CONVERGENCE_MULTIPLIERS["same_category_once"]

    if pattern.layer == "synastry" and any(other.layer == "composite" for other in echoes):
        multiplier *= CONVERGENCE_MULTIPLIERS["synastry_plus_composite"]

    if _has_double_whammy(pattern, all_patterns):
        multiplier *= CONVERGENCE_MULTIPLIERS["double_whammy"]

    if _has_natal_echo(pattern, all_patterns):
        multiplier *= CONVERGENCE_MULTIPLIERS["natal_echo"]

    return min(multiplier, CONVERGENCE_MULTIPLIERS["cap"])


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
    if relationship_type in {"romantic", "dating_exploring", "ex", "unresolved_connection"}:
        return ROMANTIC_BOOSTS
    if relationship_type == "long_term_partner":
        return LONG_TERM_PARTNER_BOOSTS
    if relationship_type in {"parent", "child", "sibling", "family_other"}:
        return FAMILY_BOOSTS
    if relationship_type in {"friend", "collaborator"}:
        return FRIEND_COLLABORATOR_BOOSTS
    if relationship_type == "admired_figure":
        return ADMIRED_FIGURE_BOOSTS
    return {}


def _context_text(context: RelationshipContext | None) -> str:
    if context is None:
        return ""
    return " ".join(
        item
        for item in [context.user_question or "", context.origin_story or "", " ".join(context.known_themes)]
        if item
    ).lower()


def _career_context_requested(context: RelationshipContext | None) -> bool:
    return any(keyword in _context_text(context) for keyword in CAREER_KEYWORDS)


def _romantic_context(context: RelationshipContext | None) -> bool:
    return context is not None and context.relationship_type in {"romantic", "dating_exploring", "ex", "unresolved_connection"}


def _communication_context_requested(context: RelationshipContext | None) -> bool:
    return any(keyword in _context_text(context) for keyword in COMMUNICATION_KEYWORDS)


def weight_patterns(patterns: list[Pattern], context: RelationshipContext | None = None) -> list[Pattern]:
    """Return patterns with relationship-type priority adjustments applied."""
    boosts = boosts_for_context(context)
    weighted: list[Pattern] = []
    career_context = _career_context_requested(context)
    communication_context = _communication_context_requested(context)
    romantic_context = _romantic_context(context)
    category_counts: dict[str, int] = {}
    for pattern in patterns:
        category_counts[pattern.category] = category_counts.get(pattern.category, 0) + 1
    for pattern in patterns:
        boost = boosts.get(pattern.category, 0)
        tier_boost = 0
        # Tier 1: central signatures
        is_mc_pattern = "midheaven" in pattern.key or "Midheaven" in pattern.title or "MC/IC" in pattern.title
        if pattern.category == "angle_luminary" and not (romantic_context and is_mc_pattern and not career_context):
            tier_boost += 24
        if pattern.key in {"synastry.venus_ascendant", "synastry.sun_moon", "synastry.moon_moon", "synastry.moon_venus"}:
            tier_boost += 20
        if pattern.key.startswith("synastry.angle_ascendant_") or pattern.key.endswith("_ascendant"):
            tier_boost += 14
        if pattern.category in {"fated_axis", "angle_structure"}:
            tier_boost += 8
        if pattern.key in {"synastry.venus_mars", "synastry.venus_pluto", "synastry.mars_pluto", "synastry.moon_saturn", "synastry.venus_saturn"}:
            tier_boost += 10
        if pattern.layer == "house_overlay":
            tier_boost -= 14
            if "node" in pattern.id:
                tier_boost -= 18
        if pattern.key.startswith("composite.nodes_on_"):
            tier_boost += 10
        if pattern.key.startswith(("composite.stellium.", "composite.conjunction_cluster")):
            tier_boost += 6

        # Tier 2: mechanics
        if pattern.key in {"synastry.venus_saturn", "synastry.mars_pluto", "synastry.venus_pluto", "synastry.mars_saturn", "composite.sun_saturn", "composite.moon_uranus", "composite.moon_saturn", "composite.venus_mars", "composite.venus_pluto", "composite.mars_pluto"}:
            tier_boost += 4

        # Tier 3 texture + down-rank exactness-only overclaims
        if pattern.key == "composite.mars_pluto":
            tier_boost -= 8
        if romantic_context and is_mc_pattern and not career_context:
            tier_boost -= 24
        if romantic_context and pattern.category == "communication" and not communication_context and category_counts.get("communication", 0) < 3 and "Ascendant" not in pattern.title and "Moon" not in pattern.title and "Sun" not in pattern.title:
            tier_boost -= 26

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

        adjusted_priority = pattern.priority + boost + tier_boost + orb_adjustment
        multiplier = convergence_multiplier(pattern, patterns)
        new_priority = max(0, min(100, round(adjusted_priority * multiplier)))
        weighted.append(pattern.model_copy(update={"priority": new_priority}))
    return sorted(weighted, key=lambda pattern: pattern.priority, reverse=True)
