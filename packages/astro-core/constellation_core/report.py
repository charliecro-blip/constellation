"""First-pass markdown report generation.

This module creates a deliberately simple Relationship Field Map from ranked
patterns. It is not the final interpretive voice; it proves the pipeline from
calculation to structured output.
"""

from __future__ import annotations

from pydantic import BaseModel

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


def _pattern_list(patterns: list[Pattern], limit: int = 8) -> str:
    if not patterns:
        return "No high-priority patterns were detected yet."
    lines = []
    for pattern in patterns[:limit]:
        evidence = "; ".join(pattern.evidence)
        lines.append(f"- **{pattern.title}** ({pattern.layer}, priority {pattern.priority}): {evidence}")
    return "\n".join(lines)


def _pattern_interpretations(patterns: list[Pattern], limit: int = 5) -> str:
    if not patterns:
        return "No interpretation blocks were selected yet."
    lines = []
    for pattern in patterns[:limit]:
        lines.append(f"### {pattern.title}")
        lines.append("")
        lines.append(interpret_pattern(pattern))
        lines.append("")
    return "\n".join(lines).strip()


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


def generate_relationship_report(relationship: RelationshipCalculation) -> RelationshipReport:
    patterns = detect_relationship_patterns(relationship)

    title = f"Relationship Field Map — {relationship.person_a.name} / {relationship.person_b.name}"
    sections = [
        ReportSection(
            title="Bird's-Eye View",
            body=(
                "This is a calculation-backed draft report. It lists the strongest detected "
                "relationship patterns without making compatibility scores or verdicts."
            ),
        ),
        ReportSection(
            title="Top Detected Patterns",
            body=_pattern_list(patterns),
        ),
        ReportSection(
            title="Early Interpretation Layer",
            body=_pattern_interpretations(patterns),
        ),
        ReportSection(
            title="The Field Between You / Composite Core",
            body=_composite_summary(relationship),
        ),
        ReportSection(
            title="Next Interpretation Step",
            body=(
                "The next layer will translate these ranked patterns into full somatic, relational "
                "sections: mutual activation, emotional body, friction loop, and repair path."
            ),
        ),
    ]
    return RelationshipReport(title=title, sections=sections)


def generate_report_from_birth_data(
    person_a: BirthData,
    person_b: BirthData,
    house_system: str = "whole_sign",
) -> RelationshipReport:
    relationship = calculate_relationship(person_a, person_b, house_system=house_system)
    return generate_relationship_report(relationship)
