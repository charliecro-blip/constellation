"""Deterministic interpretation text blocks for early reports.

These are intentionally compact. They translate pattern keys into the
somatic-relational language Constellation will use before an LLM layer is added.
"""

from __future__ import annotations

from .patterns import Pattern


INTERPRETATION_BLOCKS: dict[str, str] = {
    "synastry.venus_ascendant": (
        "Strong attraction through presence, style, and body-language. Noticeable pull, but not necessarily smooth."
    ),
    "synastry.angle_ascendant_sun": (
        "The Sun person lands directly on the Ascendant person's embodied field. Recognition is immediate; the Sun person is hard for the Ascendant person to keep abstract."
    ),
    "synastry.angle_ascendant_moon": (
        "The Moon person lands on the Ascendant person's body and instinctive field. Familiarity, reactivity, and emotional visibility arrive quickly."
    ),
    "synastry.angle_ascendant_mars": (
        "Immediate charge through body, will, and movement. Energizing, provocative, and best with clean pacing."
    ),
    "synastry.angle_ascendant_saturn": (
        "Saturn meets the Ascendant person's body and self-presentation directly. Seriousness is palpable; steadiness can become pressure if the bond tightens too quickly."
    ),
    "synastry.angle_ascendant_north_node": (
        "The nodal axis hits the Ascendant field. The meeting can feel consequential, directional, or difficult to treat as casual."
    ),
    "synastry.angle_ascendant_south_node": (
        "The nodal axis hits the Ascendant field. Familiarity can arrive fast, with old-pattern gravity that needs present-tense choice."
    ),
    "synastry.angle_midheaven_sun": (
        "The Sun person touches the Midheaven person's direction, visibility, and public self. The bond can affect ambition, reputation, or life trajectory."
    ),
    "synastry.angle_midheaven_moon": (
        "The Moon person touches the Midheaven person's visible life direction. Private feeling and public path are not easily separated here."
    ),
    "synastry.angle_midheaven_venus": (
        "Venus touches the Midheaven field: admiration, aesthetics, social visibility, and public value can become part of the attraction."
    ),
    "synastry.angle_midheaven_saturn": (
        "Saturn touches the Midheaven field. The bond may carry consequence, duty, mentorship, pressure, or long-range shaping."
    ),
    "synastry.angle_midheaven_north_node": (
        "The nodal axis touches the Midheaven field. The relationship can feel tied to vocation, visibility, or a future-facing threshold."
    ),
    "synastry.angle_midheaven_south_node": (
        "The nodal axis touches the Midheaven field. Old roles, reputation, or unfinished public-life material may be activated."
    ),
    "synastry.venus_mars": (
        "Affection and desire catch quickly. Flirtation, pursuit, and creative heat are easy; mutual pacing keeps it clean."
    ),
    "synastry.sun_moon": (
        "A primary solar-lunar recognition signature. One person's direction meets the other's emotional rhythm; consequential, familiar, and not automatically easy."
    ),
    "synastry.moon_moon": (
        "Two emotional rhythms recognize or challenge each other directly. Safety, closeness, rest, and regulation become central terrain."
    ),
    "synastry.moon_venus": (
        "Tenderness has somewhere to land. Sweetness, comfort, and affection are available; avoid turning care into appeasement."
    ),
    "synastry.moon_mars": (
        "Feelings heat up quickly. Aliveness, desire, protection, and reactivity travel together; pacing matters."
    ),
    "synastry.mercury_mars": (
        "Words carry heat, speed, humor, and provocation. It can sharpen clarity or escalate irritation."
    ),
    "synastry.mercury_mercury": (
        "The minds meet directly. Similarity can ease conversation; difference can stimulate or polarize. Translation matters more than sameness."
    ),
    "synastry.moon_saturn": (
        "Emotional life meets time, restraint, and responsibility. Saturn can steady the bond or make softness feel judged."
    ),
    "synastry.moon_pluto": (
        "The emotional field becomes deep, exposing, magnetic, and hard to keep casual. Intensity needs honesty and repair capacity."
    ),
    "synastry.venus_pluto": (
        "Attraction intensifies fast. Pleasure, longing, jealousy, and vulnerability can press into deeper material."
    ),
    "synastry.mars_pluto": (
        "High-force chemistry. Desire, anger, will, pressure, and power amplify quickly; force needs clean channels."
    ),
    "synastry.venus_saturn": (
        "Affection meets time, seriousness, and restraint. Loyalty is possible; so is the feeling of love being evaluated."
    ),
    "synastry.mars_saturn": (
        "Action meets resistance, discipline, duty, or frustration. Stamina is possible, but so is the feeling of pushing against a wall."
    ),
    "composite.venus_mars": (
        "The relationship field carries a built-in affection/desire current. This can create "
        "romantic heat, creativity, movement, and attraction, but the channel still needs mutual "
        "pacing and consent."
    ),
    "composite.mars_pluto": (
        "The relationship field carries a high-intensity engine. This can show desire, force, "
        "endurance, transformation, and conflict potential. Without repair skills, intensity can "
        "become escalation. With maturity, it can become shared power and depth."
    ),
    "composite.venus_saturn": (
        "The relationship field asks affection to meet time, structure, responsibility, or "
        "restraint. This can create devotion and durability, but the bond needs warmth so that "
        "commitment does not become only duty."
    ),
    "composite.sun_saturn": (
        "The relationship identity meets Saturn. The bond may ask for maturity, endurance, "
        "accountability, or long-term form. This can stabilize the relationship, but it can also "
        "make the field feel heavy if joy and spontaneity are not protected."
    ),
    "composite.moon_saturn": (
        "The relationship's emotional body meets Saturn: time, structure, duty, restraint, and "
        "the need for reliable repair. This can mature the bond, but it can also make softness "
        "feel delayed or burdened."
    ),
    "composite.moon_uranus": (
        "The relationship's emotional rhythm is electric, changeable, and hard to settle. Space is necessary; inconsistency can become the wound."
    ),
}


OVERLAY_BLOCKS: dict[str, str] = {
    "1": "Body and identity are emphasized. The planet person may feel immediately present, visible, or hard to keep abstract.",
    "4": "Private roots are emphasized: home, family memory, belonging, childhood patterning, and emotional foundation.",
    "5": "Romance, play, creativity, pleasure, and the feeling of being chosen are emphasized.",
    "6": "Daily life is emphasized: habits, work, health, usefulness, repair routines, and ordinary maintenance.",
    "7": "The partner mirror is emphasized. The planet person may appear as counterpart, projection surface, or relationship threshold.",
    "8": "Intimacy, trust, shared resources, psychological exposure, and erotic charge are emphasized.",
    "10": "Public life, vocation, visibility, ambition, reputation, and life direction are emphasized.",
    "12": "The hidden field is emphasized: dreams, projection, retreat, longing, ambiguity, and what is felt before it is named.",
}


COMPOSITE_MOON_BLOCKS: dict[str, str] = {
    "aries": "The relationship's emotional body runs hot and fast. Feelings want movement, honesty, and action. The repair task is cooling down without making either person feel abandoned.",
    "taurus": "The relationship's emotional body seeks steadiness, touch, comfort, repetition, and material ease. The repair task is not letting comfort become stuckness.",
    "gemini": "The relationship's emotional body needs words, curiosity, movement, and mental contact. The repair task is keeping conversation connected to feeling.",
    "cancer": "The relationship's emotional body seeks care, memory, belonging, and protection. The repair task is making safety real without collapsing into defensiveness or over-protection.",
    "leo": "The relationship's emotional body needs warmth, play, pride, and visible affection. The repair task is making room for both people to feel chosen and seen.",
    "virgo": "The relationship's emotional body regulates through usefulness, rhythm, repair, and ordinary care. The repair task is keeping practical improvement from becoming critique.",
    "libra": "The relationship's emotional body seeks reciprocity, fairness, grace, and relational balance. The repair task is naming conflict before harmony becomes avoidance.",
    "scorpio": "The relationship's emotional body is deep, private, loyal, and intense. The repair task is building enough trust that depth does not become control or suspicion.",
    "sagittarius": "The relationship's emotional body needs horizon, story, adventure, and meaning. The repair task is tending the fire between peaks of inspiration.",
    "capricorn": "The relationship's emotional body seeks structure, reliability, maturity, and proof over time. The repair task is making room for softness inside responsibility.",
    "aquarius": "The relationship's emotional body needs space, perspective, friendship, and authenticity. The repair task is keeping distance from becoming disconnection.",
    "pisces": "The relationship's emotional body is porous, imaginative, tender, and absorbing. The repair task is keeping compassion clear enough to support boundaries.",
}


COMPOSITE_SUN_BLOCKS: dict[str, str] = {
    "aries": "The relationship identity wants movement, initiation, courage, and directness.",
    "taurus": "The relationship identity wants steadiness, embodiment, value, and something tangible to build.",
    "gemini": "The relationship identity wants conversation, movement, ideas, and multiplicity.",
    "cancer": "The relationship identity wants care, memory, family, roots, and belonging.",
    "leo": "The relationship identity wants warmth, radiance, play, loyalty, and creative heart-expression.",
    "virgo": "The relationship identity wants usefulness, craft, repair, service, and intelligent daily life.",
    "libra": "The relationship identity wants reciprocity, beauty, fairness, dialogue, and partnership.",
    "scorpio": "The relationship identity wants depth, trust, honesty, transformation, and under-surface truth.",
    "sagittarius": "The relationship identity wants meaning, adventure, candor, horizon, and growth.",
    "capricorn": "The relationship identity wants structure, endurance, accountability, and real-world form.",
    "aquarius": "The relationship identity wants friendship, freedom, authenticity, systems, and future-orientation.",
    "pisces": "The relationship identity wants imagination, compassion, spiritual atmosphere, and permeability.",
}


def interpret_pattern(pattern: Pattern) -> str:
    """Return a compact interpretation for a detected pattern."""
    key = pattern.key
    if key in INTERPRETATION_BLOCKS:
        return INTERPRETATION_BLOCKS[key]

    if key.startswith("overlay.house_"):
        house = key.split("_")[-1]
        return OVERLAY_BLOCKS.get(house, "This shows where one person appears inside the other person's life terrain.")

    if key.startswith("composite.moon."):
        sign = key.split(".")[-1]
        return COMPOSITE_MOON_BLOCKS.get(sign, "Composite Moon describes the emotional body of the relationship.")

    if key.startswith("composite.sun."):
        sign = key.split(".")[-1]
        return COMPOSITE_SUN_BLOCKS.get(sign, "Composite Sun describes the identity and life-force of the relationship.")

    return "This pattern has been detected, but its interpretive block has not been written yet."
