"""Aspect detection utilities."""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import Aspect
from .zodiac import shortest_arc


@dataclass(frozen=True)
class AspectDefinition:
    name: str
    angle: float
    default_orb: float


MAJOR_ASPECTS = [
    AspectDefinition("conjunction", 0.0, 8.0),
    AspectDefinition("opposition", 180.0, 8.0),
    AspectDefinition("trine", 120.0, 6.0),
    AspectDefinition("square", 90.0, 6.0),
    AspectDefinition("sextile", 60.0, 4.0),
]

LUMINARIES = {"sun", "moon"}
PERSONAL = {"sun", "moon", "mercury", "venus", "mars"}
ANGLES = {"ascendant", "midheaven", "asc", "mc"}


def orb_for_points(point_a: str, point_b: str, aspect: AspectDefinition) -> float:
    """Return an orb for a pair of points.

    This is deliberately simple for Phase 0/1. We can tune later from case studies.
    """
    a = point_a.lower()
    b = point_b.lower()

    if a in ANGLES or b in ANGLES:
        return min(aspect.default_orb, 5.0)
    if a in LUMINARIES and b in LUMINARIES:
        return max(aspect.default_orb, 8.0)
    if a in PERSONAL and b in PERSONAL:
        return aspect.default_orb
    if a in PERSONAL or b in PERSONAL:
        return min(aspect.default_orb, 5.0)
    return min(aspect.default_orb, 3.0)


def detect_aspect(point_a: str, lon_a: float, point_b: str, lon_b: float) -> Aspect | None:
    """Detect the closest major aspect between two points, if within orb."""
    distance = shortest_arc(lon_a, lon_b)
    best: Aspect | None = None

    for definition in MAJOR_ASPECTS:
        orb = abs(distance - definition.angle)
        allowed = orb_for_points(point_a, point_b, definition)
        if orb <= allowed:
            candidate = Aspect(
                point_a=point_a,
                point_b=point_b,
                aspect=definition.name,
                exact_angle=definition.angle,
                orb=round(orb, 6),
            )
            if best is None or candidate.orb < best.orb:
                best = candidate

    return best


def detect_aspects(points_a: dict[str, float], points_b: dict[str, float]) -> list[Aspect]:
    """Detect major aspects between two point dictionaries."""
    aspects: list[Aspect] = []
    for name_a, lon_a in points_a.items():
        for name_b, lon_b in points_b.items():
            aspect = detect_aspect(name_a, lon_a, name_b, lon_b)
            if aspect is not None:
                aspects.append(aspect)
    return sorted(aspects, key=lambda item: item.orb)
