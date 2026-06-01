"""Markdown relationship report generation."""

from __future__ import annotations

import re
from collections import defaultdict

from pydantic import BaseModel

from .context import RelationshipContext
from .interpretations import interpret_pattern
from .patterns import Pattern, detect_relationship_patterns
from .relationship import calculate_relationship
from .schemas import BirthData, RelationshipCalculation
from .weighting import weight_patterns


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
        return "Background."
    if pattern.priority >= 92:
        return "Central."
    if pattern.priority >= 82:
        return "Strong."
    if pattern.priority >= 70:
        return "Moderate."
    return "Background."


def _signature_block(patterns: list[Pattern], *, limit: int, empty_message: str) -> str:
    if not patterns:
        return empty_message

    lines: list[str] = []
    for pattern in patterns[:limit]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(f"{_strength_phrase(pattern)} {interpret_pattern(pattern)}")
        lines.append("")
    return "\n".join(lines).strip()


def _central_patterns(patterns: list[Pattern]) -> list[Pattern]:
    selected = [
        pattern for pattern in patterns
        if pattern.layer != "house_overlay" and pattern.priority >= 86
    ]
    if len(selected) < 3:
        selected = [pattern for pattern in patterns if pattern.layer != "house_overlay"]
    return selected[:5]


def _supporting_patterns(patterns: list[Pattern], central: list[Pattern]) -> list[Pattern]:
    central_ids = {pattern.id for pattern in central}
    supporting = [
        pattern for pattern in patterns
        if pattern.id not in central_ids and pattern.layer == "house_overlay"
    ]
    supporting.extend(
        pattern for pattern in patterns
        if pattern.id not in central_ids and pattern.layer == "synastry" and pattern.priority < 86
    )
    return supporting[:5]


def _composite_patterns(patterns: list[Pattern]) -> list[Pattern]:
    aspects = [pattern for pattern in patterns if pattern.layer == "composite" and not pattern.key.startswith(("composite.sun.", "composite.moon."))]
    sign_texture = [pattern for pattern in patterns if pattern.layer == "composite" and pattern.key.startswith(("composite.sun.", "composite.moon."))]
    return (aspects + sign_texture)[:4]


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


def _friction_loop(patterns: list[Pattern]) -> str:
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
    selected = sorted(selected, key=lambda pattern: pattern.priority, reverse=True)

    if not selected:
        return "No single friction loop dominates the current selection. Watch the strongest central signature and build rhythm around it."

    lines = []
    for pattern in selected[:3]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(f"{_strength_phrase(pattern)} {interpret_pattern(pattern)}")
        lines.append("")
    lines.append(_repair_path(patterns))
    return "\n".join(lines).strip()


def _repair_path(patterns: list[Pattern]) -> str:
    categories = {pattern.category for pattern in patterns[:8]}
    principles = []
    if "communication" in categories:
        principles.append("Slow the conversation enough that heat can become clarity.")
    if "emotional_structure" in categories or "bond_structure" in categories or "angle_structure" in categories:
        principles.append("Check whether structure is acting as container or constraint.")
    if "intensity" in categories or "emotional_intensity" in categories or "attraction_intensity" in categories:
        principles.append("Intensity needs repair capacity; it is not proof of safety.")
    if "emotional_variability" in categories:
        principles.append("Make room for space without turning distance into abandonment.")
    if "daily_life" in categories:
        principles.append("Bring repair into ordinary routines, not only big conversations.")

    if not principles:
        principles.append("Name the strongest activation and agree on a workable pace.")

    return "\n".join(f"- {principle}" for principle in principles)


def generate_relationship_report(
    relationship: RelationshipCalculation,
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    raw_patterns = detect_relationship_patterns(relationship)
    patterns = weight_patterns(raw_patterns, context)
    central = _central_patterns(patterns)
    supporting = _supporting_patterns(patterns, central)
    composite = _composite_patterns(patterns)

    title = f"Relationship Field Map — {relationship.person_a.name} / {relationship.person_b.name}"
    sections = [
        ReportSection(
            title="Central Signatures",
            body=_signature_block(central, limit=5, empty_message="No central signatures were selected from the available chart data."),
        ),
        ReportSection(
            title="Supporting Patterns",
            body=_signature_block(supporting, limit=5, empty_message="No supporting patterns were strong enough to include."),
        ),
        ReportSection(
            title="Composite Field",
            body=_signature_block(composite, limit=4, empty_message="Composite patterns were not strong enough to lead this report."),
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
    house_system: str = "placidus",
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    relationship = calculate_relationship(person_a, person_b, house_system=house_system)
    return generate_relationship_report(relationship, context=context)
