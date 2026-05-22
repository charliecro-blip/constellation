"""Deterministic interpretation text blocks for early reports.

These are intentionally compact. They translate pattern keys into the
somatic-relational language Constellation will use before an LLM layer is added.
"""

from __future__ import annotations

from .patterns import Pattern


INTERPRETATION_BLOCKS: dict[str, str] = {
    "synastry.venus_ascendant": (
        "This is a direct attraction and recognition contact. One person's presence, body, "
        "style, or way of entering the room may reach the other person's Venus field quickly. "
        "The contact should be read as stimulus and receptivity, not as a verdict about safety "
        "or longevity."
    ),
    "synastry.venus_mars": (
        "This contact links affection and desire. It can create movement, flirtation, pursuit, "
        "heat, and creative charge. The repair question is whether the desire channel can stay "
        "clear, mutual, and well-paced."
    ),
    "synastry.mercury_mars": (
        "This contact makes the communication field active. Words may carry heat, speed, humor, "
        "argument, or provocation. The same pattern can sharpen clarity or escalate irritation, "
        "depending on pacing and repair."
    ),
    "synastry.moon_saturn": (
        "This contact brings emotional life into contact with structure, time, responsibility, "
        "or restraint. Saturn may offer steadiness and commitment, but it can also feel cold, "
        "heavy, or inhibiting. The question is whether Saturn functions as container or constraint."
    ),
    "synastry.moon_pluto": (
        "This contact can make the emotional field feel deep, exposing, magnetic, or difficult "
        "to keep casual. Intensity is not the same as safety; the bond needs honesty, pacing, "
        "and repair capacity."
    ),
    "composite.mars_pluto": (
        "The relationship field carries a high-intensity engine. This can show desire, force, "
        "endurance, transformation, and conflict potential. Without repair skills, intensity can "
        "become escalation. With maturity, it can become shared power and depth."
    ),
    "composite.moon_saturn": (
        "The relationship's emotional body meets Saturn: time, structure, duty, restraint, and "
        "the need for reliable repair. This can mature the bond, but it can also make softness "
        "feel delayed or burdened."
    ),
    "composite.moon_uranus": (
        "The relationship's emotional body is wired for change, electricity, and disruption. "
        "There may be aliveness and freedom, but also uneven rhythm. The bond needs ways to "
        "make space without turning distance into abandonment."
    ),
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

    if key.startswith("composite.moon."):
        sign = key.split(".")[-1]
        return COMPOSITE_MOON_BLOCKS.get(sign, "Composite Moon describes the emotional body of the relationship.")

    if key.startswith("composite.sun."):
        sign = key.split(".")[-1]
        return COMPOSITE_SUN_BLOCKS.get(sign, "Composite Sun describes the identity and life-force of the relationship.")

    return "This pattern has been detected, but its interpretive block has not been written yet."
