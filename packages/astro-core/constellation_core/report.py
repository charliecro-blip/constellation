"""Markdown relationship report generation.

See docs/astrology_doctrine/report_prioritization.md and
docs/astrology_doctrine/report_voice_guide.md for lead selection and voice
doctrine.
"""

from __future__ import annotations

import re
from collections import defaultdict

from pydantic import BaseModel

from .asteroid_policy import ADVANCED_ASTEROIDS, DEFAULT_ASTEROID_ORB, DEFAULT_REPORT_ASTEROIDS, RELATIONSHIP_RELEVANT_HOUSES
from .context import RelationshipContext
from .interpretations import interpret_pattern
from .natal_profile import SIGN_ELEMENTS, SIGN_MODES
from .pattern_registry import convergence_category_for, get_pattern_metadata
from .patterns import ASTEROID_CENTRAL_TARGETS, ASTEROID_POINTS, Pattern, detect_relationship_patterns
from .chart import DEFAULT_HOUSE_SYSTEM
from .relationship import calculate_relationship
from .schemas import (
    Aspect,
    AsteroidPolicyDiagnostics,
    BirthData,
    Chart,
    ChartSanityDiagnostics,
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
    candidates = [pattern for pattern in patterns if pattern.layer != "house_overlay"]
    lead_candidates = [pattern for pattern in candidates if is_lead_eligible(pattern, context, patterns)]
    primary = lead_candidates[0] if lead_candidates else next(
        (pattern for pattern in candidates if _is_major_fallback_pattern(pattern, context)),
        None,
    )
    if primary is None:
        return []

    supporting = [
        pattern
        for pattern in candidates
        if pattern.id != primary.id and not _is_generic_composite_baseline(pattern)
    ]
    return [primary, *supporting][:4]


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
    else:
        lines.append(f"- **Attachment style:** {chart.name}'s birth time data does not give a reliable Ascendant/Descendant axis here, so this profile leans on the relational planets rather than angles.")

    moon = _placement_phrase(chart, "moon")
    lines.append(f"- **Emotional need:** {moon or 'The Moon placement is not available in this chart extract'}, so regulation, safety, and reassurance should be read through that emotional tone.")

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
        lines.append(f"- **Repeated relationship terrain:** The 5th/7th/8th-house emphasis ({', '.join(houses)}) can repeat themes around romance, partnership, intimacy, trust, and shared vulnerability.")
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
    return sorted(selected, key=lambda item: item.priority, reverse=True)[:3]


def _element(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    return SIGN_ELEMENTS.get(placement.sign) if placement else None


def _mode(chart: Chart, body: str) -> str | None:
    placement = chart.placements.get(body)
    return SIGN_MODES.get(placement.sign) if placement else None


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
    synastry = [pattern for pattern in central if pattern.layer == "synastry"]
    overlays = [pattern for pattern in patterns if pattern.layer == "house_overlay" and pattern.priority >= 56]
    friction = [
        pattern
        for pattern in patterns
        if pattern.category
        in {
            "communication",
            "emotional_structure",
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

    paragraphs: list[str] = []
    if central:
        primary = central[0]
        supporting_pattern = next((pattern for pattern in central[1:] if pattern.layer == primary.layer), None)
        supporting = (
            f" {supporting_pattern.title} repeats the relational pull."
            if supporting_pattern is not None
            else ""
        )
        if primary.layer == "composite":
            paragraphs.append(
                f"The relationship organizes itself around {primary.title}. "
                f"{_interpret_for_section(primary, 'composite')}{supporting} "
                "The bond is easier to understand through this specific shared field than through generic composite texture."
            )
        else:
            paragraphs.append(
                f"The central story between {a} and {b} is carried by {primary.title}. "
                f"{_interpret_for_section(primary, 'overview')}{supporting} "
                "This is the signature to read first; tighter but more mechanical contacts should serve this story, not replace it."
            )
    else:
        paragraphs.append(
            f"The strongest organizing themes between {a} and {b} come from repeated contact patterns rather than one spectacular signature."
        )

    if comparison_notes:
        paragraphs.append(
            "Chart-to-chart comparison makes the field feel "
            + ", ".join(comparison_notes)
            + ". Use this as synthesis support, not as a score."
        )
    elif overlays:
        paragraphs.append(
            f"House overlays such as {overlays[0].title} show where one person's presence repeatedly lands in ordinary life, memory, attraction, or vulnerability."
        )

    if composite and (not paragraphs[0].startswith("The relationship organizes")):
        comp = composite[0]
        paragraphs.append(
            f"The composite field adds {comp.title}. {_interpret_for_section(comp, 'composite')} "
            "This describes what the bond tends to produce when both charts are read as one shared weather system."
        )

    repair = next((pattern for pattern in friction if not (_is_minor_communication(pattern) and synastry)), None)
    if repair:
        paragraphs.append(
            f"The main repair theme is {repair.title}. {_interpret_for_section(repair, 'friction')} "
            "Give the activation a clean form before it turns into pressure, withdrawal, or escalation."
        )
    elif friction:
        repair = friction[0]
        paragraphs.append(
            f"Communication is part of the repair work through {repair.title}, but it should not define the whole bond by itself."
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
        return "Affection, speech, and depth/compulsion are fused into one relational circuit; what is said, desired, and withheld can carry unusual charge."
    return "This close chain works like a single circuit: one body activates the next, so affection, response, timing, and pressure are read as a combined pattern rather than isolated conjunctions."


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
    lines.append(_repair_path(patterns))
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


def _repair_path(patterns: list[Pattern]) -> str:
    registry_categories = [_registry_category(pattern) for pattern in patterns[:10]]
    legacy_categories = {pattern.category for pattern in patterns[:10]}
    principles: list[str] = []

    for category in registry_categories:
        principle = REPAIR_PRINCIPLES_BY_CATEGORY.get(category)
        if principle and principle not in principles:
            principles.append(principle)

    if "communication" in legacy_categories and REPAIR_PRINCIPLES_BY_CATEGORY["communication_heat"] not in principles:
        principles.append(REPAIR_PRINCIPLES_BY_CATEGORY["communication_heat"])
    if legacy_categories.intersection({"emotional_structure", "bond_structure", "angle_structure", "action_structure"}) and REPAIR_PRINCIPLES_BY_CATEGORY["stability_container"] not in principles:
        principles.append(REPAIR_PRINCIPLES_BY_CATEGORY["stability_container"])
    if legacy_categories.intersection({"intensity", "emotional_intensity", "attraction_intensity"}) and REPAIR_PRINCIPLES_BY_CATEGORY["trust_depth"] not in principles:
        principles.append("Intensity needs repair capacity; it is not proof of safety.")
    if "emotional_variability" in legacy_categories and REPAIR_PRINCIPLES_BY_CATEGORY["volatility"] not in principles:
        principles.append(REPAIR_PRINCIPLES_BY_CATEGORY["volatility"])
    if "daily_life" in legacy_categories:
        principles.append("Bring repair into ordinary routines, not only big conversations.")

    if not principles:
        principles.append("Name the strongest activation and agree on a workable pace.")

    return "\n".join(f"- {principle}" for principle in principles[:5])


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
            title="Calculated chart check",
            body=_chart_check_body(relationship),
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
            body=_signature_block(a_to_b, limit=3, empty_message=f"No strong directional synastry patterns show {person_a_name} specifically activating {person_b_name} in the current selection."),
        ),
        ReportSection(
            title=f"How {person_b_name} Activates {person_a_name}",
            body=_signature_block(b_to_a, limit=3, empty_message=f"No strong directional synastry patterns show {person_b_name} specifically activating {person_a_name} in the current selection."),
        ),
        ReportSection(
            title="Composite Field",
            body=_signature_block(composite, limit=5, empty_message="Composite patterns were not strong enough to lead this report.", section="composite"),
        ),
        ReportSection(title="Friction and Repair", body=_friction_loop(patterns)),
    ]

    context_body = _context_note(context)
    if context_body:
        sections.append(ReportSection(title="Context Notes", body=context_body))

    return RelationshipReport(title=title, sections=sections)

def generate_report_from_birth_data(
    person_a: BirthData,
    person_b: BirthData,
    house_system: str = DEFAULT_HOUSE_SYSTEM,
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    relationship = calculate_relationship(person_a, person_b, house_system=house_system)
    return generate_relationship_report(relationship, context=context)
