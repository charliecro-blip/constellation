"""Early deterministic pattern detection.

The detector turns calculated chart data into ranked, structured evidence for
report generation. The report layer decides which detected patterns deserve
user-facing emphasis.
"""

from __future__ import annotations

from itertools import combinations

from pydantic import BaseModel, Field

from .asteroid_policy import (
    ASTEROID_CENTRAL_TARGETS,
    DEFAULT_ASTEROID_ORB,
    DEFAULT_REPORT_ASTEROIDS,
    RELATIONSHIP_RELEVANT_HOUSES,
    SUPPORTED_ASTEROID_POINTS,
)
from .schemas import Aspect, Chart, HouseOverlay, RelationshipCalculation
from .rulerships import descendant_sign, relationship_house_rulers
from .zodiac import shortest_arc


SIGN_ELEMENTS = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

SYNTHESIS_POINTS = {
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
    "chiron",
    "juno",
    "ceres",
    "vesta",
}

ASTEROID_POINTS = SUPPORTED_ASTEROID_POINTS
REPORT_ASTEROID_POINTS = DEFAULT_REPORT_ASTEROIDS
COMPOSITE_ASTEROID_TARGETS = {"sun", "moon", "venus", "mars"}
RELATIONSHIP_ASTEROID_MEANINGS = {
    "juno": "commitment terms",
    "chiron": "tender wound/healing point",
    "ceres": "care and nourishment",
    "vesta": "devotion and private focus",
}


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
        return "nodal_axis"
    return "angular_contact"


def _angle_priority(angle: str, body: str) -> int:
    if angle == "ascendant" and body in {"sun", "moon"}:
        return 94
    if angle == "ascendant" and body == "venus":
        return 90
    if angle == "ascendant" and body in {"mars", "saturn", "north_node", "south_node"}:
        return 86
    if angle == "midheaven" and body in {"sun", "moon"}:
        return 82
    if angle == "midheaven" and body in {"venus", "saturn", "north_node", "south_node"}:
        return 78
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

        if point_b in {"ascendant", "midheaven"} and point_a in important_angle_bodies:
            key = f"synastry.angle_{point_b}_{point_a}"
            if point_b == "ascendant" and point_a == "venus":
                key = "synastry.venus_ascendant"
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id=f"synastry_{point_a}_{point_b}",
                category=_angle_category(point_a),
                priority=_angle_priority(point_b, point_a),
                key=key,
                confidence="high",
            ))
            continue


        asteroid_points = pts & ASTEROID_POINTS
        non_asteroid_points = pts - ASTEROID_POINTS
        if asteroid_points and non_asteroid_points and aspect.orb <= DEFAULT_ASTEROID_ORB:
            asteroid = next(iter(asteroid_points))
            other = next(iter(non_asteroid_points))
            if asteroid in REPORT_ASTEROID_POINTS and other in ASTEROID_CENTRAL_TARGETS:
                meaning = RELATIONSHIP_ASTEROID_MEANINGS[asteroid]
                patterns.append(_synastry_pattern(
                    aspect,
                    relationship,
                    pattern_id=f"synastry_{asteroid}_{other}",
                    category="asteroid_support",
                    priority=58 if other == "midheaven" else 64,
                    key=f"synastry.asteroid.{asteroid}.{other}",
                    confidence="medium",
                ).model_copy(update={"evidence": [f"{_evidence(aspect, relationship)}; {meaning}"]}))

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

        # Sun conjunct Sun: friend/recognition signal, not a marriage/partnership indicator.
        # Jung empirical data (via Eddington): ranks #49/50 in most-observed marital aspects.
        # Base priority 55 keeps it below the synthesis packet threshold (70).
        if pts == {"sun"} and aspect.aspect == "conjunction":
            patterns.append(_synastry_pattern(
                aspect,
                relationship,
                pattern_id="synastry_sun_sun_conjunction",
                category="recognition",
                priority=55,
                key="synastry.sun_sun_conjunction",
                confidence="medium",
            ))

        # Mars opposite Mars: conflict-of-will pattern. Embed Mars signs for water-earth
        # penalty check in weighting.py.
        if pts == {"mars"} and aspect.aspect == "opposition":
            mars_a = relationship.person_a.placements.get("mars")
            mars_b = relationship.person_b.placements.get("mars")
            sign_note = (
                f"; Mars signs: {mars_a.sign.lower()}/{mars_b.sign.lower()}"
                if mars_a and mars_b
                else ""
            )
            patterns.append(Pattern(
                id="synastry_mars_mars_opposition",
                layer="synastry",
                category="volatility",
                priority=min(100, 64 + _bonus(aspect)),
                title=_synastry_title(aspect, relationship),
                evidence=[_evidence(aspect, relationship) + sign_note],
                key="synastry.mars_mars_opposition",
                confidence="medium",
            ))

    return patterns


PERSONAL_PLANETS = {"sun", "moon", "mercury", "venus", "mars"}


def _detect_stellium_gap(relationship: RelationshipCalculation) -> list[Pattern]:
    """Detect if one person has 3+ personal planets in one sign with no partner planet there.

    Informational only (priority 40) — surfaces in diagnostics, not in the main report.
    Doctrine: Eddington Worst — a stellium without a partner conjunction tends to produce
    low-resonance synastry. NOT a compatibility score element; house overlays can override.
    """
    patterns: list[Pattern] = []
    for owner, other, owner_chart, other_chart in [
        ("person_a", "person_b", relationship.person_a, relationship.person_b),
        ("person_b", "person_a", relationship.person_b, relationship.person_a),
    ]:
        sign_counts: dict[str, list[str]] = {}
        for body, placement in owner_chart.placements.items():
            if body not in PERSONAL_PLANETS:
                continue
            sign_counts.setdefault(placement.sign, []).append(body)

        for sign, bodies in sign_counts.items():
            if len(bodies) < 3:
                continue
            other_signs = {
                p.sign for b, p in other_chart.placements.items()
                if b in PERSONAL_PLANETS
            }
            if sign in other_signs:
                continue
            body_labels = [_display_point(b) for b in sorted(bodies)]
            bodies_str = ", ".join(body_labels)
            patterns.append(Pattern(
                id=f"stellium_gap_{owner}_{sign.lower()}",
                layer="synastry",
                category="informational",
                priority=40,
                title=f"{owner_chart.name}'s {sign} stellium ({bodies_str}) — no {other_chart.name} planet in {sign}",
                evidence=[
                    f"{owner_chart.name} has {bodies_str} in {sign}; "
                    f"{other_chart.name} has no personal planet there. "
                    f"A partner planet conjunct a stellium sign tends to increase felt resonance — "
                    f"strong house overlays can compensate for this gap."
                ],
                key="synastry.stellium_resonance.missing",
                confidence="medium",
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
    important_bodies = {"sun", "moon", "mercury", "venus", "mars", "saturn", "pluto"} | REPORT_ASTEROID_POINTS

    for overlay in relationship.house_overlays:
        if overlay.house not in important_houses or overlay.body not in important_bodies:
            continue
        category, priority = important_houses[overlay.house]
        if overlay.body in ASTEROID_POINTS:
            if overlay.house not in RELATIONSHIP_RELEVANT_HOUSES:
                continue
            priority -= 12
            category = "asteroid_overlay"
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


def _placement_label(body: str) -> str:
    return _display_point(body)


def _format_body_list(bodies: list[str]) -> str:
    labels = [_placement_label(body) for body in bodies]
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return f"{', '.join(labels[:-1])}, and {labels[-1]}"


def _angle_axis(angle_name: str) -> str:
    if angle_name in {"midheaven", "imum_coeli"}:
        return "MC/IC"
    return "Asc/Desc"


def _angle_distance(placement_longitude: float, angle_longitude: float) -> tuple[str, float]:
    direct = shortest_arc(placement_longitude, angle_longitude)
    opposite = shortest_arc(placement_longitude, (angle_longitude + 180) % 360)
    if direct <= opposite:
        return "direct", direct
    return "opposite", opposite


def _detect_composite_stelliums(composite: Chart) -> list[Pattern]:
    patterns: list[Pattern] = []
    by_sign: dict[str, list[str]] = {}
    for body, placement in composite.placements.items():
        if body in SYNTHESIS_POINTS:
            by_sign.setdefault(placement.sign, []).append(body)
    for sign, bodies in by_sign.items():
        if len(bodies) >= 3:
            patterns.append(Pattern(
                id=f"composite_stellium_{sign.lower()}",
                layer="composite",
                category="composite_concentration",
                priority=90 if sign == "Capricorn" else 86,
                title=f"Composite {sign} concentration",
                evidence=[f"{_format_body_list(bodies)} in {sign}"],
                key=f"composite.stellium.{sign.lower()}",
                confidence="high",
            ))

    placements = sorted(
        [(body, placement.longitude) for body, placement in composite.placements.items() if body in SYNTHESIS_POINTS],
        key=lambda item: item[1],
    )
    chains: list[list[str]] = []
    current: list[str] = []
    previous_longitude: float | None = None
    for body, longitude in placements:
        if previous_longitude is None or abs(longitude - previous_longitude) <= 8:
            current.append(body)
        else:
            if len(current) >= 3:
                chains.append(current)
            current = [body]
        previous_longitude = longitude
    if len(current) >= 3:
        chains.append(current)
    for index, bodies in enumerate(chains, start=1):
        patterns.append(Pattern(
            id=f"composite_conjunction_cluster_{index}",
            layer="composite",
            category="composite_concentration",
            priority=88,
            title=f"Composite conjunction cluster: {_format_body_list(bodies)}",
            evidence=["Close conjunction chain in the composite chart"],
            key="composite.conjunction_cluster",
            confidence="medium",
        ))
    return patterns


def _detect_composite_angle_contacts(composite: Chart) -> list[Pattern]:
    patterns: list[Pattern] = []
    if not composite.angles:
        return patterns
    angle_specs = [("ascendant", composite.angles.get("ascendant")), ("midheaven", composite.angles.get("midheaven"))]
    seen_node_axes: set[str] = set()
    for body, placement in composite.placements.items():
        if body not in SYNTHESIS_POINTS:
            continue
        for angle_name, angle in angle_specs:
            if angle is None:
                continue
            direction, distance = _angle_distance(placement.longitude, angle.longitude)
            if distance > 3:
                continue
            axis = _angle_axis(angle_name)
            if body in {"north_node", "south_node"}:
                key = f"composite.nodes_on_{axis.lower().replace('/', '_')}"
                if key in seen_node_axes:
                    continue
                seen_node_axes.add(key)
                title = f"Composite nodal axis on {axis}"
                priority = 98 if axis == "MC/IC" else 96
                category = "nodal_axis"
            else:
                contact = angle.name if direction == "direct" else ("Descendant" if angle_name == "ascendant" else "IC")
                title = f"Composite {_display_point(body)} on {contact}"
                priority = 92 if body in {"sun", "moon"} else 88
                category = "composite_angular_contact"
                key = "composite.planet_on_angle"
            patterns.append(Pattern(
                id=f"composite_{body}_on_{angle_name}_{direction}",
                layer="composite",
                category=category,
                priority=priority,
                title=title,
                evidence=[f"{_display_point(body)} within {distance:.2f} degrees of composite {axis}"],
                key=key,
                confidence="high",
            ))
    return patterns


def _aspect_lookup(composite_aspects: list[Aspect]) -> dict[tuple[str, str], Aspect]:
    lookup: dict[tuple[str, str], Aspect] = {}
    for aspect in composite_aspects:
        lookup[tuple(sorted((aspect.point_a.lower(), aspect.point_b.lower())))] = aspect
    return lookup


def _detect_composite_aspect_patterns(composite: Chart, composite_aspects: list[Aspect]) -> list[Pattern]:
    patterns: list[Pattern] = []
    lookup = _aspect_lookup(composite_aspects)
    bodies = [body for body in composite.placements if body in SYNTHESIS_POINTS and body not in {"north_node", "south_node"}]
    for trio in combinations(sorted(bodies), 3):
        aspects = [lookup.get(tuple(sorted(pair))) for pair in combinations(trio, 2)]
        if all(aspect is not None and aspect.aspect == "trine" for aspect in aspects):
            signs = [composite.placements[body].sign for body in trio]
            elements = {SIGN_ELEMENTS.get(sign) for sign in signs}
            element_note = f" in {elements.pop()} signs" if len(elements) == 1 and None not in elements else ""
            patterns.append(Pattern(
                id=f"composite_grand_trine_{'_'.join(trio)}",
                layer="composite",
                category="aspect_pattern",
                priority=78,
                title=f"Composite grand trine: {_format_body_list(list(trio))}",
                evidence=[f"Three trines{element_note}"],
                key="composite.grand_trine",
                confidence="medium",
            ))
    for opposition in [aspect for aspect in composite_aspects if aspect.aspect == "opposition"]:
        ends = {opposition.point_a.lower(), opposition.point_b.lower()}
        for apex in bodies:
            if apex in ends:
                continue
            square_aspects = [lookup.get(tuple(sorted((apex, end)))) for end in ends]
            if all(aspect is not None and aspect.aspect == "square" for aspect in square_aspects):
                trio = tuple(sorted([*ends, apex]))
                patterns.append(Pattern(
                    id=f"composite_t_square_{'_'.join(trio)}",
                    layer="composite",
                    category="aspect_pattern",
                    priority=82,
                    title=f"Composite T-square with {_display_point(apex)} as pressure point",
                    evidence=[f"{_display_point(apex)} squares an opposition between {_format_body_list(sorted(ends))}"],
                    key="composite.t_square",
                    confidence="medium",
                ))
    return patterns


def detect_composite_patterns(composite: Chart, composite_aspects: list[Aspect]) -> list[Pattern]:
    patterns: list[Pattern] = []
    patterns.extend(_detect_composite_angle_contacts(composite))
    patterns.extend(_detect_composite_stelliums(composite))
    patterns.extend(_detect_composite_aspect_patterns(composite, composite_aspects))

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

        asteroid_points = {aspect.point_a.lower(), aspect.point_b.lower()} & ASTEROID_POINTS
        personal_points = {aspect.point_a.lower(), aspect.point_b.lower()} & COMPOSITE_ASTEROID_TARGETS
        if (
            asteroid_points
            and personal_points
            and aspect.aspect == "conjunction"
            and aspect.orb <= DEFAULT_ASTEROID_ORB
        ):
            asteroid = next(iter(asteroid_points))
            if asteroid not in REPORT_ASTEROID_POINTS:
                continue
            meaning = RELATIONSHIP_ASTEROID_MEANINGS[asteroid]
            patterns.append(Pattern(
                id=f"composite_{asteroid}_personal_conjunction",
                layer="composite",
                category="asteroid_support",
                priority=68 + _bonus(aspect),
                title=_composite_title(aspect),
                evidence=[f"{_composite_evidence(aspect)}; {meaning}"],
                key=f"composite.asteroid.{asteroid}",
                confidence="medium",
            ))
            continue

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


def _relationship_ruler_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns: list[Pattern] = []
    ruler_specs = {
        "descendant_ruler": ("7th-house ruler", "familiar_pull", 62),
        "romance_ruler": ("5th-house ruler", "erotic_charge", 48),
        "intimacy_ruler": ("8th-house ruler", "trust_depth", 46),
        "ascendant_ruler": ("Ascendant ruler", "projection_mirror", 44),
    }
    charts = {"person_a": relationship.person_a, "person_b": relationship.person_b}
    names = {"person_a": relationship.person_a.name, "person_b": relationship.person_b.name}
    rulers = {owner: relationship_house_rulers(chart) for owner, chart in charts.items()}
    for aspect in relationship.synastry_aspects:
        if aspect.aspect not in {"conjunction", "opposition", "square", "trine", "sextile"}:
            continue
        for owner, activator, ruler_point, activator_point in [
            ("person_b", "person_a", aspect.point_b.lower(), aspect.point_a.lower()),
            ("person_a", "person_b", aspect.point_a.lower(), aspect.point_b.lower()),
        ]:
            for ruler_key, ruler in rulers[owner].items():
                if ruler_point != ruler or ruler_key not in ruler_specs:
                    continue
                label, category, base_priority = ruler_specs[ruler_key]
                personal_bonus = 8 if activator_point in {"sun", "moon", "venus", "mars"} and ruler_key == "descendant_ruler" else 0
                hard_bonus = 6 if aspect.aspect in {"conjunction", "opposition"} else 0
                patterns.append(Pattern(
                    id=f"relationship_ruler_{activator}_to_{owner}_{ruler_key}_{activator_point}_{ruler}_{aspect.aspect}",
                    layer="synastry",
                    category=category,
                    priority=min(92, base_priority + personal_bonus + hard_bonus + _bonus(aspect)),
                    title=f"{names[activator]}'s {_display_point(activator_point)} {_aspect_word(aspect.aspect)} {names[owner]}'s {_display_point(ruler)} ({label})",
                    evidence=[f"{_evidence(aspect, relationship)}; {_display_point(ruler)} rules {names[owner]}'s {label}"],
                    key=f"synastry.relationship_ruler.{ruler_key}",
                    confidence="high" if aspect.orb <= 3 else "medium",
                ))
        # Descendant contact is represented as a conjunction/opposition to the Ascendant axis.
        for owner, activator, angle_point, activator_point in [
            ("person_b", "person_a", aspect.point_b.lower(), aspect.point_a.lower()),
            ("person_a", "person_b", aspect.point_a.lower(), aspect.point_b.lower()),
        ]:
            if angle_point != "ascendant" or aspect.aspect not in {"conjunction", "opposition"}:
                continue
            desc = descendant_sign(charts[owner])
            contact = "Descendant" if aspect.aspect == "opposition" else "Ascendant/Descendant axis"
            patterns.append(Pattern(
                id=f"relationship_descendant_{activator}_to_{owner}_{activator_point}_{aspect.aspect}",
                layer="synastry",
                category="projection_mirror",
                priority=min(94, 78 + (8 if activator_point == "venus" else 5 if activator_point in {"sun", "moon"} else 0) + _bonus(aspect)),
                title=f"{names[activator]}'s {_display_point(activator_point)} {_aspect_word(aspect.aspect)} {names[owner]}'s {contact}",
                evidence=[f"{_evidence(aspect, relationship)}; {names[owner]}'s Descendant sign is {desc}" if desc else _evidence(aspect, relationship)],
                key="synastry.descendant_contact",
                confidence="high",
            ))
    # Concise reciprocal marker when both 7th rulers are activated in the selected aspect set.
    activated = {"person_a": False, "person_b": False}
    for pattern in patterns:
        if pattern.key == "synastry.relationship_ruler.descendant_ruler":
            if f"{relationship.person_a.name}'s 7th-house ruler" in pattern.evidence[0]:
                activated["person_a"] = True
            if f"{relationship.person_b.name}'s 7th-house ruler" in pattern.evidence[0]:
                activated["person_b"] = True
    if all(activated.values()):
        patterns.append(Pattern(
            id="relationship_ruler_reciprocal_7th",
            layer="synastry",
            category="familiar_pull",
            priority=88,
            title="Reciprocal 7th-house ruler activation",
            evidence=["Both charts have the 7th-house ruler contacted by the other person."],
            key="synastry.relationship_ruler.reciprocal_7th",
            confidence="high",
        ))
    # Reciprocal Asc/Desc ruler mirroring: both Ascendant rulers contacted cross-chart.
    asc_activated = {"person_a": False, "person_b": False}
    for pattern in patterns:
        if pattern.key == "synastry.relationship_ruler.ascendant_ruler":
            if f"{relationship.person_a.name}'s Ascendant ruler" in pattern.evidence[0]:
                asc_activated["person_a"] = True
            if f"{relationship.person_b.name}'s Ascendant ruler" in pattern.evidence[0]:
                asc_activated["person_b"] = True
    if all(asc_activated.values()):
        patterns.append(Pattern(
            id="relationship_ruler_reciprocal_asc",
            layer="synastry",
            category="projection_mirror",
            priority=82,
            title="Reciprocal Ascendant-ruler activation",
            evidence=["Both charts have the Ascendant ruler contacted by the other person — a strong identity-mirror signature."],
            key="synastry.relationship_ruler.reciprocal_asc",
            confidence="high",
        ))
    return patterns

def detect_relationship_patterns(relationship: RelationshipCalculation) -> list[Pattern]:
    patterns = detect_synastry_patterns(relationship)
    patterns.extend(detect_house_overlay_patterns(relationship))
    patterns.extend(_relationship_ruler_patterns(relationship))
    patterns.extend(_detect_stellium_gap(relationship))
    if relationship.composite is not None:
        patterns.extend(detect_composite_patterns(relationship.composite, relationship.composite_aspects))
    return sorted(patterns, key=lambda pattern: pattern.priority, reverse=True)
