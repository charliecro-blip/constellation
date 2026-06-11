"""Relationship-type weighting for detected patterns.

The detector identifies what is present. Weighting decides what should be
emphasized for this particular relationship type.
"""

from __future__ import annotations

import re

from .context import RelationshipContext
from .pattern_registry import convergence_category_for, get_pattern_metadata, planet_pair_for
from .scoring_weights import CONVERGENCE_MULTIPLIERS
from .patterns import Pattern


CAREER_KEYWORDS = {
    "career",
    "work",
    "public",
    "vocation",
    "reputation",
    "visibility",
    "calling",
    "ambition",
    "collaboration",
    "business",
    "professional",
    "creative project",
}
COMMUNICATION_KEYWORDS = {
    "communication",
    "conflict",
    "argument",
    "talking",
    "texting",
    "conversation",
    "misunderstanding",
    "mental connection",
}


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


def public_life_context_requested(context: RelationshipContext | None) -> bool:
    return any(keyword in _context_text(context) for keyword in CAREER_KEYWORDS)


def _career_context_requested(context: RelationshipContext | None) -> bool:
    return public_life_context_requested(context)


def _romantic_context(context: RelationshipContext | None) -> bool:
    return context is not None and context.relationship_type in {"romantic", "dating_exploring", "ex", "unresolved_connection"}


def communication_context_requested(context: RelationshipContext | None) -> bool:
    return any(keyword in _context_text(context) for keyword in COMMUNICATION_KEYWORDS)


def _directional_pair(pattern: Pattern) -> tuple[str, str, str, str] | None:
    if pattern.layer != "synastry":
        return None
    match = re.match(
        r"^(?P<left_owner>.+?)'s (?P<left_body>[A-Za-z ]+) .+ (?P<right_owner>.+?)'s (?P<right_body>[A-Za-z ]+)$",
        pattern.title,
    )
    if match is None:
        return None
    return (
        match.group("left_owner").strip().lower(),
        match.group("left_body").strip().lower().replace(" ", "_"),
        match.group("right_owner").strip().lower(),
        match.group("right_body").strip().lower().replace(" ", "_"),
    )


def _has_double_whammy(pattern: Pattern, patterns: list[Pattern]) -> bool:
    pair = planet_pair_for(pattern)
    directional = _directional_pair(pattern)
    if pair is None or directional is None:
        return False
    left_owner, left_body, right_owner, right_body = directional
    for other in patterns:
        if other.id == pattern.id or other.layer != "synastry":
            continue
        if planet_pair_for(other) != pair:
            continue
        other_directional = _directional_pair(other)
        if other_directional is None:
            continue
        other_left_owner, other_left_body, other_right_owner, other_right_body = other_directional
        if (
            other_left_owner == right_owner
            and other_right_owner == left_owner
            and other_left_body == left_body
            and other_right_body == right_body
        ):
            return True
    return False


def convergence_multiplier_for(pattern: Pattern, patterns: list[Pattern]) -> float:
    """Return the report-prioritization multiplier earned by repeated themes."""
    category = convergence_category_for(pattern)
    category_count = sum(1 for item in patterns if convergence_category_for(item) == category)
    multiplier = 1.0
    if category_count >= 3:
        multiplier *= CONVERGENCE_MULTIPLIERS["same_category_twice"]
    elif category_count == 2:
        multiplier *= CONVERGENCE_MULTIPLIERS["same_category_once"]

    if pattern.layer == "synastry" and any(
        item.layer == "composite" and convergence_category_for(item) == category for item in patterns
    ):
        multiplier *= CONVERGENCE_MULTIPLIERS["synastry_plus_composite"]

    if _has_double_whammy(pattern, patterns):
        multiplier *= CONVERGENCE_MULTIPLIERS["double_whammy"]

    if pattern.layer != "natal" and any(
        item.layer == "natal" and convergence_category_for(item) == category for item in patterns
    ):
        multiplier *= CONVERGENCE_MULTIPLIERS["natal_echo"]

    return min(multiplier, CONVERGENCE_MULTIPLIERS["cap"])


def weight_patterns(patterns: list[Pattern], context: RelationshipContext | None = None) -> list[Pattern]:
    """Return patterns with relationship-type priority adjustments applied."""
    boosts = boosts_for_context(context)
    weighted: list[Pattern] = []
    career_context = _career_context_requested(context)
    communication_context = communication_context_requested(context)
    romantic_context = _romantic_context(context)
    category_counts: dict[str, int] = {}
    for pattern in patterns:
        category_counts[pattern.category] = category_counts.get(pattern.category, 0) + 1
    for pattern in patterns:
        boost = boosts.get(pattern.category, 0)
        metadata = get_pattern_metadata(pattern.key)
        tier_boost = 0
        # Tier 1: central signatures
        is_mc_pattern = (
            metadata.category == "public_life"
            or "midheaven" in pattern.key
            or "Midheaven" in pattern.title
            or "MC/IC" in pattern.title
        )
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

        adjusted_priority = max(0, pattern.priority + boost + tier_boost + orb_adjustment)
        convergence_multiplier = convergence_multiplier_for(pattern, patterns)
        new_priority = min(100, round(adjusted_priority * convergence_multiplier))
        weighted.append(pattern.model_copy(update={"priority": new_priority}))
    return sorted(weighted, key=lambda pattern: pattern.priority, reverse=True)
