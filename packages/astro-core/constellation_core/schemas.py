"""Shared data schemas for Constellation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BirthData(BaseModel):
    """Birth data normalized enough for deterministic chart calculation.

    Phase 0 intentionally accepts latitude, longitude, and timezone directly.
    Place lookup can be added later after calculation correctness is proven.
    """

    name: str
    date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    time: str | None = Field(None, description="Local civil time in HH:MM or HH:MM:SS format")
    time_known: bool = True
    latitude: float
    longitude: float
    timezone: str = Field(..., description="IANA timezone, e.g. America/Chicago")


class Placement(BaseModel):
    body: str
    longitude: float
    sign: str
    sign_index: int
    degree: float
    house: int | None = None


class Angle(BaseModel):
    name: Literal["Ascendant", "Midheaven"]
    longitude: float
    sign: str
    sign_index: int
    degree: float


class HouseCusps(BaseModel):
    system: str
    cusps: dict[int, float]


class Chart(BaseModel):
    name: str
    birth: BirthData
    julian_day_ut: float | None
    house_system: str
    placements: dict[str, Placement]
    angles: dict[str, Angle] = Field(default_factory=dict)
    houses: HouseCusps | None = None
    warnings: list[str] = Field(default_factory=list)


class Aspect(BaseModel):
    point_a: str
    point_b: str
    aspect: str
    exact_angle: float
    orb: float


class RelationshipCalculation(BaseModel):
    person_a: Chart
    person_b: Chart
    synastry_aspects: list[Aspect]
    composite: Chart | None = None
    composite_aspects: list[Aspect] = Field(default_factory=list)
