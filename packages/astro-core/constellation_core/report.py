"""Markdown relationship report generation.

See docs/astrology_doctrine/report_prioritization.md and
docs/astrology_doctrine/report_voice_guide.md for lead selection and voice
doctrine.
"""

from __future__ import annotations

import re
from collections import defaultdict

from pydantic import BaseModel, Field

from .asteroid_policy import ADVANCED_ASTEROIDS, DEFAULT_ASTEROID_ORB, DEFAULT_REPORT_ASTEROIDS, RELATIONSHIP_RELEVANT_HOUSES
from .context import RelationshipContext
from .interpretations import interpret_pattern
from .natal_profile import SIGN_ELEMENTS, SIGN_MODES
from .temperament import compact_temperament_text, compare_temperaments
from .pattern_registry import convergence_category_for, get_pattern_metadata
from .patterns import ASTEROID_CENTRAL_TARGETS, ASTEROID_POINTS, Pattern, _aspect_word, detect_relationship_patterns
from .chart import DEFAULT_HOUSE_SYSTEM
from .relationship import calculate_relationship
from .rulerships import relationship_house_rulers, relationship_significator_summary
from .schemas import (
    Aspect,
    AsteroidPolicyDiagnostics,
    BirthData,
    Chart,
    ChartSanityDiagnostics,
    DynamicDetail,
    RankedPatternSummary,
    RelationshipCalculation,
    ReportDiagnostics,
    ReportPatternDiagnostics,
    ReportSynthesisPacket,
)
from .weighting import communication_context_requested, public_life_context_requested, weight_patterns


class ReportSection(BaseModel):
    title: str
    body: str


class RelationshipReport(BaseModel):
    title: str
    sections: list[ReportSection]
    dynamic_details: list[DynamicDetail] = Field(default_factory=list)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.body)
            lines.append("")
        return "\n".join(lines).strip() + "\n"


def _patterns_by_category(patterns: list[Pattern]) -> dict[str, list[Pattern]]:
    grouped: dict[str, list[Pattern]] = defaultdict(list)
    for pattern in patterns:
        grouped[pattern.category].append(pattern)
    return grouped


def _orb_from_pattern(pattern: Pattern) -> float | None:
    match = re.search(r"orb\s+([0-9]+(?:\.[0-9]+)?)", " ".join(pattern.evidence))
    return float(match.group(1)) if match else None


def _strength_phrase(pattern: Pattern) -> str:
    orb = _orb_from_pattern(pattern)
    if orb is not None:
        if orb <= 0.25:
            return "Exact."
        if orb <= 1.0:
            return "Very close."
        if orb <= 3.0:
            return "Close."
        if orb <= 5.0 or pattern.priority >= 86:
            return "Moderate."
        return "Additional."
    if pattern.priority >= 92:
        return "Central."
    if pattern.priority >= 82:
        return "Strong."
    if pattern.priority >= 70:
        return "Moderate."
    return "Additional."


def _interpret_for_section(pattern: Pattern, section: str) -> str:
    if pattern.key == "composite.moon_uranus" and section in {"central", "overview"}:
        return "The emotional rhythm alternates between closeness and space, so stability has to be chosen rather than assumed."
    if pattern.key == "composite.moon_uranus" and section == "friction":
        return (
            "The Moon–Uranus square describes a rhythm problem: closeness and distance may alternate quickly, "
            "and attempts to stabilize the bond can trigger the need for space. The repair is not to eliminate "
            "the electricity, but to create agreements that let freedom and attachment coexist."
        )
    if section == "composite" and pattern.key.startswith("composite.stellium."):
        return _composite_stellium_language(pattern)
    if section == "composite" and pattern.key == "composite.conjunction_cluster":
        return _composite_cluster_language(pattern)
    if section == "composite" and pattern.key == "composite.t_square":
        return _composite_t_square_language(pattern)
    if section == "composite" and pattern.key == "composite.mars_pluto":
        return _composite_mars_pluto_language()
    return interpret_pattern(pattern)


def _signature_block(patterns: list[Pattern], *, limit: int, empty_message: str, section: str = "general") -> str:
    if not patterns:
        return empty_message

    lines: list[str] = []
    for pattern in patterns[:limit]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(f"{_strength_phrase(pattern)} {_interpret_for_section(pattern, section)}")
        lines.append("")
    return "\n".join(lines).strip()


MINOR_COMMUNICATION_KEYS = {"synastry.mercury_mars", "synastry.mercury_mercury"}


def _is_minor_communication(pattern: Pattern) -> bool:
    metadata = get_pattern_metadata(pattern.key)
    return (
        metadata.category == "communication_heat"
        or pattern.category == "communication"
        or pattern.key in MINOR_COMMUNICATION_KEYS
    )


def _is_public_life_pattern(pattern: Pattern) -> bool:
    metadata = get_pattern_metadata(pattern.key)
    return (
        metadata.category == "public_life"
        or "midheaven" in pattern.key.lower()
        or "midheaven" in pattern.title.lower()
        or "mc/ic" in pattern.title.lower()
    )


def _is_generic_composite_baseline(pattern: Pattern) -> bool:
    return pattern.layer == "composite" and pattern.key.startswith(("composite.sun.", "composite.moon."))


def _has_synastry_convergence(pattern: Pattern, patterns: list[Pattern]) -> bool:
    category = convergence_category_for(pattern)
    return any(
        other.layer == "synastry"
        and other.id != pattern.id
        and other.priority >= 70
        and convergence_category_for(other) == category
        for other in patterns
    )


def _is_major_composite_concentration(pattern: Pattern) -> bool:
    if pattern.layer != "composite" or pattern.priority < 88:
        return False
    if not pattern.key.startswith(("composite.stellium.", "composite.conjunction_cluster")):
        return False
    evidence_text = " ".join(pattern.evidence).lower()
    return any(body in evidence_text for body in ["sun", "moon", "venus", "mars", "saturn", "pluto"])


AFFIRMATIVE_LEAD_KEYS = {
    "synastry.venus_ascendant",
    "synastry.moon_venus",
    "synastry.sun_moon",
    "synastry.moon_moon",
    "synastry.venus_mars",
    "composite.venus_mars",
}
AFFIRMATIVE_OVERLAY_KEYS = {"overlay.house_5", "overlay.house_7"}
HARD_OPENING_CATEGORIES = {
    "communication",
    "emotional_structure",
    "bond_structure",
    "relationship_structure",
    "angle_structure",
    "emotional_intensity",
    "intensity",
    "action_structure",
    "emotional_variability",
}


def _is_affirmative_lead(pattern: Pattern) -> bool:
    if pattern.key in AFFIRMATIVE_LEAD_KEYS or pattern.key in AFFIRMATIVE_OVERLAY_KEYS:
        return True
    title = pattern.title.lower()
    if pattern.layer == "house_overlay" and (" 7th house" in title or " 5th house" in title):
        return True
    if "venus" in title and ("ascendant" in title or "descendant" in title):
        return True
    return False


def _is_hard_opening(pattern: Pattern) -> bool:
    return pattern.layer == "composite" and pattern.category in HARD_OPENING_CATEGORIES


def is_lead_eligible(
    pattern: Pattern, context: RelationshipContext | None = None, patterns: list[Pattern] | None = None
) -> bool:
    metadata = get_pattern_metadata(pattern.key)
    all_patterns = patterns or [pattern]

    if pattern.layer == "house_overlay" or _is_generic_composite_baseline(pattern):
        return False
    if _is_minor_communication(pattern):
        return communication_context_requested(context)
    if _is_public_life_pattern(pattern):
        return public_life_context_requested(context)
    if pattern.layer == "composite":
        if _is_major_composite_concentration(pattern):
            return True
        return metadata.lead_eligible and _has_synastry_convergence(pattern, all_patterns)
    return metadata.lead_eligible


def _is_major_fallback_pattern(pattern: Pattern, context: RelationshipContext | None = None) -> bool:
    metadata = get_pattern_metadata(pattern.key)
    if pattern.layer == "house_overlay" or _is_generic_composite_baseline(pattern):
        return False
    if _is_minor_communication(pattern):
        return False
    if _is_public_life_pattern(pattern) and not public_life_context_requested(context):
        return context is None and pattern.priority >= 84
    return metadata.tier <= 2 or pattern.priority >= 84


def _central_patterns(
    patterns: list[Pattern], context: RelationshipContext | None = None
) -> list[Pattern]:
    candidates = [pattern for pattern in patterns if not _is_generic_composite_baseline(pattern)]
    affirmative = [pattern for pattern in candidates if _is_affirmative_lead(pattern)]
    lead_candidates = [
        pattern
        for pattern in candidates
        if pattern.layer != "house_overlay" and is_lead_eligible(pattern, context, patterns)
    ]

    hard_lead = lead_candidates[0] if lead_candidates else None
    should_use_affirmative = (
        affirmative
        and not public_life_context_requested(context)
        and (
            hard_lead is None
            or _is_hard_opening(hard_lead)
            or affirmative[0].priority >= hard_lead.priority - 18
        )
    )
    if should_use_affirmative:
        primary = affirmative[0]
    else:
        primary = hard_lead or next(
            (
                pattern
                for pattern in candidates
                if pattern.layer != "house_overlay" and _is_major_fallback_pattern(pattern, context)
            ),
            None,
        )
    if primary is None:
        return []

    supporting = [pattern for pattern in candidates if pattern.id != primary.id]
    # Keep the opening synthetic: after an affirmative lead, show another relational pull before the pressure.
    if _is_affirmative_lead(primary):
        supporting = sorted(supporting, key=lambda p: (not _is_affirmative_lead(p), -p.priority))
    return [primary, *supporting][:5]


def _display_body(body: str) -> str:
    return body.replace("_", " ").title()


def _ordinal(number: int) -> str:
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _placement_phrase(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    if placement is None:
        return None
    house = f" in the {_ordinal(placement.house)} house" if placement.house is not None else ""
    return f"{_display_body(body)} in {placement.sign}{house}"


def _angle_phrase(chart: Chart, angle: str) -> str | None:
    placement = chart.angles.get(angle)
    if placement is None:
        return None
    label = "Ascendant" if angle == "ascendant" else "Midheaven"
    return f"{label} in {placement.sign}"


def _descendant_phrase(chart: Chart) -> str | None:
    asc = chart.angles.get("ascendant")
    if asc is None:
        return None
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    desc_sign = signs[(asc.sign_index + 6) % 12]
    return f"Descendant in {desc_sign}"


def _profile_body(chart: Chart, patterns: list[Pattern]) -> str:
    anchors = [item for item in [_angle_phrase(chart, "ascendant"), _descendant_phrase(chart)] if item]
    relational = [item for item in (_placement_phrase(chart, body) for body in ["sun", "moon", "venus", "mars"]) if item]
    houses = [item for item in relational if any(f" {_ordinal(house)} house" in item for house in [5, 7, 8])]

    lines: list[str] = []
    if anchors:
        lines.append(f"- **Attachment style:** {chart.name} meets relationship through {', '.join(anchors)}. The Ascendant/Descendant axis describes how closeness begins, what feels inviting, and what can get projected onto a partner.")
        axis = relationship_significator_summary(chart).get("relationship_axis", {})
        desc = axis.get("descendant")
        desc_ruler = (axis.get("descendant_ruler") or {}) if isinstance(axis, dict) else {}
        if desc and desc_ruler:
            house = f" in the {_ordinal(desc_ruler.get('house'))} house" if desc_ruler.get("house") else ""
            lines.append(f"- **Partnership ruler:** With {desc} on the Descendant, {chart.name} often meets partnership through {_display_body(str(desc_ruler.get('planet', '')))} themes. The 7th-house ruler placed in {desc_ruler.get('sign')}{house} shows where mirroring, loyalty, boundaries, attraction, or negotiation become personally specific rather than generic.")
    else:
        lines.append(f"- **Attachment style:** {chart.name}'s birth time data does not give a reliable Ascendant/Descendant axis here, so this profile leans on the relational planets rather than angles.")

    moon = _placement_phrase(chart, "moon")
    moon_placement = chart.placements.get("moon")
    if moon_placement:
        moon_tone = _element_mode(moon_placement.sign)
        moon_texture = _moon_temperament_texture(moon_placement.sign)
        lines.append(
            f"- **Emotional need:** {moon} is a {moon_tone} emotional style. {moon_texture} Regulation, safety, and reassurance should be read through that lived tone rather than reduced to a generic need for closeness."
        )
    else:
        lines.append("- **Emotional need:** The Moon placement is not available in this chart extract, so regulation, safety, and reassurance should not be over-specified.")

    desire_parts = [item for item in [_placement_phrase(chart, "venus"), _placement_phrase(chart, "mars")] if item]
    if desire_parts:
        lines.append(f"- **Desire pattern:** {', '.join(desire_parts)} describes how affection, pursuit, attraction, and embodied chemistry tend to move.")

    sun = _placement_phrase(chart, "sun")
    if sun:
        lines.append(f"- **What gets protected:** {sun} points to the selfhood {chart.name} is trying to keep intact inside intimacy, especially when a bond asks for compromise.")

    devotion_markers = [
        item
        for item in (_placement_phrase(chart, body) for body in sorted(DEFAULT_REPORT_ASTEROIDS))
        if item and any(f" {_ordinal(house)} house" in item for house in RELATIONSHIP_RELEVANT_HOUSES)
    ]
    if devotion_markers:
        lines.append(f"- **Devotion and vulnerability markers:** {', '.join(devotion_markers)} adds specific texture around commitment, care, tenderness, or private focus.")

    if houses:
        terrain_parts: list[str] = []
        house_numbers = {chart.placements[item].house for item in chart.placements if chart.placements[item].house in {5, 7, 8}}
        if 5 in house_numbers:
            terrain_parts.append("5th-house emphasis makes romance, play, creative risk, pleasure, and the courage to be visibly delighted part of the relationship story")
        if 7 in house_numbers:
            terrain_parts.append("7th-house emphasis makes direct encounter, mirroring, projection, and negotiated choice unavoidable")
        if 8 in house_numbers:
            terrain_parts.append("8th-house emphasis brings trust, exposure, shared consequence, and the need for honest vulnerability")
        terrain = "; ".join(terrain_parts)
        lines.append(
            f"- **Repeated relationship terrain:** {chart.name}'s relational planets emphasize {', '.join(houses)}. {terrain}. The pattern is not a simple house list; it shows how pleasure, partnership, and intimacy can become intertwined under real relational pressure."
        )
    else:
        lines.append("- **Repeated relationship terrain:** Watch how affection, desire, and self-protection repeat under stress; those patterns will matter more than a full natal inventory here.")

    saturn_contacts = [pattern.title for pattern in patterns if pattern.layer == "synastry" and "Saturn" in pattern.title and any(body in pattern.title for body in ["Moon", "Venus", "Mars"])]
    if saturn_contacts:
        lines.append(f"- **Saturn sensitivity:** Contacts such as {saturn_contacts[0]} make timing, restraint, duty, or fear of rejection part of the relational learning curve.")

    return "\n".join(lines[:6])


def _is_angle(point: str) -> bool:
    return point.lower() in {"ascendant", "midheaven"}


def _activator_for_aspect(aspect: Aspect) -> str:
    point_a = aspect.point_a.lower()
    point_b = aspect.point_b.lower()
    if _is_angle(point_a) and not _is_angle(point_b):
        return "person_b"
    return "person_a"


def _pattern_for_aspect(patterns: list[Pattern], aspect: Aspect) -> Pattern | None:
    point_a = _display_body(aspect.point_a)
    point_b = _display_body(aspect.point_b)
    aspect_word = {"conjunction": "conjunct", "opposition": "opposite"}.get(aspect.aspect, aspect.aspect)
    needle = f"{point_a} {aspect_word} "
    tail = point_b
    for pattern in patterns:
        if pattern.layer == "synastry" and needle in pattern.title and pattern.title.endswith(tail):
            return pattern
    return None


def _directional_patterns(relationship: RelationshipCalculation, patterns: list[Pattern], activator: str) -> list[Pattern]:
    selected: list[Pattern] = []
    seen: set[str] = set()
    for aspect in relationship.synastry_aspects:
        if _activator_for_aspect(aspect) != activator:
            continue
        pattern = _pattern_for_aspect(patterns, aspect)
        if pattern is not None and pattern.id not in seen:
            selected.append(pattern)
            seen.add(pattern.id)
    for pattern in patterns:
        if pattern.layer != "house_overlay" or pattern.id in seen:
            continue
        wants_a = activator == "person_a" and f"{relationship.person_a.name}'s" in pattern.title and f"in {relationship.person_b.name}'s" in pattern.title
        wants_b = activator == "person_b" and f"{relationship.person_b.name}'s" in pattern.title and f"in {relationship.person_a.name}'s" in pattern.title
        if wants_a or wants_b:
            selected.append(pattern)
            seen.add(pattern.id)
    sorted_selected = sorted(selected, key=lambda item: item.priority, reverse=True)
    top = sorted_selected[:4]
    has_aspect = any(pattern.layer == "synastry" for pattern in top)
    has_overlay = any(pattern.layer == "house_overlay" for pattern in top)
    if not has_overlay:
        overlay = next(
            (
                pattern
                for pattern in sorted_selected[4:]
                if pattern.layer == "house_overlay" and pattern.key in {"overlay.house_5", "overlay.house_7", "overlay.house_8"}
            ),
            None,
        )
        if overlay is not None:
            top = [*top[:3], overlay]
    if not has_aspect:
        aspect = next((pattern for pattern in sorted_selected[4:] if pattern.layer == "synastry"), None)
        if aspect is not None:
            top = [*top[:3], aspect]
    if sum(1 for pattern in top[:3] if pattern.layer == "house_overlay") > 1:
        aspect = next((pattern for pattern in sorted_selected if pattern.layer == "synastry" and pattern not in top[:3]), None)
        if aspect is not None:
            first_overlay_index = next(i for i, pattern in enumerate(top[:3]) if pattern.layer == "house_overlay")
            replace_index = next(
                (i for i in range(2, -1, -1) if i != first_overlay_index and top[i].layer == "house_overlay"),
                None,
            )
            if replace_index is not None:
                top[replace_index] = aspect
    return top


RELATIONAL_ROLE_BY_BODY = {
    "sun": "identity, vitality, and the need to be recognized",
    "moon": "emotional safety, instinct, and the way care is received",
    "mercury": "language, perception, and the pace of interpretation",
    "venus": "affection, attraction, pleasure, and relational receptivity",
    "mars": "desire, initiative, heat, and embodied pursuit",
    "saturn": "limits, timing, responsibility, and fear of failure",
    "pluto": "depth, power, exposure, and transformation",
}


def _natal_role(body: str) -> str:
    return RELATIONAL_ROLE_BY_BODY.get(body.lower(), "a natal function that becomes activated in relationship")


def _possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def _placement_context(chart: Chart, body: str) -> str:
    placement = chart.placements.get(body.lower())
    if placement is None:
        return f"{_possessive(chart.name)} {_display_body(body)}"
    house = f" in the {_ordinal(placement.house)} house" if placement.house is not None else ""
    tone = _element_mode(placement.sign)
    return f"{_possessive(chart.name)} {placement.sign} {_display_body(body)}{house} ({tone})"


def _synastry_aspect_for_pattern(relationship: RelationshipCalculation, pattern: Pattern) -> Aspect | None:
    for aspect in relationship.synastry_aspects:
        if _pattern_for_aspect([pattern], aspect) is pattern:
            return aspect
    return None


def _natalized_synastry_language(relationship: RelationshipCalculation, pattern: Pattern, section: str) -> str:
    if pattern.layer != "synastry":
        return _interpret_for_section(pattern, section)
    aspect = _synastry_aspect_for_pattern(relationship, pattern)
    if aspect is None:
        return _interpret_for_section(pattern, section)
    point_a = aspect.point_a.lower()
    point_b = aspect.point_b.lower()
    aspect_word = _aspect_word(aspect.aspect)
    if point_a == "ascendant":
        desc_note = " This also works as a Descendant/partnership-axis contact when the aspect is an opposition, so attraction can feel like direct mirroring rather than background chemistry." if aspect.aspect == "opposition" and point_b == "venus" else ""
        return (
            f"{_possessive(relationship.person_a.name)} Ascendant axis meets {_placement_context(relationship.person_b, point_b)} by {aspect_word}. "
            f"The {point_b.title()} person activates how the Ascendant person enters relationship, is seen, and recognizes partnership cues.{desc_note} "
            f"Because {_display_body(point_b)} carries {_natal_role(point_b)}, this is felt through both body language and relationship choice."
        )
    if point_b == "ascendant":
        desc_note = " This also touches the Descendant/partnership axis when the aspect is an opposition, so the pull can feel relationally explicit." if aspect.aspect == "opposition" and point_a == "venus" else ""
        return (
            f"{_placement_context(relationship.person_a, point_a)} meets {_possessive(relationship.person_b.name)} Ascendant axis by {aspect_word}. "
            f"The planet person activates how the Ascendant person enters relationship and recognizes the other across the partnership axis.{desc_note} "
            f"Because {_display_body(point_a)} carries {_natal_role(point_a)}, the signature is not generic; it arrives through that natal style."
        )
    if point_a in RELATIONAL_ROLE_BY_BODY or point_b in RELATIONAL_ROLE_BY_BODY:
        return (
            f"{_placement_context(relationship.person_a, point_a)} meets {_placement_context(relationship.person_b, point_b)} by {aspect_word}. "
            f"This is not only a {_display_body(point_a)}/{_display_body(point_b)} contact: it links {_natal_role(point_a)} with {_natal_role(point_b)}, so the attraction or friction is filtered through each person's natal sign, house, and relationship role. "
            f"{_interpret_for_section(pattern, section)}"
        )
    return _interpret_for_section(pattern, section)


def _interpret_pattern_for_relationship(relationship: RelationshipCalculation, pattern: Pattern, section: str) -> str:
    if pattern.layer == "synastry":
        return _natalized_synastry_language(relationship, pattern, section)
    return _interpret_for_section(pattern, section)


def _overlay_language(pattern: Pattern) -> str:
    title = pattern.title
    if " 7th house" in title:
        if "Venus" in title:
            return f"{title} is a direct partnership signature: affection, beauty, and receptivity land in the house of mirroring, choice, and one-to-one encounter. Attraction may feel obvious because the Venus person reflects what the house person recognizes as relational."
        return f"{title} emphasizes partnership mirroring. The planet person does not simply add a topic; they activate the house person's 7th-house field of direct encounter, projection, reciprocity, and negotiated commitment."
    if " 5th house" in title:
        return f"{title} brings romance, play, creative risk, pleasure, and the feeling of being enlivened into the foreground."
    if " 8th house" in title:
        return f"{title} moves the bond toward trust, exposure, shared vulnerability, and psychological consequence."
    return interpret_pattern(pattern)


def _signature_block_for_relationship(relationship: RelationshipCalculation, patterns: list[Pattern], *, limit: int, empty_message: str, section: str = "general") -> str:
    if not patterns:
        return empty_message
    lines: list[str] = []
    for pattern in patterns[:limit]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        language = _overlay_language(pattern) if pattern.layer == "house_overlay" else _interpret_pattern_for_relationship(relationship, pattern, section)
        lines.append(f"{_strength_phrase(pattern)} {language}")
        lines.append("")
    return "\n".join(lines).strip()


def _element(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    return SIGN_ELEMENTS.get(placement.sign) if placement else None


def _mode(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    return SIGN_MODES.get(placement.sign) if placement else None


def _moon_temperament_texture(sign: str) -> str:
    element = SIGN_ELEMENTS.get(sign)
    mode = SIGN_MODES.get(sign)
    if sign == "Capricorn":
        return "Care often moves through reliability, competence, kept promises, and proof over time; sensitivity protected by self-control may be contained, and loyalty deepens once safety is earned."
    if sign == "Gemini":
        return "Feeling often processes through language, movement, curiosity, responsiveness, and naming what is happening; variability does not automatically mean shallowness."
    if element == "earth":
        return "Care tends to need consistency, embodiment, practical follow-through, and time to trust what is reliable."
    if element == "air":
        return "Care tends to need language, perspective, responsiveness, and enough room to think feelings through."
    if element == "fire":
        return "Care tends to need warmth, directness, movement, courage, and permission for feeling to become action."
    if element == "water":
        return "Care tends to need attunement, privacy, memory, softness, and room for feelings to arrive before they are explained."
    if mode == "fixed":
        return "Emotional safety often grows through continuity and consistency."
    return "Emotional safety is shaped by the sign's element and modality."


def _comparison_notes(relationship: RelationshipCalculation) -> list[str]:
    a_chart = relationship.person_a
    b_chart = relationship.person_b
    notes: list[str] = []
    a_moon = a_chart.placements.get("moon")
    b_moon = b_chart.placements.get("moon")
    if a_moon and b_moon:
        if a_moon.sign == b_moon.sign:
            notes.append("emotionally familiar")
        elif _element(a_chart, "moon") == _element(b_chart, "moon"):
            notes.append("emotionally legible")
        else:
            notes.append("emotionally mismatched enough to need translation")
    for body, label in [("venus", "affection"), ("mars", "desire")]:
        a_place = a_chart.placements.get(body)
        b_place = b_chart.placements.get(body)
        if not a_place or not b_place:
            continue
        if a_place.sign == b_place.sign:
            notes.append(f"shared {label} language")
        elif _element(a_chart, body) == _element(b_chart, body):
            notes.append(f"compatible {label} pacing")
    a_sun = a_chart.placements.get("sun")
    b_sun = b_chart.placements.get("sun")
    if a_sun and b_moon and a_sun.sign == b_moon.sign:
        notes.append(f"{b_chart.name}'s Moon recognizes {a_chart.name}'s Sun tone")
    if b_sun and a_moon and b_sun.sign == a_moon.sign:
        notes.append(f"{a_chart.name}'s Moon recognizes {b_chart.name}'s Sun tone")
    modes = [_mode(chart, body) for chart in [a_chart, b_chart] for body in ["sun", "moon", "venus", "mars"]]
    mode_counts = {mode: modes.count(mode) for mode in set(modes) if mode}
    if mode_counts:
        mode, count = max(mode_counts.items(), key=lambda item: item[1])
        if count >= 4:
            notes.append(f"shared {mode} emphasis")
    return notes[:3]


def _overview(relationship: RelationshipCalculation, central: list[Pattern], composite: list[Pattern], patterns: list[Pattern]) -> str:
    a = relationship.person_a.name
    b = relationship.person_b.name
    affirmative = [pattern for pattern in central if _is_affirmative_lead(pattern)] or [pattern for pattern in patterns if _is_affirmative_lead(pattern)]
    overlays = [pattern for pattern in patterns if pattern.layer == "house_overlay" and pattern.priority >= 48]
    partnership_overlays = [pattern for pattern in overlays if pattern.key in {"overlay.house_5", "overlay.house_7"}]
    friction = [
        pattern
        for pattern in patterns
        if pattern.category
        in {
            "communication",
            "emotional_structure",
            "bond_structure",
            "relationship_structure",
            "angle_structure",
            "emotional_intensity",
            "emotional_activation",
            "embodied_activation",
            "intensity",
            "action_structure",
            "emotional_variability",
        }
    ]
    comparison_notes = _comparison_notes(relationship)
    temperament_text = compact_temperament_text(compare_temperaments(relationship.person_a, relationship.person_b))

    paragraphs: list[str] = []
    if affirmative:
        lead = affirmative[0]
        lead_text = _overlay_language(lead) if lead.layer == "house_overlay" else _interpret_pattern_for_relationship(relationship, lead, "overview")
        paragraphs.append(
            f"What first draws attention in the field between {a} and {b} is {lead.title}. {lead_text} "
            "This gives the report an affirmative starting point: recognition, attraction, mirroring, pleasure, or relational aliveness should be read before the heavier mechanics are allowed to define the whole bond."
        )
    elif central:
        primary = central[0]
        paragraphs.append(
            f"The central story between {a} and {b} is carried by {primary.title}. "
            f"{_interpret_pattern_for_relationship(relationship, primary, 'overview')} "
            "Read it as the broad relational field rather than as an isolated technical aspect."
        )
    else:
        paragraphs.append(
            f"The strongest organizing themes between {a} and {b} come from repeated contact patterns rather than one spectacular signature."
        )

    if partnership_overlays:
        paragraphs.append(
            f"The bond also has clear house-overlay weight: {partnership_overlays[0].title}. "
            f"{_overlay_language(partnership_overlays[0])} "
            "This describes where the connection lands in lived experience, not just what aspects are mathematically exact."
        )
    elif comparison_notes:
        paragraphs.append(
            "Chart-to-chart comparison makes the field feel "
            + ", ".join(comparison_notes)
            + ". Use this as synthesis support, not as a score."
        )
    elif temperament_text:
        paragraphs.append(
            "The clearest temperament support is " + temperament_text + ". This is useful only as translation context for the selected dynamics, not as a standalone element reading."
        )

    pressure = next((pattern for pattern in friction if pattern not in affirmative), None)
    if pressure:
        paragraphs.append(
            f"The pressure enters through {pressure.title}. {_interpret_pattern_for_relationship(relationship, pressure, 'friction')} "
            "This names the complexity without making friction the opening thesis."
        )
    elif composite:
        comp = composite[0]
        paragraphs.append(
            f"The composite field adds {comp.title}. {_interpret_for_section(comp, 'composite')} "
            "This describes what the bond tends to produce when both charts are read as one shared weather system."
        )

    repair_source = pressure or (friction[0] if friction else None)
    if repair_source:
        repair = _repair_principle_for_pattern(repair_source)
        paragraphs.append(
            f"The growth practice is concrete: {repair} The relationship is best served when sweetness, charge, and repair capacity are developed together."
        )

    return "\n\n".join(paragraphs[:4])


def _composite_stellium_language(pattern: Pattern) -> str:
    sign = pattern.key.rsplit(".", 1)[-1].title()
    themes = {
        "Capricorn": "structure, timing, responsibility, durability, and real-world consequence",
        "Scorpio": "privacy, intensity, trust, emotional depth, and transformation",
        "Cancer": "care, memory, belonging, protectiveness, and emotional safety",
        "Libra": "negotiation, reciprocity, aesthetics, and the need to keep the relational mirror clean",
        "Aries": "directness, heat, initiative, courage, and quick ignition",
        "Taurus": "steadiness, touch, loyalty, pleasure, and the slow building of trust",
        "Gemini": "language, curiosity, nervous-system movement, and ongoing translation",
        "Leo": "visibility, play, pride, generosity, and creative recognition",
        "Virgo": "discernment, service, repair, daily practice, and useful precision",
        "Sagittarius": "movement, candor, belief, distance, and shared horizons",
        "Aquarius": "friendship, difference, space, experimentation, and systems of belonging",
        "Pisces": "porosity, imagination, compassion, longing, and careful boundaries",
    }.get(sign, "shared emphasis, pacing, expectation, and repair")
    return f"This concentration makes the composite field speak in {sign} terms: {themes}. The listed bodies operate less like separate details and more like one shared climate."


def _composite_cluster_language(pattern: Pattern) -> str:
    title = pattern.title.lower()
    if all(body in title for body in ["venus", "mercury", "pluto"]):
        return "Affection, speech, and depth/compulsion are braided together: tenderness is hard to separate from what is said, probed, desired, or withheld."
    return "The conjunction cluster concentrates several relationship functions into one shared operating system, so conversations, desire, timing, and pressure tend to activate together rather than arriving as neat separate issues."


def _composite_t_square_language(pattern: Pattern) -> str:
    evidence = pattern.evidence[0] if pattern.evidence else "one planet squares an opposition"
    return (
        f"The pressure structure is specific: {evidence}. "
        "A T-square works through an opposition that keeps two needs polarized while the apex/pressure point becomes the place where tension discharges. "
        "Behaviorally, this can create triangle-like repetition, urgency, or the sense that one issue must solve the whole relationship. Repair asks the couple to name both ends of the opposition and give the pressure point a deliberate outlet instead of acting it out."
    )


def _composite_mars_pluto_language() -> str:
    return (
        "Composite Mars conjunct Pluto gives the shared field high charge: desire, anger, will, sexuality, and creative force can amplify quickly. "
        "The bond may resist staying casual because power and vulnerability become intertwined; handled unconsciously this can escalate, but handled consciously it supports transformation. "
        "Consent, pacing, trust, and a clear way to de-escalate are part of the chemistry itself."
    )


def _composite_patterns(patterns: list[Pattern]) -> list[Pattern]:
    synthesis_prefixes = (
        "composite.nodes_on_",
        "composite.planet_on_angle",
        "composite.stellium.",
        "composite.conjunction_cluster",
        "composite.grand_trine",
        "composite.t_square",
    )
    synthesis = [pattern for pattern in patterns if pattern.layer == "composite" and pattern.key.startswith(synthesis_prefixes)]
    hard_aspects = [
        pattern for pattern in patterns
        if pattern.layer == "composite"
        and pattern.key not in {item.key for item in synthesis}
        and pattern.category in {"emotional_variability", "emotional_structure", "bond_structure", "relationship_structure", "desire", "intensity"}
        and (pattern.priority >= 84 or pattern.category in {"emotional_variability", "emotional_structure"})
    ]
    specific_sign_texture = [
        pattern for pattern in patterns
        if pattern.layer == "composite"
        and pattern.key.startswith(("composite.sun.", "composite.moon."))
        and pattern.priority >= 82
    ]
    return (synthesis + hard_aspects + specific_sign_texture)[:5]


def _composite_field_body(composite: list[Pattern]) -> str:
    if not composite:
        return "Composite patterns were not strong enough to lead this report."
    ordered = sorted(
        composite,
        key=lambda pattern: (
            0 if pattern.key.startswith("composite.moon.") else
            1 if pattern.key.startswith(("composite.stellium.", "composite.conjunction_cluster")) else
            2 if pattern.key == "composite.t_square" else
            3 if pattern.key == "composite.mars_pluto" else
            4 if pattern.key == "composite.sun_saturn" else
            5,
            -pattern.priority,
        ),
    )[:5]
    paragraphs: list[str] = []
    for index, pattern in enumerate(ordered):
        lead = "The composite field begins with" if index == 0 else "That leads into" if index == 1 else "A further layer is"
        paragraphs.append(f"### {pattern.title}\n\n{_strength_phrase(pattern)} {lead} {pattern.title}: {_interpret_for_section(pattern, 'composite')}")
    return "\n\n".join(paragraphs)



def _detail_kind(pattern: Pattern) -> str:
    if pattern.layer == "house_overlay":
        return "house_overlay"
    if pattern.layer == "composite":
        return "composite_pattern" if pattern.key in {"composite.t_square", "composite.conjunction_cluster"} or pattern.key.startswith("composite.stellium.") else "composite_aspect"
    if "angle" in pattern.key or "ascendant" in pattern.key or "midheaven" in pattern.key:
        return "angle_contact"
    return "synastry_aspect"


def _element_mode(sign: str) -> str:
    mode = SIGN_MODES.get(sign)
    element = SIGN_ELEMENTS.get(sign)
    return f"{mode} {element}" if mode and element else sign


def _placement_detail_context(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    if placement is None:
        return None
    house = f" in the {_ordinal(placement.house)} house" if placement.house is not None else ""
    role = {
        "sun": "identity and vitality",
        "moon": "safety needs and emotional regulation",
        "mercury": "language, listening, and nervous-system pacing",
        "venus": "affection, pleasure, attraction, and receiving",
        "mars": "desire, assertion, conflict style, and action",
        "saturn": "limits, accountability, and time",
        "pluto": "power, vulnerability, and deep change",
    }.get(body, "relational sensitivity")
    return f"{chart.name}'s {placement.sign} {_display_body(body)}{house} ({_element_mode(placement.sign)}) is a channel for {role}."


def _temperament_bridge_for_aspect(relationship: RelationshipCalculation, aspect: Aspect) -> str:
    a = relationship.person_a.placements.get(aspect.point_a.lower())
    b = relationship.person_b.placements.get(aspect.point_b.lower())
    if not a or not b:
        return ""
    a_tone = _element_mode(a.sign)
    b_tone = _element_mode(b.sign)
    if a_tone == b_tone:
        return f"Both channels share {a_tone}, so the aspect has a common operating language even when the contact is tense."
    if SIGN_MODES.get(a.sign) == SIGN_MODES.get(b.sign):
        return f"This is {a_tone} meeting {b_tone}: the shared {SIGN_MODES.get(a.sign)} modality can adapt or shift, while the element difference asks for translation."
    return f"This is {a_tone} meeting {b_tone}, so pacing and elemental style are part of the lived contact."


def _aspect_for_pattern(relationship: RelationshipCalculation, pattern: Pattern) -> Aspect | None:
    for aspect in relationship.synastry_aspects:
        title = f"{relationship.person_a.name}'s {_display_body(aspect.point_a)} {_aspect_word(aspect.aspect)} {relationship.person_b.name}'s {_display_body(aspect.point_b)}"
        if title == pattern.title:
            return aspect
    for aspect in relationship.composite_aspects:
        title = f"Composite {_display_body(aspect.point_a)} {_aspect_word(aspect.aspect)} {_display_body(aspect.point_b)}"
        if title == pattern.title:
            return aspect
    return None


def _related_titles(pattern: Pattern, all_patterns: list[Pattern]) -> list[str]:
    tokens = {part for part in pattern.key.replace('.', '_').split('_') if part in {"moon", "mercury", "venus", "mars", "saturn", "pluto", "sun"}}
    related = []
    for other in all_patterns:
        if other.id == pattern.id:
            continue
        other_tokens = set(other.key.replace('.', '_').split('_'))
        if tokens & other_tokens or convergence_category_for(other) == convergence_category_for(pattern):
            related.append(other.title)
        if len(related) >= 4:
            break
    return related


def _relationship_ruler_note_for_aspect(relationship: RelationshipCalculation, aspect: Aspect) -> str | None:
    rulers = {
        "person_a": relationship_house_rulers(relationship.person_a),
        "person_b": relationship_house_rulers(relationship.person_b),
    }
    labels = {
        "descendant_ruler": "Descendant/7th-house ruler",
        "romance_ruler": "5th-house ruler",
        "intimacy_ruler": "8th-house ruler",
        "ascendant_ruler": "Ascendant ruler",
    }
    checks = [("person_b", aspect.point_b.lower(), relationship.person_b.name), ("person_a", aspect.point_a.lower(), relationship.person_a.name)]
    for owner, point, name in checks:
        for key, ruler in rulers[owner].items():
            if point == ruler and key in labels:
                return f"This is not only a generic planet contact: {_display_body(ruler)} rules {name}'s {labels[key]}, so the aspect touches a chart-specific relationship significator."
    return None


def _dynamic_detail_for_pattern(relationship: RelationshipCalculation, pattern: Pattern, all_patterns: list[Pattern], section: str) -> DynamicDetail:
    aspect = _aspect_for_pattern(relationship, pattern)
    technical: list[str] = [*pattern.evidence]
    context_bits: list[str] = []
    if aspect and pattern.layer == "synastry":
        ruler_note = _relationship_ruler_note_for_aspect(relationship, aspect)
        for chart, body in [(relationship.person_a, aspect.point_a.lower()), (relationship.person_b, aspect.point_b.lower())]:
            if bit := _placement_detail_context(chart, body):
                context_bits.append(bit)
                technical.append(bit)
        if len(context_bits) == 2:
            bridge = _temperament_bridge_for_aspect(relationship, aspect)
            read_more = f"{context_bits[0]} {context_bits[1]} {bridge} The {_aspect_word(aspect.aspect)} is therefore not just a generic {aspect.point_a}/{aspect.point_b} contact; it describes how these two natal channels meet in this particular bond."
            if ruler_note:
                read_more += " " + ruler_note
        else:
            read_more = "This contact matters because it ties a central synastry signature to the lived style of each person's natal chart rather than treating the aspect in isolation."
            if ruler_note:
                read_more += " " + ruler_note
    elif pattern.layer == "house_overlay":
        read_more = "This overlay shows where one person's planet enters the other's lived house terrain. It matters most when it repeats a larger motif in the map rather than standing alone."
    elif pattern.key == "composite.t_square":
        evidence = pattern.evidence[0] if pattern.evidence else pattern.title
        read_more = f"{evidence}. In a T-square, the opposition names the polarity the relationship keeps trying to hold, while the apex or pressure point shows where that tension tends to discharge behaviorally. The repair principle is to slow the apex response, name both sides of the opposition, and connect this pressure back to matching synastry themes before reacting."
    elif pattern.key == "composite.mars_pluto":
        read_more = "Composite Mars/Pluto amplifies desire, will, sexuality, creative force, and the overlap between power and vulnerability. This can make the bond difficult to keep casual and can escalate quickly when fear or control enters the room, so pacing, consent, trust, and deliberate de-escalation are part of the medicine of the aspect."
    else:
        read_more = f"{_interpret_for_section(pattern, 'composite' if pattern.layer == 'composite' else 'general')} Read as part of the whole map, this dynamic gains meaning through its repetitions, house emphasis, and related signatures rather than as a standalone label."
    related = _related_titles(pattern, all_patterns)
    if related:
        read_more += f" Related dynamics to compare: {', '.join(related[:3])}."
    return DynamicDetail(
        id=f"detail-{pattern.id}",
        title=pattern.title,
        kind=_detail_kind(pattern),
        summary=_interpret_for_section(pattern, "overview" if section == "Overview" else "general"),
        read_more=read_more,
        technical_factors=technical[:6],
        related_dynamics=related,
        repair_prompt=REPAIR_PRINCIPLES_BY_CATEGORY.get(_registry_category(pattern)),
        motif_category=convergence_category_for(pattern),
        priority=pattern.priority,
        section=section,
    )


def build_dynamic_details(relationship: RelationshipCalculation, patterns: list[Pattern], context: RelationshipContext | None = None) -> list[DynamicDetail]:
    central = _central_patterns(patterns, context)[:6]
    composite = _composite_patterns(patterns)[:4]
    friction = _friction_patterns(patterns)[:3]
    overlays = [p for p in patterns if p.layer == "house_overlay" and p.priority >= 62][:4]
    ordered: list[tuple[Pattern, str]] = [(p, "Overview") for p in central] + [(p, "House overlays") for p in overlays] + [(p, "Composite Field") for p in composite] + [(p, "Friction and Repair") for p in friction]
    details: list[DynamicDetail] = []
    seen: set[str] = set()
    for pattern, section in ordered:
        if pattern.id in seen:
            continue
        seen.add(pattern.id)
        details.append(_dynamic_detail_for_pattern(relationship, pattern, patterns, section))
        if len(details) >= 12:
            break
    return details

def _context_note(context: RelationshipContext | None) -> str | None:
    if context is None or not (context.user_question or context.origin_story or context.known_themes):
        return None

    lines: list[str] = []
    if context.user_question:
        lines.append(f"Question in the room: {context.user_question}")
    if context.origin_story:
        lines.append(f"Origin note: {context.origin_story}")
    if context.known_themes:
        lines.append(f"Named themes: {', '.join(context.known_themes)}.")
    return "\n\n".join(lines)



def _format_house(house: int | None) -> str:
    return f", {_ordinal(house)} house" if house is not None else ", house unavailable"


def _chart_check_body(relationship: RelationshipCalculation) -> str:
    lines: list[str] = []
    for chart in [relationship.person_a, relationship.person_b]:
        lines.append(f"### {chart.name} — calculated chart")
        lines.append("")
        asc = chart.angles.get("ascendant")
        if asc is None:
            lines.append("- Ascendant: unavailable because birth time is unknown or incomplete.")
        else:
            lines.append(f"- Ascendant: {asc.sign}")
        for body in ["sun", "moon", "mercury", "venus", "mars"]:
            placement = chart.placements.get(body)
            if placement is None:
                lines.append(f"- {_display_body(body)}: unavailable")
                continue
            lines.append(f"- {_display_body(body)}: {placement.sign}{_format_house(placement.house)}")
        house_label = chart.house_system.replace("_", " ").title()
        if chart.angles:
            lines.append(f"- House system: {house_label}")
        else:
            lines.append(f"- House system: {house_label}; houses and Ascendant unavailable or approximate without a known birth time.")
        birthplace = chart.birth.birthplace_label or "manual coordinates"
        lines.append(
            f"- Birthplace: {birthplace} — {chart.birth.latitude:.4f}, {chart.birth.longitude:.4f} — {chart.birth.timezone}"
        )
        if chart.warnings:
            lines.append(f"- Calculation note: {' '.join(chart.warnings)}")
        lines.append("")
    return "\n".join(lines).strip()

def _registry_category(pattern: Pattern) -> str:
    return get_pattern_metadata(pattern.key).category


def _friction_signature(pattern: Pattern) -> str:
    category = _registry_category(pattern)
    if category == "communication_heat":
        return (
            f"{_interpret_for_section(pattern, 'friction')} The friction signature is not merely disagreement; "
            "it is the gap between intention, tone, timing, and impact."
        )
    if category == "stability_container" or pattern.category in {"emotional_structure", "action_structure", "angle_structure"}:
        return (
            f"{_interpret_for_section(pattern, 'friction')} The friction signature often feels like care becoming pressure, "
            "or steadiness being received as restriction."
        )
    if category == "devotion_contract":
        return (
            f"{_interpret_for_section(pattern, 'friction')} The bond asks for commitment to become behavioral, "
            "not only emotional or implied."
        )
    if category == "erotic_charge":
        return (
            f"{_interpret_for_section(pattern, 'friction')} Chemistry is real here, but intensity needs pacing "
            "before either person treats charge as capacity."
        )
    if category == "trust_depth":
        return (
            f"{_interpret_for_section(pattern, 'friction')} Vulnerability should move at the speed of earned trust, "
            "not at the speed of the strongest feeling."
        )
    if category == "volatility":
        return (
            f"{_interpret_for_section(pattern, 'friction')} Distance and reconnection need an agreed rhythm so the "
            "push-pull does not become the whole relationship."
        )
    return _interpret_for_section(pattern, "friction")


def _friction_loop(patterns: list[Pattern]) -> str:
    selected = _friction_patterns(patterns)

    if not selected:
        return "No single friction loop dominates the current selection. Name the strongest activation and build an agreed rhythm around it.\n\n### Repair principles\n\n" + _repair_path(patterns)

    lines = []
    for pattern in selected[:3]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(f"{_strength_phrase(pattern)} {_friction_signature(pattern)}")
        lines.append("")
    lines.append("### Repair principles")
    lines.append("")
    lines.append(_repair_path([*selected, *patterns]))
    return "\n".join(lines).strip()


REPAIR_PRINCIPLES_BY_CATEGORY = {
    "emotional_recognition": "Do not assume the other person knows what you feel just because the connection feels familiar; build a shared emotional vocabulary.",
    "erotic_charge": "Chemistry is real, but it should be paced; do not mistake intensity alone for long-term capacity.",
    "trust_depth": "Build trust deliberately, in pace with the vulnerability and intensity the contact brings.",
    "communication_heat": "Name the gap between intention and impact; avoid treating tone issues as proof of incompatibility.",
    "stability_container": "Ask whether structure feels supportive or restrictive, then name expectations directly.",
    "volatility": "Clarify what each person needs during distance or cool-down periods; do not make the push-pull rhythm the whole relationship.",
    "projection_mirror": "Ask what is being seen in the other person, and whether it belongs partly to the observer.",
    "idealization": "Ask what is being seen in the other person, and whether it belongs partly to the observer.",
    "private_roots": "Distinguish present relationship needs from old family, home, or belonging templates.",
    "devotion_contract": "Clarify what commitment means behaviorally, not just emotionally.",
    "wounding_healing": "Handle tenderness carefully; avoid implying that pain equals depth.",
}


def _repair_principle_for_pattern(pattern: Pattern) -> str:
    if pattern.key == "synastry.mercury_mars":
        return "With Mercury/Mars heat in the chart, slow the nervous-system speed before debating content; tone, timing, and impact need as much care as being right."
    if pattern.key == "synastry.mercury_mercury":
        return "With Mercury/Mercury friction, translate between cognitive styles instead of assuming the other person is being careless or obtuse."
    if pattern.key == "composite.sun_saturn" or pattern.key in {"synastry.moon_saturn", "synastry.venus_saturn", "synastry.mars_saturn"}:
        return "With Saturn carrying pressure, make expectations explicit and protect permission for warmth, play, and imperfection inside responsibility."
    if pattern.key in {"composite.mars_pluto", "synastry.mars_pluto"}:
        return "With Mars/Pluto carrying so much charge, pace intensity through consent, trust, and de-escalation rather than treating escalation as proof the bond can hold everything at once."
    if pattern.key == "synastry.venus_ascendant" or (pattern.layer == "house_overlay" and pattern.key == "overlay.house_7"):
        return "With Venus/angle or 7th-house mirroring, enjoy the recognition without confusing attraction, reflection, or being chosen with automatic obligation."
    if pattern.key == "overlay.house_12":
        return "With 12th-house activation, name what is sensed but not spoken so intuition does not become projection."
    category = _registry_category(pattern)
    return REPAIR_PRINCIPLES_BY_CATEGORY.get(category, "Name the strongest activation and agree on a workable pace.")


def _repair_path(patterns: list[Pattern]) -> str:
    legacy_categories = {pattern.category for pattern in patterns[:10]}
    principles: list[str] = []

    for pattern in patterns[:10]:
        principle = _repair_principle_for_pattern(pattern)
        if principle and principle not in principles:
            principles.append(principle)

    if "communication" in legacy_categories and REPAIR_PRINCIPLES_BY_CATEGORY["communication_heat"] not in principles:
        principles.append(REPAIR_PRINCIPLES_BY_CATEGORY["communication_heat"])
    if legacy_categories.intersection({"emotional_structure", "bond_structure", "angle_structure", "action_structure"}) and REPAIR_PRINCIPLES_BY_CATEGORY["stability_container"] not in principles:
        principles.append(REPAIR_PRINCIPLES_BY_CATEGORY["stability_container"])
    if legacy_categories.intersection({"intensity", "emotional_intensity", "attraction_intensity"}) and REPAIR_PRINCIPLES_BY_CATEGORY["trust_depth"] not in principles:
        principles.append("With the chart's intensity signatures, vulnerability should move at the speed of earned trust rather than the speed of the strongest feeling.")
    if "emotional_variability" in legacy_categories and REPAIR_PRINCIPLES_BY_CATEGORY["volatility"] not in principles:
        principles.append(REPAIR_PRINCIPLES_BY_CATEGORY["volatility"])
    if "daily_life" in legacy_categories:
        principles.append("Bring repair into ordinary routines, not only big conversations.")
    principles.extend(_temperament_repair_principles(patterns))

    if not principles:
        principles.append("Name the strongest activation and agree on a workable pace.")

    return "\n".join(f"- {principle}" for principle in principles[:5])


def _temperament_repair_principles(patterns: list[Pattern]) -> list[str]:
    text = " ".join(pattern.title for pattern in patterns[:10]).lower()
    principles: list[str] = []
    if "mercury" in text:
        principles.append("Where Mercury is emphasized, repair works best through precision, naming, translation, and checking assumptions before arguing conclusions.")
    if "moon" in text:
        principles.append("Where Moon contacts are emphasized, distinguish explaining a feeling from actually giving it time to be felt and soothed.")
    return principles[:2]


def _pattern_summary(pattern: Pattern) -> RankedPatternSummary:
    metadata = get_pattern_metadata(pattern.key)
    evidence_text = "; ".join(pattern.evidence) if pattern.evidence else None
    reason = _interpret_for_section(
        pattern,
        "composite" if pattern.layer == "composite" else "friction" if metadata.default_section == "friction_repair" else "overview",
    )
    return RankedPatternSummary(
        key=pattern.key,
        title=pattern.title,
        category=metadata.category or pattern.category,
        tier=metadata.tier,
        priority=pattern.priority,
        adjusted_priority=pattern.priority,
        confidence=pattern.confidence,
        layer=pattern.layer,
        evidence_text=evidence_text,
        interpretive_reason=reason,
    )


def _friction_patterns(patterns: list[Pattern]) -> list[Pattern]:
    grouped = _patterns_by_category(patterns)
    friction_categories = [
        "communication",
        "emotional_structure",
        "angle_structure",
        "emotional_intensity",
        "emotional_activation",
        "embodied_activation",
        "intensity",
        "action_structure",
        "emotional_variability",
    ]
    selected: list[Pattern] = []
    for category in friction_categories:
        selected.extend(grouped.get(category, []))
    selected.extend(
        pattern
        for pattern in patterns
        if _registry_category(pattern)
        in {
            "communication_heat",
            "stability_container",
            "devotion_contract",
            "erotic_charge",
            "trust_depth",
            "volatility",
            "wounding_healing",
        }
        and pattern not in selected
    )
    return sorted(selected, key=lambda pattern: pattern.priority, reverse=True)


def _repair_theme_list(patterns: list[Pattern]) -> list[str]:
    return [line.removeprefix("- ") for line in _repair_path(patterns).splitlines() if line.strip()][:5]


def build_report_synthesis_packet(
    relationship: RelationshipCalculation,
    context: RelationshipContext | None = None,
    *,
    max_patterns: int = 7,
) -> ReportSynthesisPacket:
    """Build compact AI guidance from the deterministic report selection."""
    raw_patterns = detect_relationship_patterns(relationship)
    patterns = weight_patterns(raw_patterns, context)
    central = _central_patterns(patterns, context)
    composite = _composite_patterns(patterns)
    lead = central[0] if central else (patterns[0] if patterns else None)

    return ReportSynthesisPacket(
        relationship_type=context.relationship_type if context else None,
        status=context.status if context else None,
        user_question=context.user_question if context else None,
        origin_story=context.origin_story if context else None,
        house_system=relationship.person_a.house_system,
        top_ranked_patterns=[_pattern_summary(pattern) for pattern in patterns[:max_patterns]],
        lead_pattern=_pattern_summary(lead) if lead else None,
        friction_patterns=[_pattern_summary(pattern) for pattern in _friction_patterns(patterns)[:3]],
        repair_themes=_repair_theme_list(patterns),
        composite_themes=[_pattern_summary(pattern) for pattern in composite[:3]],
        chart_sanity_summary=_chart_check_body(relationship),
        dynamic_details=build_dynamic_details(relationship, patterns, context),
        temperament_summary=compare_temperaments(relationship.person_a, relationship.person_b),
        relationship_rulership_summary={
            "person_a": relationship_significator_summary(relationship.person_a),
            "person_b": relationship_significator_summary(relationship.person_b),
            "cross_activations": [pattern.evidence[0] for pattern in patterns if pattern.key.startswith("synastry.relationship_ruler") or pattern.key == "synastry.descendant_contact"][:8],
        },
    )




def _placement_diagnostic(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    if placement is None:
        return None
    house = f", house {placement.house}" if placement.house is not None else ""
    return f"{placement.sign} {placement.degree:.1f}°{house}"


def _chart_sanity_diagnostics(chart: Chart) -> ChartSanityDiagnostics:
    asc = chart.angles.get("ascendant")
    mc = chart.angles.get("midheaven")
    return ChartSanityDiagnostics(
        name=chart.name,
        time_known=chart.birth.time_known,
        house_system=chart.house_system,
        ascendant=f"{asc.sign} {asc.degree:.1f}°" if asc else None,
        midheaven=f"{mc.sign} {mc.degree:.1f}°" if mc else None,
        sun=_placement_diagnostic(chart, "sun"),
        moon=_placement_diagnostic(chart, "moon"),
        venus=_placement_diagnostic(chart, "venus"),
        mars=_placement_diagnostic(chart, "mars"),
        birthplace=chart.birth.birthplace_label or "manual coordinates",
        timezone=chart.birth.timezone,
        coordinates=f"{chart.birth.latitude:.4f}, {chart.birth.longitude:.4f}",
        warnings=chart.warnings,
    )


def _pattern_diagnostics(
    pattern: Pattern,
    *,
    raw_by_id: dict[str, Pattern] | None = None,
    context: RelationshipContext | None = None,
    patterns: list[Pattern] | None = None,
) -> ReportPatternDiagnostics:
    metadata = get_pattern_metadata(pattern.key)
    raw = raw_by_id.get(pattern.id) if raw_by_id else None
    return ReportPatternDiagnostics(
        key=pattern.key,
        title=pattern.title,
        category=metadata.category or pattern.category,
        tier=metadata.tier,
        priority=raw.priority if raw is not None else pattern.priority,
        adjusted_priority=pattern.priority,
        confidence=pattern.confidence,
        layer=pattern.layer,
        lead_eligible=is_lead_eligible(pattern, context, patterns),
        evidence=pattern.evidence,
    )


def _pattern_diagnostics_from_summary(summary: RankedPatternSummary) -> ReportPatternDiagnostics:
    metadata = get_pattern_metadata(summary.key)
    evidence = [summary.evidence_text] if summary.evidence_text else []
    return ReportPatternDiagnostics(
        key=summary.key,
        title=summary.title,
        category=summary.category,
        tier=summary.tier,
        priority=summary.priority,
        adjusted_priority=summary.adjusted_priority,
        confidence=summary.confidence,
        layer=summary.layer,
        lead_eligible=metadata.lead_eligible,
        evidence=evidence,
    )


def _aspect_asteroids(aspect: Aspect) -> set[str]:
    return {aspect.point_a.lower(), aspect.point_b.lower()} & ASTEROID_POINTS


def _aspect_non_asteroids(aspect: Aspect) -> set[str]:
    return {aspect.point_a.lower(), aspect.point_b.lower()} - ASTEROID_POINTS


def _suppressed_asteroid_notes(relationship: RelationshipCalculation, included_keys: set[str]) -> list[str]:
    notes: list[str] = []
    for label, aspects in [("synastry", relationship.synastry_aspects), ("composite", relationship.composite_aspects)]:
        for aspect in aspects:
            asteroids = _aspect_asteroids(aspect)
            if not asteroids:
                continue
            other_points = _aspect_non_asteroids(aspect)
            asteroid = sorted(asteroids)[0]
            other = sorted(other_points)[0] if other_points else "asteroid"
            key_fragment = f".asteroid.{asteroid}.{other}"
            if any(key_fragment in key for key in included_keys):
                continue
            if asteroid in ADVANCED_ASTEROIDS:
                notes.append(
                    f"{label}: {asteroid} {aspect.aspect} {other} suppressed as advanced asteroid (orb {aspect.orb:.2f})"
                )
            elif aspect.orb > DEFAULT_ASTEROID_ORB:
                notes.append(
                    f"{label}: {asteroid} {aspect.aspect} {other} suppressed outside default asteroid orb (orb {aspect.orb:.2f})"
                )
            elif other not in ASTEROID_CENTRAL_TARGETS:
                notes.append(
                    f"{label}: {asteroid} {aspect.aspect} {other} suppressed because target is not central"
                )
    return notes[:12]


def _synthesis_packet_summary(packet: ReportSynthesisPacket) -> dict[str, object]:
    return {
        "house_system": packet.house_system,
        "lead_pattern_key": packet.lead_pattern.key if packet.lead_pattern else None,
        "top_ranked_pattern_keys": [pattern.key for pattern in packet.top_ranked_patterns],
        "friction_pattern_keys": [pattern.key for pattern in packet.friction_patterns],
        "composite_theme_keys": [pattern.key for pattern in packet.composite_themes],
        "repair_theme_count": len(packet.repair_themes),
        "has_chart_sanity_summary": bool(packet.chart_sanity_summary),
        "has_temperament_summary": bool(packet.temperament_summary),
        "relationship_rulership_summary": packet.relationship_rulership_summary,
    }


def build_report_diagnostics(
    relationship: RelationshipCalculation,
    context: RelationshipContext | None = None,
    *,
    synthesis_packet: ReportSynthesisPacket | None = None,
    max_patterns: int = 10,
) -> ReportDiagnostics:
    """Build compact developer diagnostics for deterministic report ranking and motif QA."""
    from .motifs import select_motifs_for_persistence

    raw_patterns = detect_relationship_patterns(relationship)
    raw_by_id = {pattern.id: pattern for pattern in raw_patterns}
    patterns = weight_patterns(raw_patterns, context)
    central = _central_patterns(patterns, context)
    composite = _composite_patterns(patterns)
    lead = central[0] if central else (patterns[0] if patterns else None)
    packet = synthesis_packet or build_report_synthesis_packet(relationship, context=context)
    included_asteroids = [pattern for pattern in patterns if ".asteroid." in pattern.key or pattern.category.startswith("asteroid")]
    included_keys = {pattern.key for pattern in included_asteroids}

    return ReportDiagnostics(
        house_system=relationship.person_a.house_system,
        person_a_chart_sanity=_chart_sanity_diagnostics(relationship.person_a),
        person_b_chart_sanity=_chart_sanity_diagnostics(relationship.person_b),
        top_ranked_patterns=[
            _pattern_diagnostics(pattern, raw_by_id=raw_by_id, context=context, patterns=patterns)
            for pattern in patterns[:max_patterns]
        ],
        selected_lead_pattern=(
            _pattern_diagnostics(lead, raw_by_id=raw_by_id, context=context, patterns=patterns) if lead else None
        ),
        overview_central_patterns=[
            _pattern_diagnostics(pattern, raw_by_id=raw_by_id, context=context, patterns=patterns)
            for pattern in central
        ],
        friction_patterns=[
            _pattern_diagnostics(pattern, raw_by_id=raw_by_id, context=context, patterns=patterns)
            for pattern in _friction_patterns(patterns)[:3]
        ],
        composite_themes=[
            _pattern_diagnostics(pattern, raw_by_id=raw_by_id, context=context, patterns=patterns)
            for pattern in composite[:3]
        ],
        motif_persistence_summary=[
            _pattern_diagnostics_from_summary(pattern) for pattern in select_motifs_for_persistence(packet)
        ],
        asteroid_policy_summary=AsteroidPolicyDiagnostics(
            included_asteroid_patterns=[
                _pattern_diagnostics(pattern, raw_by_id=raw_by_id, context=context, patterns=patterns)
                for pattern in included_asteroids[:8]
            ],
            suppressed_asteroid_patterns=_suppressed_asteroid_notes(relationship, included_keys),
            default_report_asteroids=sorted(DEFAULT_REPORT_ASTEROIDS),
            advanced_asteroids_suppressed=sorted(ADVANCED_ASTEROIDS),
        ),
        ai_synthesis_packet_summary=_synthesis_packet_summary(packet),
        temperament_summary=compare_temperaments(relationship.person_a, relationship.person_b),
        relationship_rulership_summary={
            "person_a": relationship_significator_summary(relationship.person_a),
            "person_b": relationship_significator_summary(relationship.person_b),
            "cross_activations": [pattern.evidence[0] for pattern in patterns if pattern.key.startswith("synastry.relationship_ruler") or pattern.key == "synastry.descendant_contact"][:8],
        },
    )


def generate_relationship_report(
    relationship: RelationshipCalculation,
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    raw_patterns = detect_relationship_patterns(relationship)
    patterns = weight_patterns(raw_patterns, context)
    central = _central_patterns(patterns, context)
    composite = _composite_patterns(patterns)
    a_to_b = _directional_patterns(relationship, patterns, "person_a")
    b_to_a = _directional_patterns(relationship, patterns, "person_b")

    person_a_name = relationship.person_a.name
    person_b_name = relationship.person_b.name
    title = f"Relationship Field Map — {person_a_name} / {person_b_name}"
    sections = [
        ReportSection(
            title="Overview",
            body=_overview(relationship, central, composite, patterns),
        ),
        ReportSection(
            title=f"{person_a_name} Relationship Profile",
            body=_profile_body(relationship.person_a, patterns),
        ),
        ReportSection(
            title=f"{person_b_name} Relationship Profile",
            body=_profile_body(relationship.person_b, patterns),
        ),
        ReportSection(
            title=f"How {person_a_name} Activates {person_b_name}",
            body=_signature_block_for_relationship(relationship, a_to_b, limit=3, empty_message=f"No strong directional synastry patterns show {person_a_name} specifically activating {person_b_name} in the current selection."),
        ),
        ReportSection(
            title=f"How {person_b_name} Activates {person_a_name}",
            body=_signature_block_for_relationship(relationship, b_to_a, limit=3, empty_message=f"No strong directional synastry patterns show {person_b_name} specifically activating {person_a_name} in the current selection."),
        ),
        ReportSection(
            title="Composite Field",
            body=_composite_field_body(composite),
        ),
        ReportSection(title="Friction and Repair", body=_friction_loop(patterns)),
        ReportSection(
            title="Calculated chart check",
            body=_chart_check_body(relationship),
        ),
    ]

    context_body = _context_note(context)
    if context_body:
        sections.append(ReportSection(title="Context Notes", body=context_body))

    return RelationshipReport(title=title, sections=sections, dynamic_details=build_dynamic_details(relationship, patterns, context))

def generate_report_from_birth_data(
    person_a: BirthData,
    person_b: BirthData,
    house_system: str = DEFAULT_HOUSE_SYSTEM,
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    relationship = calculate_relationship(person_a, person_b, house_system=house_system)
    return generate_relationship_report(relationship, context=context)
