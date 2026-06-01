"""Early deterministic pattern detection.

The detector turns calculated chart data into ranked, structured evidence for
report generation. The report layer decides which detected patterns deserve
user-facing emphasis.
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


def _display_point(point: str) -> str:
    return point.replace("_", " ").title()


def _points(aspect: Aspect) -> set[str]:
    return {aspect.point_a.lower(), aspect.point_b.lower()}


def _aspect_word(aspect_name: str) -> str:
    return {"conjunction": "conjunct", "opposition": "opposite"}.get(aspect_name, aspect_name)


def _synastry_title(aspect: Aspect, relationship: RelationshipCalculation) -> str:
    left = f"{relationship.person_a.name}'s {_display_point(aspect.point_a)}"
    right = f"{relationship.person_b.name}'s {_display_point(aspect.point_b)}"
    return f"{left} {_aspect_word(aspect.aspect)} {right}"


def _composite_title(aspect: Aspect) -> str:
    return f"Composite {_display_point(aspect.point_a)} {_aspect_word(aspect.aspect)} {_display_point(aspect.point_b)}"


def _evidence(aspect: Aspect, relationship: RelationshipCalculation) -> str:
    return f"{_synastry_title(aspect, relationship)}; orb {aspect.orb:.2f}"


def _composite_evidence(aspect: Aspect) -> str:
    return f"{_composite_title(aspect)}; orb {aspect.orb:.2f}"


def _bonus(aspect: Aspect) -> int:
    return min(max(0, int(10 - min(aspect.orb, 10))), 10)


def _pair_key(*points: str) -> str:
    return "_".join(sorted(point.lower() for point in points))


def _angle_category(body: str) -> str:
    if body in {"sun", "moon"}:
        return "angle_luminary"
    if body == "venus":
        return "attraction"
    if body == "mars":
        return "embodied_activation"
    if body == "saturn":
        return "angle_structure"
    if body in {"north_node", "south_node"}:
        return "fated_axis"
    return "angular_contact"


def _angle_priority(angle: str, body: str) -> int:
    if angle == "ascendant" and body in {"sun", "moon"}:
        return 94
    if angle == "ascendant" and body == "venus":
        return 90
    if angle == "ascendant" and body in {"mars", "saturn", "north_node", "south_node"}:
        return 86
    if angle == "midheaven" and body in {"sun", "moon"}:
        return 88
    if angle == "midheaven" and body in {"venus", "saturn", "north_node", "south_node"}:
        return 84
    return 80


def _synastry_pattern(
    aspect: Aspect,
    relationship: RelationshipCalculation,
    *,
    pattern_id: str,
    category: str,
    priority: int,
    key: str,
    confidence: str = "medium",
) -> Pattern:
    return Pattern(
        id=pattern_id,
        layer="synastry",
        category=category,
        priority=min(100, priority + _bonus(aspect)),
        title=_synastry_title(aspect, relationship),
        evidence=[_evidence(aspect, relationship)],
        key=key,
        confidence=confidence,
    )


def detect_synastry_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns: list[Pattern] = []
    important_angle_bodies = {"sun", "moon", "venus", "mars", "saturn", "north_node", "south_node"}

    for aspect in relationship.synastry_aspects:
        pts = _points(aspect)
        point_a = aspect.point_a.lower()
        point_b = aspect.point_b.lower()
        pair = _pair_key(point_a, point_b)

        if point_a in {"ascendant", "midheaven"} and point_b in important_angle_bodies:
            key = f"synastry.angle_{point_a}_{point_b}"
            if point_a == "ascendant" and point_b == "venus":
                key = "synastry.venus_ascendant"
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id=f"synastry_{point_a}_{point_b}",
                category=_angle_category(point_b),
                priority=_angle_priority(point_a, point_b),
                key=key,
                confidence="high",
            ))
            continue

        if pair == "mars_venus":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_venus_mars",
                category="desire",
                priority=82,
                key="synastry.venus_mars",
                confidence="high",
            ))

        if pair == "moon_sun":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_sun_moon",
                category="recognition",
                priority=84,
                key="synastry.sun_moon",
                confidence="high",
            ))

        if pts == {"moon"}:
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_moon_moon",
                category="emotional_translation",
                priority=80,
                key="synastry.moon_moon",
                confidence="high",
            ))

        if pair == "moon_venus":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_moon_venus",
                category="affection",
                priority=78,
                key="synastry.moon_venus",
                confidence="high",
            ))

        if pair == "mars_moon":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_moon_mars",
                category="emotional_activation",
                priority=78,
                key="synastry.moon_mars",
            ))

        if pair == "mars_mercury":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_mercury_mars",
                category="communication",
                priority=76,
                key="synastry.mercury_mars",
            ))

        if pts == {"mercury"}:
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_mercury_mercury",
                category="communication",
                priority=72,
                key="synastry.mercury_mercury",
            ))

        if pair == "moon_saturn":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_moon_saturn",
                category="emotional_structure",
                priority=78,
                key="synastry.moon_saturn",
            ))

        if pair == "moon_pluto":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_moon_pluto",
                category="emotional_intensity",
                priority=82,
                key="synastry.moon_pluto",
            ))

        if pair == "pluto_venus":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_venus_pluto",
                category="attraction_intensity",
                priority=82,
                key="synastry.venus_pluto",
            ))

        if pair == "mars_pluto":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_mars_pluto",
                category="intensity",
                priority=82,
                key="synastry.mars_pluto",
            ))

        if pair == "saturn_venus":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_venus_saturn",
                category="bond_structure",
                priority=76,
                key="synastry.venus_saturn",
            ))

        if pair == "mars_saturn":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_mars_saturn",
                category="action_structure",
                priority=74,
                key="synastry.mars_saturn",
            ))

    return patterns


def _ordinal(number: int) -> str:
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _overlay_evidence(overlay: HouseOverlay, relationship: RelationshipCalculation) -> str:
    planet_owner = relationship.person_a.name if overlay.planet_owner == "person_a" else relationship.person_b.name
    house_owner = relationship.person_a.name if overlay.house_owner == "person_a" else relationship.person_b.name
    return f"{planet_owner}'s {_display_point(overlay.body)} in {house_owner}'s {_ordinal(overlay.house)} house"


def detect_house_overlay_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns: list[Pattern] = []
    important_houses = {
        1: ("identity_body", 58),
        4: ("home_roots", 62),
        5: ("romance_creativity", 56),
        6: ("daily_life", 54),
        7: ("partnership", 64),
        8: ("intimacy_depth", 62),
        10: ("public_direction", 56),
        12: ("hidden_field", 58),
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
            title=_overlay_evidence(overlay, relationship),
            evidence=[_overlay_evidence(overlay, relationship)],
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
            priority=66,
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
            priority=62,
            title=f"Composite Sun in {sun.sign}",
            evidence=[f"Composite Sun {sun.degree:.2f} {sun.sign}"],
            key=f"composite.sun.{sun.sign.lower()}",
            confidence="high",
        ))

    hard_aspects = {"conjunction", "opposition", "square"}
    for aspect in composite_aspects:
        pair = _pair_key(aspect.point_a, aspect.point_b)
        bonus = _bonus(aspect)
        hard_bonus = 6 if aspect.aspect in hard_aspects else 0
        trine_penalty = 4 if aspect.aspect == "trine" else 0

        composite_specs = {
            "mars_venus": ("composite_venus_mars", "desire", 78, "composite.venus_mars", "high"),
            "mars_pluto": ("composite_mars_pluto", "intensity", 80, "composite.mars_pluto", "high"),
            "saturn_venus": ("composite_venus_saturn", "bond_structure", 78, "composite.venus_saturn", "medium"),
            "saturn_sun": ("composite_sun_saturn", "relationship_structure", 78, "composite.sun_saturn", "medium"),
            "moon_saturn": ("composite_moon_saturn", "emotional_structure", 82, "composite.moon_saturn", "medium"),
            "moon_uranus": ("composite_moon_uranus", "emotional_variability", 84, "composite.moon_uranus", "medium"),
        }
        if pair not in composite_specs:
            continue
        pattern_id, category, base_priority, key, confidence = composite_specs[pair]
        patterns.append(Pattern(
            id=pattern_id,
            layer="composite",
            category=category,
            priority=min(100, base_priority + bonus + hard_bonus - trine_penalty),
            title=_composite_title(aspect),
            evidence=[_composite_evidence(aspect)],
            key=key,
            confidence=confidence,
        ))

    return patterns


def detect_relationship_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns = detect_synastry_patterns(relationship)
    patterns.extend(detect_house_overlay_patterns(relationship))
    if relationship.composite is not None:
        patterns.extend(detect_composite_patterns(relationship.composite, relationship.composite_aspects))
    return sorted(patterns, key=lambda pattern: pattern.priority, reverse=True)
