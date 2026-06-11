import pytest

from constellation_core.context import RelationshipContext
from constellation_core.patterns import Pattern, detect_relationship_patterns
from constellation_core.report import generate_relationship_report
from constellation_core.schemas import Aspect, BirthData, Chart, RelationshipCalculation
from constellation_core.weighting import CONVERGENCE_MULTIPLIERS, convergence_multiplier, weight_patterns


def _pattern(
    key: str,
    category: str,
    *,
    layer: str = "synastry",
    priority: int = 60,
    title: str | None = None,
) -> Pattern:
    return Pattern(
        id=key.replace(".", "_"),
        layer=layer,
        category=category,
        priority=priority,
        title=title or key,
        evidence=[f"{title or key}; orb 3.00"],
        key=key,
    )


def _birth(name: str) -> BirthData:
    return BirthData(
        name=name,
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )


def _chart(name: str) -> Chart:
    return Chart(
        name=name,
        birth=_birth(name),
        julian_day_ut=None,
        house_system="whole_sign",
        placements={},
    )


def test_no_echo_keeps_neutral_convergence_multiplier():
    isolated = _pattern("synastry.mercury_mars", "communication")

    assert convergence_multiplier(isolated, [isolated]) == 1.0


def test_same_category_patterns_receive_convergence_boost():
    primary = _pattern("custom.structure.one", "emotional_structure")
    echo = _pattern("custom.structure.two", "emotional_structure")

    weighted = weight_patterns([primary, echo])

    assert weighted[0].priority == round(primary.priority * CONVERGENCE_MULTIPLIERS["same_category_once"])
    assert convergence_multiplier(primary, [primary, echo]) == CONVERGENCE_MULTIPLIERS["same_category_once"]


def test_convergence_multiplier_caps_at_sixty_percent():
    primary = _pattern(
        "synastry.venus_mars",
        "desire",
        title="Alex's Venus conjunct Blake's Mars",
    )
    patterns = [
        primary,
        _pattern("synastry.venus_mars", "desire", title="Blake's Venus square Alex's Mars"),
        _pattern("composite.venus_mars", "desire", layer="composite"),
        _pattern("natal.venus_mars", "desire", layer="natal"),
    ]

    assert convergence_multiplier(primary, patterns) == CONVERGENCE_MULTIPLIERS["cap"]


def test_double_whammy_venus_mars_receives_stronger_boost():
    primary = _pattern(
        "synastry.venus_mars",
        "desire",
        title="Alex's Venus conjunct Blake's Mars",
    )
    reciprocal = _pattern(
        "synastry.venus_mars",
        "desire",
        title="Blake's Venus square Alex's Mars",
    )

    assert convergence_multiplier(primary, [primary, reciprocal]) == pytest.approx(1.12 * 1.30)


def test_synastry_moon_saturn_plus_composite_moon_saturn_receives_boost():
    synastry = _pattern("synastry.moon_saturn", "emotional_structure")
    composite = _pattern("composite.moon_saturn", "emotional_structure", layer="composite")

    assert convergence_multiplier(synastry, [synastry, composite]) == pytest.approx(1.4)


def test_composite_echo_boosts_related_synastry_pattern():
    synastry = _pattern("synastry.venus_pluto", "attraction_intensity")
    composite_echo = _pattern("composite.stellium.scorpio", "composite_concentration", layer="composite")

    assert convergence_multiplier(synastry, [synastry, composite_echo]) == pytest.approx(1.4)


def test_isolated_mercury_mars_does_not_become_report_leading():
    relationship = RelationshipCalculation(
        person_a=_chart("Alex"),
        person_b=_chart("Blake"),
        synastry_aspects=[Aspect(point_a="mars", point_b="mercury", aspect="square", exact_angle=90, orb=0.1)],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    overview = generate_relationship_report(relationship, context=context).to_markdown().split("## Overview")[1].split("## Calculated chart check")[0]

    assert "Mars square Blake's Mercury" not in overview.split(".", 1)[0]


def test_mercury_mars_with_echoes_can_rise_but_remains_non_lead_by_default():
    relationship = RelationshipCalculation(
        person_a=_chart("Alex"),
        person_b=_chart("Blake"),
        synastry_aspects=[
            Aspect(point_a="mars", point_b="mercury", aspect="square", exact_angle=90, orb=0.1),
            Aspect(point_a="mercury", point_b="mercury", aspect="opposition", exact_angle=180, orb=0.2),
            Aspect(point_a="mercury", point_b="mars", aspect="trine", exact_angle=120, orb=0.3),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )
    context = RelationshipContext(relationship_type="romantic", status="current")

    weighted = weight_patterns(detect_relationship_patterns(relationship), context)
    mercury_mars = next(pattern for pattern in weighted if pattern.key == "synastry.mercury_mars")
    overview = generate_relationship_report(relationship, context=context).to_markdown().split("## Overview")[1].split("## Calculated chart check")[0]

    assert mercury_mars.priority >= 84
    assert "Mars square Blake's Mercury" not in overview.split(".", 1)[0]


def test_convergence_report_has_no_score_or_meant_to_be_language():
    relationship = RelationshipCalculation(
        person_a=_chart("Alex"),
        person_b=_chart("Blake"),
        synastry_aspects=[
            Aspect(point_a="venus", point_b="mars", aspect="conjunction", exact_angle=0, orb=0.3),
            Aspect(point_a="mars", point_b="venus", aspect="square", exact_angle=90, orb=0.4),
        ],
        house_overlays=[],
        composite=None,
        composite_aspects=[],
    )

    markdown = generate_relationship_report(relationship).to_markdown().lower()

    assert "compatibility score" not in markdown
    assert "meant to be" not in markdown
