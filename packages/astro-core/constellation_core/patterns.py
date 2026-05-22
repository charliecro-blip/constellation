"""Early deterministic pattern detection.

The goal of this module is to turn calculated chart data into ranked,
structured evidence for a future report generator. It does not write prose.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .schemas import Aspect, Chart, RelationshipCalculation


class Pattern(BaseModel):
    id: str
    layer: str
    category: str
    priority: int = Field(ge=0, le=100)
    title: str
    evidence: list[str]
    key: str
    confidence: str = "medium"


def _points(aspect: Aspect) -> set[str]:
    return {aspect.point_a.lower(), aspect.point_b.lower()}


def _evidence(aspect: Aspect) -> str:
    return f"{aspect.point_a} {aspect.aspect} {aspect.point_b}; orb {aspect.orb:.2f}"


def _bonus(aspect: Aspect) -> int:
    return min(max(0, int(10 - min(aspect.orb, 10))), 10)


def detect_synastry_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns: list[Pattern] = []

    for aspect in relationship.synastry_aspects:
        pts = _points(aspect)
        bonus = _bonus(aspect)

        if "ascendant" in pts and "venus" in pts:
            patterns.append(Pattern(
                id="synastry_venus_ascendant",
                layer="synastry",
                category="attraction",
                priority=90 + bonus,
                title="Venus and Ascendant contact",
                evidence=[_evidence(aspect)],
                key="synastry.venus_ascendant",
                confidence="high",
            ))

        if "venus" in pts and "mars" in pts:
            patterns.append(Pattern(
                id="synastry_venus_mars",
                layer="synastry",
                category="desire",
                priority=82 + bonus,
                title="Venus and Mars contact",
                evidence=[_evidence(aspect)],
                key="synastry.venus_mars",
                confidence="high",
            ))

        if "mercury" in pts and "mars" in pts:
            patterns.append(Pattern(
                id="synastry_mercury_mars",
                layer="synastry",
                category="communication",
                priority=76 + bonus,
                title="Mercury and Mars contact",
                evidence=[_evidence(aspect)],
                key="synastry.mercury_mars",
                confidence="medium",
            ))

        if "moon" in pts and "saturn" in pts:
            patterns.append(Pattern(
                id="synastry_moon_saturn",
                layer="synastry",
                category="emotional_structure",
                priority=78 + bonus,
                title="Moon and Saturn contact",
                evidence=[_evidence(aspect)],
                key="synastry.moon_saturn",
                confidence="medium",
            ))

        if "moon" in pts and "pluto" in pts:
            patterns.append(Pattern(
                id="synastry_moon_pluto",
                layer="synastry",
                category="emotional_intensity",
                priority=82 + bonus,
                title="Moon and Pluto contact",
                evidence=[_evidence(aspect)],
                key="synastry.moon_pluto",
                confidence="medium",
            ))

    return patterns


def detect_composite_patterns(composite: Chart, composite_aspects: list[Aspect]) -> list[Pattern]:
    patterns: list[Pattern] = []

    moon = composite.placements.get("moon")
    if moon is not None:
        patterns.append(Pattern(
            id=f"composite_moon_{moon.sign.lower()}",
            layer="composite",
            category="emotional_body",
            priority=76,
            title=f"Composite Moon in {moon.sign}",
            evidence=[f"Composite Moon {moon.degree:.2f} {moon.sign}"],
            key=f"composite.moon.{moon.sign.lower()}",
            confidence="high",
        ))

    sun = composite.placements.get("sun")
    if sun is not None:
        patterns.append(Pattern(
            id=f"composite_sun_{sun.sign.lower()}",
            layer="composite",
            category="relationship_identity",
            priority=70,
            title=f"Composite Sun in {sun.sign}",
            evidence=[f"Composite Sun {sun.degree:.2f} {sun.sign}"],
            key=f"composite.sun.{sun.sign.lower()}",
            confidence="high",
        ))

    for aspect in composite_aspects:
        pts = _points(aspect)
        bonus = _bonus(aspect)

        if "mars" in pts and "pluto" in pts:
            patterns.append(Pattern(
                id="composite_mars_pluto",
                layer="composite",
                category="intensity",
                priority=88 + bonus,
                title="Composite Mars and Pluto contact",
                evidence=[_evidence(aspect)],
                key="composite.mars_pluto",
                confidence="high",
            ))

        if "moon" in pts and "saturn" in pts:
            patterns.append(Pattern(
                id="composite_moon_saturn",
                layer="composite",
                category="emotional_structure",
                priority=82 + bonus,
                title="Composite Moon and Saturn contact",
                evidence=[_evidence(aspect)],
                key="composite.moon_saturn",
                confidence="medium",
            ))

        if "moon" in pts and "uranus" in pts:
            patterns.append(Pattern(
                id="composite_moon_uranus",
                layer="composite",
                category="emotional_variability",
                priority=82 + bonus,
                title="Composite Moon and Uranus contact",
                evidence=[_evidence(aspect)],
                key="composite.moon_uranus",
                confidence="medium",
            ))

    return patterns


def detect_relationship_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns = detect_synastry_patterns(relationship)
    if relationship.composite is not None:
        patterns.extend(detect_composite_patterns(relationship.composite, relationship.composite_aspects))
    return sorted(patterns, key=lambda pattern: pattern.priority, reverse=True)
