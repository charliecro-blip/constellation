"""Composite chart utilities."""

from __future__ import annotations

from .aspects import detect_aspects
from .chart import chart_points
from .schemas import Aspect, BirthData, Chart, Placement
from .zodiac import midpoint_longitude, to_zodiac_position


COMPOSITE_BODY_ORDER = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "north_node",
    "south_node",
]


def calculate_midpoint_composite(chart_a: Chart, chart_b: Chart) -> Chart:
    """Calculate a simple midpoint composite chart from two natal charts.

    Phase 1 calculates planetary midpoint positions. Composite angles and houses
    require a more careful method and are intentionally omitted for now.
    """
    placements: dict[str, Placement] = {}

    for body in COMPOSITE_BODY_ORDER:
        if body not in chart_a.placements or body not in chart_b.placements:
            continue
        midpoint = midpoint_longitude(
            chart_a.placements[body].longitude,
            chart_b.placements[body].longitude,
        )
        pos = to_zodiac_position(midpoint)
        placements[body] = Placement(
            body=body,
            longitude=pos.longitude,
            sign=pos.sign,
            sign_index=pos.sign_index,
            degree=pos.degree,
            house=None,
        )

    birth = BirthData(
        name=f"Composite: {chart_a.name} / {chart_b.name}",
        date="0001-01-01",
        time=None,
        time_known=False,
        latitude=0.0,
        longitude=0.0,
        timezone="UTC",
    )

    return Chart(
        name=birth.name,
        birth=birth,
        julian_day_ut=None,
        house_system="midpoint_composite_no_houses",
        placements=placements,
        angles={},
        houses=None,
        warnings=[
            "Composite planets are midpoint positions. Composite angles/houses are omitted in this phase."
        ],
    )


def composite_aspects(composite: Chart) -> list[Aspect]:
    """Detect aspects within a composite chart."""
    points = chart_points(composite, include_angles=False)
    aspects: list[Aspect] = []
    names = list(points.keys())
    for i, name_a in enumerate(names):
        for name_b in names[i + 1 :]:
            from .aspects import detect_aspect

            aspect = detect_aspect(name_a, points[name_a], name_b, points[name_b])
            if aspect is not None:
                aspects.append(aspect)
    return sorted(aspects, key=lambda item: item.orb)
