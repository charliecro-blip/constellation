"""Early deterministic pattern detection.

The goal of this module is to turn calculated chart data into ranked,
structured evidence for a future report generator. It does not write prose.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .schemas import Aspect, Chart, HouseOverlay, RelationshipCalculation


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

        if "sun" in pts and "moon" in pts:
            patterns.append(Pattern(
                id="synastry_sun_moon",
                layer="synastry",
                category="recognition",
                priority=84 + bonus,
                title="Sun and Moon contact",
                evidence=[_evidence(aspect)],
                key="synastry.sun_moon",
                confidence="high",
            ))

        if pts == {"moon"}:
            patterns.append(Pattern(
                id="synastry_moon_moon",
                layer="synastry",
                category="emotional_translation",
                priority=80 + bonus,
                title="Moon to Moon contact",
                evidence=[_evidence(aspect)],
                key="synastry.moon_moon",
                confidence="high",
            ))

        if "moon" in pts and "venus" in pts:
            patterns.append(Pattern(
                id="synastry_moon_venus",
                layer="synastry",
                category="affection",
                priority=78 + bonus,
                title="Moon and Venus contact",
                evidence=[_evidence(aspect)],
                key="synastry.moon_venus",
                confidence="high",
            ))

        if "moon" in pts and "mars" in pts:
            patterns.append(Pattern(
                id="synastry_moon_mars",
                layer="synastry",
                category="emotional_activation",
                priority=78 + bonus,
                title="Moon and Mars contact",
                evidence=[_evidence(aspect)],
                key="synastry.moon_mars",
                confidence="medium",
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

        if pts == {"mercury"}:
            patterns.append(Pattern(
                id="synastry_mercury_mercury",
                layer="synastry",
                category="communication",
                priority=72 + bonus,
                title="Mercury to Mercury contact",
                evidence=[_evidence(aspect)],
                key="synastry.mercury_mercury",
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

        if "venus" in pts and "pluto" in pts:
            patterns.append(Pattern(
                id="synastry_venus_pluto",
                layer="synastry",
                category="attraction_intensity",
                priority=82 + bonus,
                title="Venus and Pluto contact",
                evidence=[_evidence(aspect)],
                key="synastry.venus_pluto",
                confidence="medium",
            ))

        if "mars" in pts and "pluto" in pts:
            patterns.append(Pattern(
                id="synastry_mars_pluto",
                layer="synastry",
                category="intensity",
                priority=82 + bonus,
                title="Mars and Pluto contact",
                evidence=[_evidence(aspect)],
                key="synastry.mars_pluto",
                confidence="medium",
            ))

        if "venus" in pts and "saturn" in pts:
            patterns.append(Pattern(
                id="synastry_venus_saturn",
                layer="synastry",
                category="bond_structure",
                priority=76 + bonus,
                title="Venus and Saturn contact",
                evidence=[_evidence(aspect)],
                key="synastry.venus_saturn",
                confidence="medium",
            ))

        if "mars" in pts and "saturn" in pts:
            patterns.append(Pattern(
                id="synastry_mars_saturn",
                layer="synastry",
                category="action_structure",
                priority=74 + bonus,
                title="Mars and Saturn contact",
                evidence=[_evidence(aspect)],
                key="synastry.mars_saturn",
                confidence="medium",
            ))

    return patterns


def _overlay_evidence(overlay: HouseOverlay) -> str:
    return f"{overlay.planet_owner} {overlay.body} in {overlay.house_owner} house {overlay.house}"


def detect_house_overlay_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns: list[Pattern] = []
    important_houses = {
        1: ("identity_body", 76),
        4: ("home_roots", 80),
        5: ("romance_creativity", 74),
        6: ("daily_life", 72),
        7: ("partnership", 82),
        8: ("intimacy_depth", 80),
        10: ("public_direction", 74),
        12: ("hidden_field", 76),
    }
    important_bodies = {"sun", "moon", "mercury", "venus", "mars", "saturn", "pluto", "north_node", "south_node"}

    for overlay in relationship.house_overlays:
        if overlay.house not in important_houses or overlay.body not in important_bodies:
            continue
        category, priority = important_houses[overlay.house]
        patterns.append(Pattern(
            id=f"overlay_{overlay.planet_owner}_{overlay.body}_in_{overlay.house_owner}_house_{overlay.house}",
            layer="house_overlay",
            category=category,
            priority=priority,
            title=f"{overlay.body.title()} in the other's {overlay.house} house",
            evidence=[_overlay_evidence(overlay)],
            key=f"overlay.house_{overlay.house}",
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

        if "venus" in pts and "mars" in pts:
            patterns.append(Pattern(
                id="composite_venus_mars",
                layer="composite",
                category="desire",
                priority=82 + bonus,
                title="Composite Venus and Mars contact",
                evidence=[_evidence(aspect)],
                key="composite.venus_mars",
                confidence="high",
            ))

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

        if "venus" in pts and "saturn" in pts:
            patterns.append(Pattern(
                id="composite_venus_saturn",
                layer="composite",
                category="bond_structure",
                priority=80 + bonus,
                title="Composite Venus and Saturn contact",
                evidence=[_evidence(aspect)],
                key="composite.venus_saturn",
                confidence="medium",
            ))

        if "sun" in pts and "saturn" in pts:
            patterns.append(Pattern(
                id="composite_sun_saturn",
                layer="composite",
                category="relationship_structure",
                priority=80 + bonus,
                title="Composite Sun and Saturn contact",
                evidence=[_evidence(aspect)],
                key="composite.sun_saturn",
                confidence="medium",
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
    patterns.extend(detect_house_overlay_patterns(relationship))
    if relationship.composite is not None:
        patterns.extend(detect_composite_patterns(relationship.composite, relationship.composite_aspects))
    return sorted(patterns, key=lambda pattern: pattern.priority, reverse=True)
