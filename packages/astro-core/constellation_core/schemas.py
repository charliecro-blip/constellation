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
    birthplace_label: str | None = None

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


class RankedPatternSummary(BaseModel):
    """Compact deterministic pattern summary for AI report guidance."""

    key: str
    title: str
    category: str
    tier: int | None = None
    priority: int
    adjusted_priority: int | None = None
    confidence: str
    layer: str
    evidence_text: str | None = None
    interpretive_reason: str | None = None



class DynamicDetail(BaseModel):
    """Expandable interpretive context for a central relationship dynamic."""

    id: str
    title: str
    kind: Literal[
        "synastry_aspect",
        "house_overlay",
        "angle_contact",
        "composite_aspect",
        "composite_pattern",
        "motif",
        "profile_theme",
    ]
    summary: str
    read_more: str
    technical_factors: list[str] = Field(default_factory=list)
    related_dynamics: list[str] = Field(default_factory=list)
    repair_prompt: str | None = None
    motif_category: str | None = None
    priority: int
    section: str


class ReportPatternDiagnostics(BaseModel):
    """Compact developer-facing view of a ranked deterministic pattern."""

    key: str
    title: str
    category: str
    tier: int | None = None
    priority: int
    adjusted_priority: int | None = None
    confidence: str
    layer: str
    lead_eligible: bool
    evidence: list[str] = Field(default_factory=list)


class ChartSanityDiagnostics(BaseModel):
    """Small chart-calculation summary for diagnostics, without raw chart dumps."""

    name: str
    time_known: bool
    house_system: str
    ascendant: str | None = None
    midheaven: str | None = None
    sun: str | None = None
    moon: str | None = None
    venus: str | None = None
    mars: str | None = None
    birthplace: str | None = None
    timezone: str
    coordinates: str
    warnings: list[str] = Field(default_factory=list)


class AsteroidPolicyDiagnostics(BaseModel):
    """Developer-facing summary of default versus gated asteroid surfacing."""

    included_asteroid_patterns: list[ReportPatternDiagnostics] = Field(default_factory=list)
    suppressed_asteroid_patterns: list[str] = Field(default_factory=list)
    default_report_asteroids: list[str] = Field(default_factory=list)
    advanced_asteroids_suppressed: list[str] = Field(default_factory=list)


class ReportDiagnostics(BaseModel):
    """Compact deterministic report diagnostics for builder QA."""

    house_system: str
    person_a_chart_sanity: ChartSanityDiagnostics
    person_b_chart_sanity: ChartSanityDiagnostics
    top_ranked_patterns: list[ReportPatternDiagnostics] = Field(default_factory=list)
    selected_lead_pattern: ReportPatternDiagnostics | None = None
    overview_central_patterns: list[ReportPatternDiagnostics] = Field(default_factory=list)
    friction_patterns: list[ReportPatternDiagnostics] = Field(default_factory=list)
    composite_themes: list[ReportPatternDiagnostics] = Field(default_factory=list)
    motif_persistence_summary: list[ReportPatternDiagnostics] = Field(default_factory=list)
    asteroid_policy_summary: AsteroidPolicyDiagnostics
    ai_synthesis_packet_summary: dict[str, object] | None = None
    temperament_summary: dict[str, object] | None = None


class ReportSynthesisPacket(BaseModel):
    """Deterministic priorities the AI enhancer should preserve."""

    relationship_type: str | None = None
    status: str | None = None
    user_question: str | None = None
    origin_story: str | None = None
    house_system: str | None = None
    top_ranked_patterns: list[RankedPatternSummary] = Field(default_factory=list)
    lead_pattern: RankedPatternSummary | None = None
    friction_patterns: list[RankedPatternSummary] = Field(default_factory=list)
    repair_themes: list[str] = Field(default_factory=list)
    composite_themes: list[RankedPatternSummary] = Field(default_factory=list)
    chart_sanity_summary: str | None = None
    dynamic_details: list[DynamicDetail] = Field(default_factory=list)
    temperament_summary: dict[str, object] | None = None
