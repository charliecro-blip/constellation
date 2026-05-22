"""Zodiac utilities."""

from __future__ import annotations

from dataclasses import dataclass

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


@dataclass(frozen=True)
class ZodiacPosition:
    """A normalized zodiac position."""

    longitude: float
    sign: str
    sign_index: int
    degree: float


def normalize_longitude(longitude: float) -> float:
    """Normalize any longitude to the 0 <= longitude < 360 range."""
    return longitude % 360.0


def to_zodiac_position(longitude: float) -> ZodiacPosition:
    """Convert ecliptic longitude to sign + degree position."""
    normalized = normalize_longitude(longitude)
    sign_index = int(normalized // 30)
    degree = normalized - (sign_index * 30)
    return ZodiacPosition(
        longitude=round(normalized, 6),
        sign=SIGNS[sign_index],
        sign_index=sign_index,
        degree=round(degree, 6),
    )


def opposite_longitude(longitude: float) -> float:
    """Return the zodiacal opposition point."""
    return normalize_longitude(longitude + 180.0)


def shortest_arc(a: float, b: float) -> float:
    """Return the shortest angular distance between two longitudes."""
    diff = abs(normalize_longitude(a) - normalize_longitude(b))
    return min(diff, 360.0 - diff)


def midpoint_longitude(a: float, b: float) -> float:
    """Return the zodiacal midpoint along the shortest arc."""
    a_norm = normalize_longitude(a)
    b_norm = normalize_longitude(b)
    diff = (b_norm - a_norm) % 360.0
    if diff > 180.0:
        diff -= 360.0
    return normalize_longitude(a_norm + diff / 2.0)
