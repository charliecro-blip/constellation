"""Natal chart calculation for Constellation."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import swisseph as swe

from .schemas import Angle, BirthData, Chart, HouseCusps, Placement
from .zodiac import opposite_longitude, to_zodiac_position

PLANET_IDS: dict[str, int] = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
    "north_node": swe.TRUE_NODE,
}

HOUSE_SYSTEMS: dict[str, bytes] = {
    "placidus": b"P",
    "koch": b"K",
    "porphyry": b"O",
    "regiomontanus": b"R",
    "equal": b"E",
    "whole_sign": b"W",
}


def parse_local_datetime(birth: BirthData) -> datetime | None:
    """Parse local birth datetime with timezone attached."""
    if not birth.time_known or not birth.time:
        return None

    date_part = birth.date
    time_part = birth.time
    if len(time_part.split(":")) == 2:
        time_part = f"{time_part}:00"

    naive = datetime.fromisoformat(f"{date_part}T{time_part}")
    return naive.replace(tzinfo=ZoneInfo(birth.timezone))


def julian_day_ut_from_birth(birth: BirthData) -> float | None:
    """Convert local birth data to Julian Day UT."""
    local_dt = parse_local_datetime(birth)
    if local_dt is None:
        return None

    utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
    hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600 + utc_dt.microsecond / 3_600_000_000
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour)


def calculate_planet_longitudes(julian_day_ut: float) -> dict[str, float]:
    """Calculate tropical ecliptic longitudes for required planets."""
    longitudes: dict[str, float] = {}
    for name, planet_id in PLANET_IDS.items():
        result, _flags = swe.calc_ut(julian_day_ut, planet_id, swe.FLG_SWIEPH)
        longitudes[name] = result[0] % 360.0

    longitudes["south_node"] = opposite_longitude(longitudes["north_node"])
    return longitudes


def calculate_houses(
    julian_day_ut: float,
    latitude: float,
    longitude: float,
    house_system: str,
) -> tuple[HouseCusps, dict[str, Angle]]:
    """Calculate house cusps, Ascendant, and Midheaven."""
    system_key = house_system.lower()
    if system_key not in HOUSE_SYSTEMS:
        raise ValueError(f"Unsupported house system: {house_system}")

    cusps, ascmc = swe.houses_ex(julian_day_ut, latitude, longitude, HOUSE_SYSTEMS[system_key])
    cusp_map = {index + 1: round(value % 360.0, 6) for index, value in enumerate(cusps)}

    asc_pos = to_zodiac_position(ascmc[0])
    mc_pos = to_zodiac_position(ascmc[1])
    angles = {
        "ascendant": Angle(
            name="Ascendant",
            longitude=asc_pos.longitude,
            sign=asc_pos.sign,
            sign_index=asc_pos.sign_index,
            degree=asc_pos.degree,
        ),
        "midheaven": Angle(
            name="Midheaven",
            longitude=mc_pos.longitude,
            sign=mc_pos.sign,
            sign_index=mc_pos.sign_index,
            degree=mc_pos.degree,
        ),
    }
    return HouseCusps(system=system_key, cusps=cusp_map), angles


def whole_sign_house(planet_longitude: float, asc_longitude: float) -> int:
    """Calculate whole-sign house from planet longitude and Ascendant longitude."""
    planet_sign = int((planet_longitude % 360.0) // 30)
    asc_sign = int((asc_longitude % 360.0) // 30)
    return ((planet_sign - asc_sign) % 12) + 1


def chart_points(chart: Chart, include_angles: bool = True) -> dict[str, float]:
    """Return chart points as name -> longitude."""
    points = {name: placement.longitude for name, placement in chart.placements.items()}
    if include_angles:
        if "ascendant" in chart.angles:
            points["ascendant"] = chart.angles["ascendant"].longitude
        if "midheaven" in chart.angles:
            points["midheaven"] = chart.angles["midheaven"].longitude
    return points


def calculate_chart(birth: BirthData, house_system: str = "whole_sign") -> Chart:
    """Calculate a natal chart from normalized birth data."""
    warnings: list[str] = []
    julian_day_ut = julian_day_ut_from_birth(birth)

    if julian_day_ut is None:
        # Noon chart fallback for missing birth time. This keeps planetary placements usable
        # but suppresses angles/houses.
        noon_birth = birth.model_copy(update={"time": "12:00:00", "time_known": True})
        julian_day_ut = julian_day_ut_from_birth(noon_birth)
        warnings.append("Birth time unknown: calculated planetary placements for local noon; houses and angles omitted.")

    assert julian_day_ut is not None
    longitudes = calculate_planet_longitudes(julian_day_ut)

    houses = None
    angles: dict[str, Angle] = {}
    if birth.time_known and birth.time:
        houses, angles = calculate_houses(
            julian_day_ut=julian_day_ut,
            latitude=birth.latitude,
            longitude=birth.longitude,
            house_system=house_system,
        )
    else:
        warnings.append("Angles and houses require a known birth time.")

    asc_longitude = angles["ascendant"].longitude if "ascendant" in angles else None
    placements: dict[str, Placement] = {}
    for body, longitude in longitudes.items():
        position = to_zodiac_position(longitude)
        house = whole_sign_house(longitude, asc_longitude) if asc_longitude is not None else None
        placements[body] = Placement(
            body=body,
            longitude=position.longitude,
            sign=position.sign,
            sign_index=position.sign_index,
            degree=position.degree,
            house=house,
        )

    return Chart(
        name=birth.name,
        birth=birth,
        julian_day_ut=round(julian_day_ut, 8),
        house_system=house_system,
        placements=placements,
        angles=angles,
        houses=houses,
        warnings=warnings,
    )
