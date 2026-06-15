"""Relationship-house rulership helpers.

Constellation uses traditional sign rulers for this lightweight interpretive
layer: Mars rules Aries/Scorpio, Venus Taurus/Libra, Mercury Gemini/Virgo,
Moon Cancer, Sun Leo, Jupiter Sagittarius/Pisces, and Saturn
Capricorn/Aquarius. Modern ruler debates, dignity, sect, and timing doctrines
are intentionally out of scope here.
"""

from __future__ import annotations

from .schemas import Chart
from .zodiac import SIGNS, to_zodiac_position

TRADITIONAL_SIGN_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

RELATIONSHIP_HOUSES = {1: "ascendant_ruler", 4: "roots_ruler", 5: "romance_ruler", 7: "descendant_ruler", 8: "intimacy_ruler", 10: "public_ruler"}
NATURAL_SIGNIFICATORS = {"venus": "natural_relationship", "mars": "desire_action", "moon": "attachment_need"}


def sign_ruler(sign: str) -> str | None:
    return TRADITIONAL_SIGN_RULERS.get(sign.lower())


def house_cusp_sign(chart: Chart, house: int) -> str | None:
    if chart.houses and house in chart.houses.cusps:
        return to_zodiac_position(chart.houses.cusps[house]).sign
    asc = chart.angles.get("ascendant")
    if asc is None:
        return None
    return SIGNS[(asc.sign_index + house - 1) % 12]


def descendant_sign(chart: Chart) -> str | None:
    return house_cusp_sign(chart, 7)


def ruler_placement(chart: Chart, ruler: str | None) -> dict[str, object] | None:
    if ruler is None:
        return None
    placement = chart.placements.get(ruler)
    if placement is None:
        return {"planet": ruler.title()}
    return {"planet": ruler.title(), "sign": placement.sign, "house": placement.house, "degree": round(placement.degree, 2)}


def house_ruler_summary(chart: Chart, house: int) -> dict[str, object] | None:
    sign = house_cusp_sign(chart, house)
    ruler = sign_ruler(sign) if sign else None
    if sign is None or ruler is None:
        return None
    return {"house": house, "sign": sign, "ruler": ruler_placement(chart, ruler)}


def relationship_significator_summary(chart: Chart) -> dict[str, object]:
    asc = house_cusp_sign(chart, 1)
    desc = house_cusp_sign(chart, 7)
    asc_ruler = sign_ruler(asc) if asc else None
    desc_ruler = sign_ruler(desc) if desc else None
    summary: dict[str, object] = {
        "relationship_axis": {
            "ascendant": asc,
            "ascendant_ruler": ruler_placement(chart, asc_ruler),
            "descendant": desc,
            "descendant_ruler": ruler_placement(chart, desc_ruler),
        },
        "romance_significator": house_ruler_summary(chart, 5),
        "intimacy_significator": house_ruler_summary(chart, 8),
        "roots_significator": house_ruler_summary(chart, 4),
        "public_significator": house_ruler_summary(chart, 10),
        "natural_significators": {role: ruler_placement(chart, body) for body, role in NATURAL_SIGNIFICATORS.items()},
    }
    return summary


def relationship_house_rulers(chart: Chart) -> dict[str, str]:
    rulers: dict[str, str] = {}
    for house, label in RELATIONSHIP_HOUSES.items():
        if sign := house_cusp_sign(chart, house):
            if ruler := sign_ruler(sign):
                rulers[label] = ruler
    return rulers
