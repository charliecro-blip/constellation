from __future__ import annotations

import inspect

from constellation_core.pattern_registry import get_pattern_metadata
from constellation_core.patterns import Pattern
from constellation_core.report import _central_patterns
from constellation_core.weighting import convergence_multiplier_for, weight_patterns


def _pattern(
    key: str,
    *,
    layer: str = "synastry",
    category: str = "desire",
    priority: int = 50,
    title: str | None = None,
    evidence: list[str] | None = None,
    pattern_id: str | None = None,
) -> Pattern:
    return Pattern(
        id=pattern_id or key.replace(".", "_"),
        layer=layer,
        category=category,
        priority=priority,
        title=title or key,
        evidence=evidence or [],
        key=key,
        confidence="medium",
    )


def test_same_category_echo_increases_priority():
    alone = _pattern(
        "synastry.sun_moon",
        category="recognition",
        priority=50,
        title="A's Sun conjunct B's Moon",
    )
    echo = _pattern(
        "synastry.moon_moon",
        category="emotional_translation",
        priority=50,
        title="A's Moon conjunct B's Moon",
    )

    alone_weighted = weight_patterns([alone])[0]
    echoed_weighted = next(pattern for pattern in weight_patterns([alone, echo]) if pattern.id == alone.id)

    assert convergence_multiplier_for(alone, [alone, echo]) > 1.0
    assert echoed_weighted.priority > alone_weighted.priority


def test_convergence_multiplier_caps_at_1_60():
    target = _pattern(
        "synastry.venus_mars",
        priority=50,
        title="A's Venus conjunct B's Mars",
    )
    reciprocal = _pattern(
        "synastry.venus_mars",
        priority=50,
        title="B's Venus square A's Mars",
        pattern_id="synastry_venus_mars_reciprocal",
    )
    composite = _pattern(
        "composite.venus_mars",
        layer="composite",
        category="desire",
        priority=50,
        title="Composite Venus conjunct Mars",
    )
    natal = _pattern(
        "synastry.venus_mars",
        layer="natal",
        category="desire",
        priority=50,
        title="Natal Venus conjunct Mars",
        pattern_id="natal_venus_mars",
    )

    assert convergence_multiplier_for(target, [target, reciprocal, composite, natal]) == 1.60


def test_double_whammy_venus_mars_receives_boost():
    first = _pattern(
        "synastry.venus_mars",
        priority=50,
        title="A's Venus conjunct B's Mars",
    )
    reciprocal = _pattern(
        "synastry.venus_mars",
        priority=50,
        title="B's Venus square A's Mars",
        pattern_id="synastry_venus_mars_reciprocal",
    )

    assert convergence_multiplier_for(first, [first]) == 1.0
    assert convergence_multiplier_for(first, [first, reciprocal]) > 1.0


def test_synastry_moon_saturn_plus_composite_moon_saturn_receives_boost():
    synastry = _pattern(
        "synastry.moon_saturn",
        category="emotional_structure",
        priority=50,
        title="A's Moon opposite B's Saturn",
    )
    composite = _pattern(
        "composite.moon_saturn",
        layer="composite",
        category="emotional_structure",
        priority=50,
        title="Composite Moon square Saturn",
    )

    assert convergence_multiplier_for(synastry, [synastry, composite]) > 1.0
    weighted = next(pattern for pattern in weight_patterns([synastry, composite]) if pattern.id == synastry.id)
    solo = weight_patterns([synastry])[0]
    assert weighted.priority > solo.priority


def test_composite_concentration_can_echo_related_synastry_theme():
    synastry = _pattern(
        "synastry.venus_pluto",
        category="attraction_intensity",
        priority=50,
        title="A's Venus square B's Pluto",
    )
    composite = _pattern(
        "composite.stellium.scorpio",
        layer="composite",
        category="composite_concentration",
        priority=50,
        title="Composite Scorpio concentration",
        evidence=["Sun, Venus, and Pluto in Scorpio"],
    )

    assert convergence_multiplier_for(synastry, [synastry, composite]) > 1.0
    weighted = next(pattern for pattern in weight_patterns([synastry, composite]) if pattern.id == synastry.id)
    solo = weight_patterns([synastry])[0]
    assert weighted.priority > solo.priority


def test_isolated_mercury_mars_does_not_become_report_leading():
    mercury_mars = _pattern(
        "synastry.mercury_mars",
        category="communication",
        priority=95,
        title="A's Mercury square B's Mars",
    )

    assert _central_patterns(weight_patterns([mercury_mars])) == []


def test_mercury_mars_with_multiple_echoes_can_rise_but_remains_non_lead_eligible_by_default():
    mercury_mars = _pattern(
        "synastry.mercury_mars",
        category="communication",
        priority=50,
        title="A's Mercury square B's Mars",
    )
    reciprocal = _pattern(
        "synastry.mercury_mars",
        category="communication",
        priority=50,
        title="B's Mercury opposite A's Mars",
        pattern_id="synastry_mercury_mars_reciprocal",
    )
    mercury_mercury = _pattern(
        "synastry.mercury_mercury",
        category="communication",
        priority=50,
        title="A's Mercury trine B's Mercury",
    )

    solo = weight_patterns([mercury_mars])[0]
    converged = next(
        pattern
        for pattern in weight_patterns([mercury_mars, reciprocal, mercury_mercury])
        if pattern.id == mercury_mars.id
    )

    assert converged.priority > solo.priority
    assert get_pattern_metadata("synastry.mercury_mars").lead_eligible is False
    assert mercury_mars not in _central_patterns(weight_patterns([mercury_mars, reciprocal, mercury_mercury]))


def test_neutral_no_echo_pattern_keeps_multiplier_1_0():
    neutral = _pattern(
        "unknown.texture",
        category="supporting_texture",
        priority=50,
        title="Neutral supporting texture",
    )

    assert convergence_multiplier_for(neutral, [neutral]) == 1.0


def test_weighting_language_does_not_introduce_compatibility_score_or_meant_to_be_claims():
    import constellation_core.scoring_weights as scoring_weights
    import constellation_core.weighting as weighting

    source = inspect.getsource(weighting).lower() + inspect.getsource(scoring_weights).lower()

    assert "compatibility score" not in source
    assert "meant to be" not in source


def test_12th_house_overlay_receives_steeper_penalty_than_romantic_houses():
    """12th house overlay must score lower than 7th/5th/8th overlays — not in the romantic tier."""
    house_12 = _pattern("overlay.house_12", layer="house_overlay", category="hidden_field", priority=58)
    house_7 = _pattern("overlay.house_7", layer="house_overlay", category="partnership", priority=64)
    house_5 = _pattern("overlay.house_5", layer="house_overlay", category="romance_creativity", priority=56)
    house_8 = _pattern("overlay.house_8", layer="house_overlay", category="intimacy_depth", priority=62)

    patterns = [house_12, house_7, house_5, house_8]
    weighted = {p.key: p for p in weight_patterns(patterns)}

    # 12th must score lower than all three romantic overlays.
    assert weighted["overlay.house_12"].priority < weighted["overlay.house_7"].priority
    assert weighted["overlay.house_12"].priority < weighted["overlay.house_5"].priority
    assert weighted["overlay.house_12"].priority < weighted["overlay.house_8"].priority


def test_mars_mars_water_earth_opposition_receives_extra_penalty():
    """Mars opposite Mars in water-earth sign pairs should score lower than fire-air pairs."""
    from constellation_core.weighting import WATER_EARTH_OPPOSITION_PAIRS

    # Confirm the constant covers all three pairs.
    assert frozenset({"pisces", "virgo"}) in WATER_EARTH_OPPOSITION_PAIRS
    assert frozenset({"scorpio", "taurus"}) in WATER_EARTH_OPPOSITION_PAIRS
    assert frozenset({"cancer", "capricorn"}) in WATER_EARTH_OPPOSITION_PAIRS

    water_earth = _pattern(
        "synastry.mars_mars_opposition",
        category="volatility",
        priority=70,
        evidence=["A's Mars opposite B's Mars; orb 1.0; Mars signs: scorpio/taurus"],
    )
    fire_air = _pattern(
        "synastry.mars_mars_opposition",
        category="volatility",
        priority=70,
        pattern_id="mars_mars_fire_air",
        evidence=["A's Mars opposite B's Mars; orb 1.0; Mars signs: aries/libra"],
    )

    weighted_we = weight_patterns([water_earth])[0]
    weighted_fa = weight_patterns([fire_air])[0]
    assert weighted_we.priority < weighted_fa.priority


def test_sun_sun_conjunction_scores_below_sun_moon():
    """Sun conjunct Sun (friend signal) must score below Sun-Moon for romantic priority."""
    sun_sun = _pattern("synastry.sun_sun_conjunction", category="recognition", priority=55)
    sun_moon = _pattern("synastry.sun_moon", category="recognition", priority=84)

    weighted = {p.key: p for p in weight_patterns([sun_sun, sun_moon])}
    assert weighted["synastry.sun_sun_conjunction"].priority < weighted["synastry.sun_moon"].priority


def test_sun_sun_conjunction_below_synthesis_packet_threshold():
    """Sun conjunct Sun should not reach the synthesis packet inclusion threshold (70)."""
    sun_sun = _pattern("synastry.sun_sun_conjunction", category="recognition", priority=55,
                       evidence=["A's Sun conjunct B's Sun; orb 0.5"])
    weighted = weight_patterns([sun_sun])[0]
    assert weighted.priority < 70
