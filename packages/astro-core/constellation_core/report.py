"""First-pass markdown report generation.

This module creates a deliberately simple Relationship Field Map from ranked
patterns. It is not the final interpretive voice; it proves the pipeline from
calculation to structured output.
"""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel

from .context import RelationshipContext
from .interpretations import interpret_pattern
from .patterns import Pattern, detect_relationship_patterns
from .relationship import calculate_relationship
from .schemas import BirthData, RelationshipCalculation


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


def _context_summary(context: RelationshipContext | None) -> str:
    if context is None:
        return "No relationship context was provided. This report is reading the chart field only."

    lines = [
        f"- Relationship type: {context.relationship_type}",
        f"- Status: {context.status}",
    ]
    if context.user_question:
        lines.append(f"- User question: {context.user_question}")
    if context.origin_story:
        lines.append(f"- Origin story / symbolic context: {context.origin_story}")
    if context.known_themes:
        lines.append(f"- Known themes: {', '.join(context.known_themes)}")
    return "\n".join(lines)


def _pattern_list(patterns: list[Pattern], limit: int = 10) -> str:
    if not patterns:
        return "No high-priority patterns were detected yet."
    lines = []
    for pattern in patterns[:limit]:
        evidence = "; ".join(pattern.evidence)
        lines.append(f"- **{pattern.title}** ({pattern.layer}, priority {pattern.priority}): {evidence}")
    return "\n".join(lines)


def _patterns_by_category(patterns: list[Pattern]) -> dict[str, list[Pattern]]:
    grouped: dict[str, list[Pattern]] = defaultdict(list)
    for pattern in patterns:
        grouped[pattern.category].append(pattern)
    return grouped


def _interpretation_for_categories(
    patterns: list[Pattern],
    categories: set[str],
    empty_message: str,
    limit: int = 4,
) -> str:
    selected = [pattern for pattern in patterns if pattern.category in categories]
    if not selected:
        return empty_message

    lines = []
    for pattern in selected[:limit]:
        evidence = "; ".join(pattern.evidence)
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(f"Evidence: {evidence}")
        lines.append("")
        lines.append(interpret_pattern(pattern))
        lines.append("")
    return "\n".join(lines).strip()


def _birdseye(patterns: list[Pattern], context: RelationshipContext | None) -> str:
    if not patterns:
        return (
            "This is a calculation-backed draft report. No high-priority patterns have been "
            "selected yet, so the next step is to validate chart data and expand detection."
        )

    top = patterns[0]
    context_note = ""
    if context and context.relationship_type != "other":
        context_note = f" This is being framed as a {context.relationship_type} relationship."

    return (
        "This draft reads the relationship as a field of activation rather than a compatibility "
        f"score.{context_note} The strongest currently detected pattern is **{top.title}**, "
        "which should set the first interpretive emphasis while the remaining patterns provide "
        "supporting layers."
    )


def _pattern_interpretations(patterns: list[Pattern], limit: int = 6) -> str:
    if not patterns:
        return "No interpretation blocks were selected yet."
    lines = []
    for pattern in patterns[:limit]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(interpret_pattern(pattern))
        lines.append("")
    return "\n".join(lines).strip()


def _biographical_activation(context: RelationshipContext | None) -> str:
    if context is None or not context.has_origin_story():
        return (
            "No origin story was provided. Later versions can ask about meaningful places, "
            "objects, dreams, timing, family context, or old relationship chapters."
        )
    return (
        "The user provided an origin story or symbolic context. This should be treated as "
        "part of the relationship field, not as decorative background. Some relationships "
        "do not only activate chemistry; they activate memory, biography, place, timing, "
        "or an unfinished storyline."
    )


def _composite_summary(relationship: RelationshipCalculation) -> str:
    if relationship.composite is None:
        return "Composite chart was not calculated."

    composite = relationship.composite
    sun = composite.placements.get("sun")
    moon = composite.placements.get("moon")
    venus = composite.placements.get("venus")
    mars = composite.placements.get("mars")

    parts = []
    if sun:
        parts.append(f"Composite Sun: {sun.degree:.2f} {sun.sign}")
    if moon:
        parts.append(f"Composite Moon: {moon.degree:.2f} {moon.sign}")
    if venus:
        parts.append(f"Composite Venus: {venus.degree:.2f} {venus.sign}")
    if mars:
        parts.append(f"Composite Mars: {mars.degree:.2f} {mars.sign}")

    if not parts:
        return "Composite chart has no core placements available."
    return "\n".join(f"- {part}" for part in parts)


def _friction_loop(patterns: list[Pattern]) -> str:
    grouped = _patterns_by_category(patterns)
    friction_categories = [
        "communication",
        "emotional_structure",
        "emotional_intensity",
        "emotional_activation",
        "intensity",
        "action_structure",
        "emotional_variability",
    ]
    selected = []
    for category in friction_categories:
        selected.extend(grouped.get(category, []))
    selected = sorted(selected, key=lambda pattern: pattern.priority, reverse=True)

    if not selected:
        return (
            "No major friction loop has been selected yet. This does not mean there is no friction; "
            "it means the current detector needs more chart evidence or more rules."
        )

    lines = [
        "A first-pass friction loop can be built from the strongest pressure patterns:",
        "",
    ]
    for index, pattern in enumerate(selected[:4], start=1):
        lines.append(f"{index}. **{pattern.title}** — {interpret_pattern(pattern)}")
    lines.append("")
    lines.append("The repair path should focus on pacing, translation, and making activation conscious before it becomes escalation.")
    return "\n".join(lines)


def _repair_path(patterns: list[Pattern]) -> str:
    categories = {pattern.category for pattern in patterns[:8]}
    principles = []
    if "communication" in categories:
        principles.append("Slow the conversation enough that heat can become clarity rather than escalation.")
    if "emotional_structure" in categories or "bond_structure" in categories:
        principles.append("Ask whether structure is functioning as container or constraint.")
    if "intensity" in categories or "emotional_intensity" in categories or "attraction_intensity" in categories:
        principles.append("Treat intensity as something that requires repair capacity, not as proof of safety.")
    if "emotional_variability" in categories:
        principles.append("Create space without turning distance into abandonment.")
    if "daily_life" in categories:
        principles.append("Bring the repair into ordinary routines, not only big conversations.")

    if not principles:
        principles.append("Name the strongest activation and ask what kind of rhythm would help it become workable.")

    return "\n".join(f"- {principle}" for principle in principles)


def _one_sentence_summary(patterns: list[Pattern]) -> str:
    if not patterns:
        return "This relationship map needs more validated chart data before a strong summary can be generated."
    top = patterns[0]
    return f"The current map is led by {top.title.lower()}: a relationship field that asks for awareness, translation, and repair rather than a compatibility verdict."


def generate_relationship_report(
    relationship: RelationshipCalculation,
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    patterns = detect_relationship_patterns(relationship)

    title = f"Relationship Field Map — {relationship.person_a.name} / {relationship.person_b.name}"
    sections = [
        ReportSection(title="Context", body=_context_summary(context)),
        ReportSection(title="Bird's-Eye View", body=_birdseye(patterns, context)),
        ReportSection(title="Top Detected Patterns", body=_pattern_list(patterns)),
        ReportSection(
            title="Mutual Activation / Synastry",
            body=_interpretation_for_categories(
                patterns,
                {"recognition", "communication", "emotional_translation", "emotional_activation"},
                "No mutual activation patterns were selected yet.",
            ),
        ),
        ReportSection(
            title="Desire & Affection Layer",
            body=_interpretation_for_categories(
                patterns,
                {"attraction", "desire", "affection", "attraction_intensity"},
                "No desire or affection patterns were selected yet.",
            ),
        ),
        ReportSection(
            title="Emotional Safety Layer",
            body=_interpretation_for_categories(
                patterns,
                {"emotional_structure", "emotional_intensity", "emotional_variability", "home_roots"},
                "No emotional safety patterns were selected yet.",
            ),
        ),
        ReportSection(
            title="Early Interpretation Layer",
            body=_pattern_interpretations(patterns),
        ),
        ReportSection(title="Biographical Activation", body=_biographical_activation(context)),
        ReportSection(title="The Field Between You / Composite Core", body=_composite_summary(relationship)),
        ReportSection(title="Friction Loop", body=_friction_loop(patterns)),
        ReportSection(title="Repair Path", body=_repair_path(patterns)),
        ReportSection(title="One-Sentence Summary", body=_one_sentence_summary(patterns)),
    ]
    return RelationshipReport(title=title, sections=sections)


def generate_report_from_birth_data(
    person_a: BirthData,
    person_b: BirthData,
    house_system: str = "whole_sign",
    context: RelationshipContext | None = None,
) -> RelationshipReport:
    relationship = calculate_relationship(person_a, person_b, house_system=house_system)
    return generate_relationship_report(relationship, context=context)
