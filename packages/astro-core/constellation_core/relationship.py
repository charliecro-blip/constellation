"""Relationship calculation utilities."""

from __future__ import annotations

from .aspects import detect_aspects
from .chart import calculate_chart, chart_points
from .composite import calculate_midpoint_composite, composite_aspects
from .schemas import BirthData, RelationshipCalculation


def calculate_relationship(
    person_a: BirthData,
    person_b: BirthData,
    house_system: str = "whole_sign",
) -> RelationshipCalculation:
    """Calculate natal charts, synastry aspects, and midpoint composite."""
    chart_a = calculate_chart(person_a, house_system=house_system)
    chart_b = calculate_chart(person_b, house_system=house_system)

    synastry = detect_aspects(chart_points(chart_a), chart_points(chart_b))
    composite = calculate_midpoint_composite(chart_a, chart_b)
    comp_aspects = composite_aspects(composite)

    return RelationshipCalculation(
        person_a=chart_a,
        person_b=chart_b,
        synastry_aspects=synastry,
        composite=composite,
        composite_aspects=comp_aspects,
    )
