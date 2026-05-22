"""Natal relational profile helpers.

These helpers summarize each person's baseline relationship style before
synastry and composite layers are interpreted.
"""

from __future__ import annotations

from pydantic import BaseModel

from .schemas import Chart, Placement


class NatalProfile(BaseModel):
    name: str
    headline: str
    core_points: list[str]
    confidence_notes: list[str]


SIGN_ELEMENTS: dict[str, str] = {
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

SIGN_MODES: dict[str, str] = {
    "Aries": "cardinal",
    "Cancer": "cardinal",
    "Libra": "cardinal",
    "Capricorn": "cardinal",
    "Taurus": "fixed",
    "Leo": "fixed",
    "Scorpio": "fixed",
    "Aquarius": "fixed",
    "Gemini": "mutable",
    "Virgo": "mutable",
    "Sagittarius": "mutable",
    "Pisces": "mutable",
}


def _placement_line(label: str, placement: Placement | None) -> str | None:
    if placement is None:
        return None
    element = SIGN_ELEMENTS.get(placement.sign, "unknown element")
    mode = SIGN_MODES.get(placement.sign, "unknown mode")
    house = f", house {placement.house}" if placement.house is not None else ""
    return f"{label}: {placement.degree:.2f} {placement.sign}{house} ({mode} {element})"


def _relationship_note(body: str, placement: Placement | None) -> str | None:
    if placement is None:
        return None
    sign = placement.sign
    if body == "moon":
        return f"Moon in {sign} describes emotional regulation, safety needs, memory, and the body-level way this person seeks closeness or protection."
    if body == "venus":
        return f"Venus in {sign} describes affection, attraction, aesthetics, receptivity, pleasure, and what feels beautiful or worth choosing."
    if body == "mars":
        return f"Mars in {sign} describes desire, pursuit, heat, assertion, conflict style, and how action moves through the relational field."
    if body == "mercury":
        return f"Mercury in {sign} describes communication rhythm, translation style, curiosity, nervous-system language, and how contact becomes verbal."
    return None


def _headline(chart: Chart) -> str:
    moon = chart.placements.get("moon")
    venus = chart.placements.get("venus")
    mars = chart.placements.get("mars")
    asc = chart.angles.get("ascendant")

    parts: list[str] = []
    if moon:
        parts.append(f"Moon in {moon.sign}")
    if venus:
        parts.append(f"Venus in {venus.sign}")
    if mars:
        parts.append(f"Mars in {mars.sign}")
    if asc:
        parts.append(f"{asc.sign} rising")

    if not parts:
        return "Relational profile needs more chart data."
    return ", ".join(parts)


def build_natal_profile(chart: Chart) -> NatalProfile:
    core_points: list[str] = []
    confidence_notes: list[str] = []

    for label, key in [
        ("Moon", "moon"),
        ("Venus", "venus"),
        ("Mars", "mars"),
        ("Mercury", "mercury"),
        ("Saturn", "saturn"),
    ]:
        line = _placement_line(label, chart.placements.get(key))
        if line:
            core_points.append(line)
        note = _relationship_note(key, chart.placements.get(key))
        if note:
            core_points.append(note)

    asc = chart.angles.get("ascendant")
    mc = chart.angles.get("midheaven")
    if asc:
        core_points.append(f"Ascendant: {asc.degree:.2f} {asc.sign}. This describes embodiment, first-contact style, and how others initially meet this person.")
    if mc:
        core_points.append(f"Midheaven: {mc.degree:.2f} {mc.sign}. This can matter when a relationship activates vocation, visibility, public identity, or direction.")

    if not chart.birth.time_known or not chart.birth.time:
        confidence_notes.append("Birth time is unknown; houses, angles, Ascendant, Midheaven, and house-based relational claims should be minimized.")
    if chart.warnings:
        confidence_notes.extend(chart.warnings)
    if not confidence_notes:
        confidence_notes.append("Birth time is marked known; angular and house material can be used, pending validation against trusted chart software.")

    return NatalProfile(
        name=chart.name,
        headline=_headline(chart),
        core_points=core_points,
        confidence_notes=confidence_notes,
    )


def natal_profile_markdown(chart: Chart) -> str:
    profile = build_natal_profile(chart)
    lines = [f"**{profile.headline}**", ""]
    lines.extend(f"- {point}" for point in profile.core_points)
    lines.append("")
    lines.append("Confidence:")
    lines.extend(f"- {note}" for note in profile.confidence_notes)
    return "\n".join(lines)
