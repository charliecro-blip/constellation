"""Confidence and missing-data helpers."""

from __future__ import annotations

from .schemas import RelationshipCalculation


def chart_confidence_notes(relationship: RelationshipCalculation) -> list[str]:
    """Return user-facing notes about chart confidence and missing birth times."""
    notes: list[str] = []

    for label, chart in [("Person A", relationship.person_a), ("Person B", relationship.person_b)]:
        if not chart.birth.time_known or not chart.birth.time:
            notes.append(
                f"{label} has an unknown birth time. Planetary placements are calculated for local noon; "
                "angles, houses, and house overlays should not be treated as reliable."
            )
        if chart.warnings:
            notes.extend(f"{label}: {warning}" for warning in chart.warnings)

    if relationship.composite and relationship.composite.warnings:
        notes.extend(f"Composite: {warning}" for warning in relationship.composite.warnings)

    if not notes:
        notes.append(
            "Both birth times are marked as known. Angles, houses, and house overlays are available, "
            "but should still be validated against a trusted chart source during this prototype phase."
        )

    return notes


def confidence_markdown(relationship: RelationshipCalculation) -> str:
    return "\n".join(f"- {note}" for note in chart_confidence_notes(relationship))
