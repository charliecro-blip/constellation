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

ASTEROID_IDS: dict[str, int] = {
    "chiron": swe.CHIRON,
    "juno": swe.JUNO,
    "ceres": swe.CERES,
    "vesta": swe.VESTA,
    "psyche": swe.AST_OFFSET + 16,
    "eros": swe.AST_OFFSET + 433,
}

DEFAULT_HOUSE_SYSTEM = "placidus"

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


def calculate_planet_longitudes(julian_day_ut: float) -> tuple[dict[str, float], list[str]]:
    """Calculate tropical ecliptic longitudes for required planets and supported asteroids."""
    longitudes: dict[str, float] = {}
    warnings: list[str] = []
    for name, planet_id in PLANET_IDS.items():
        result, _flags = swe.calc_ut(julian_day_ut, planet_id, swe.FLG_SWIEPH)
        longitudes[name] = result[0] % 360.0

    longitudes["south_node"] = opposite_longitude(longitudes["north_node"])

    omitted_asteroids: list[str] = []
    for name, asteroid_id in ASTEROID_IDS.items():
        try:
            result, _flags = swe.calc_ut(julian_day_ut, asteroid_id, swe.FLG_SWIEPH)
        except swe.Error:
            omitted_asteroids.append(name.title())
            continue
        longitudes[name] = result[0] % 360.0
    if omitted_asteroids:
        warnings.append(
            f"Asteroid ephemeris unavailable for {', '.join(omitted_asteroids)}; omitted from relationship asteroid checks."
        )
    return longitudes, warnings


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


def quadrant_house(planet_longitude: float, cusps: dict[int, float]) -> int | None:
    """Return the house containing a longitude for systems with explicit cusps."""
    if len(cusps) < 12:
        return None
    longitude = planet_longitude % 360.0
    for house in range(1, 13):
        start = cusps[house] % 360.0
        end = cusps[1 if house == 12 else house + 1] % 360.0
        adjusted_end = end + (360.0 if end <= start else 0.0)
        adjusted_longitude = longitude + (360.0 if longitude < start else 0.0)
        if start <= adjusted_longitude < adjusted_end:
            return house
    return None


def house_for_longitude(chart: Chart, planet_longitude: float) -> int | None:
    """Calculate a placement/overlay house using the chart's configured house system."""
    asc = chart.angles.get("ascendant")
    if asc is None:
        return None
    if chart.house_system == "whole_sign" or chart.houses is None:
        return whole_sign_house(planet_longitude, asc.longitude)
    return quadrant_house(planet_longitude, chart.houses.cusps)


def chart_points(chart: Chart, include_angles: bool = True) -> dict[str, float]:
    """Return chart points as name -> longitude."""
    points = {name: placement.longitude for name, placement in chart.placements.items()}
    if include_angles:
        if "ascendant" in chart.angles:
            points["ascendant"] = chart.angles["ascendant"].longitude
        if "midheaven" in chart.angles:
            points["midheaven"] = chart.angles["midheaven"].longitude
    return points


def calculate_chart(birth: BirthData, house_system: str = DEFAULT_HOUSE_SYSTEM) -> Chart:
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
    longitudes, asteroid_warnings = calculate_planet_longitudes(julian_day_ut)
    warnings.extend(asteroid_warnings)

    houses = None
    angles: dict[str, Angle] = {}
    if birth.time_known and birth.time:
        houses, angles = calculate_houses(
            julian_day_ut=julian_day_ut,
            latitude=birth.latitude,
            longitude=birth.longitude,
            house_system=house_system.lower(),
        )
    else:
        warnings.append("Angles and houses require a known birth time.")

    chart_shell = Chart(
        name=birth.name,
        birth=birth,
        julian_day_ut=round(julian_day_ut, 8),
        house_system=house_system.lower(),
        placements={},
        angles=angles,
        houses=houses,
        warnings=[],
    )
    placements: dict[str, Placement] = {}
    for body, longitude in longitudes.items():
        position = to_zodiac_position(longitude)
        house = house_for_longitude(chart_shell, longitude)
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
        house_system=house_system.lower(),
        placements=placements,
        angles=angles,
        houses=houses,
        warnings=warnings,
    )
