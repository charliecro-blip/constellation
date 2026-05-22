"""Shared data schemas for Constellation."""

from __future__ import annotations

from datetime import date as Date
from datetime import time as Time
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator


class BirthData(BaseModel):
    """Birth data normalized enough for deterministic chart calculation.

    Phase 0 intentionally accepts latitude, longitude, and timezone directly.
    Place lookup can be added later after calculation correctness is proven.
    """

    name: str
    date: str = Field(..., description="Birth date in YYYY-MM-DD format")
    time: str | None = Field(None, description="Local civil time in HH:MM or HH:MM:SS format")
    time_known: bool = True
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = Field(..., description="IANA timezone, e.g. America/Chicago")

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        try:
            Date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("date must use YYYY-MM-DD format") from exc
        return value

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str | None) -> str | None:
        if value is None:
            return value
        pieces = value.split(":")
        if len(pieces) == 2:
            value_to_parse = f"{value}:00"
        else:
            value_to_parse = value
        try:
            Time.fromisoformat(value_to_parse)
        except ValueError as exc:
            raise ValueError("time must use HH:MM or HH:MM:SS format") from exc
        return value

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("timezone must be a valid IANA timezone name") from exc
        return value


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


class HouseOverlay(BaseModel):
    """A planet from one person's chart landing in the other person's house."""

    planet_owner: Literal["person_a", "person_b"]
    house_owner: Literal["person_a", "person_b"]
    body: str
    house: int
    body_longitude: float


class RelationshipCalculation(BaseModel):
    person_a: Chart
    person_b: Chart
    synastry_aspects: list[Aspect]
    house_overlays: list[HouseOverlay] = Field(default_factory=list)
    composite: Chart | None = None
    composite_aspects: list[Aspect] = Field(default_factory=list)
