"""Persistence models for saved birth profiles and relationships."""

from __future__ import annotations

from datetime import date, datetime, time
from uuid import uuid4

from sqlmodel import Field, SQLModel

from .chart import DEFAULT_HOUSE_SYSTEM


def _utcnow() -> datetime:
    return datetime.utcnow()


class BirthProfile(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str | None = Field(default=None, index=True)
    anonymous_id: str | None = Field(default=None, index=True)

    display_name: str
    birth_date: date
    birth_time: time | None = None
    time_known: bool = True
    latitude: float
    longitude: float
    timezone: str
    birthplace_label: str | None = None
    geocoding_source: str | None = None

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class SavedRelationship(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str | None = Field(default=None, index=True)
    anonymous_id: str | None = Field(default=None, index=True)

    person_a_id: str = Field(foreign_key="birthprofile.id", index=True)
    person_b_id: str = Field(foreign_key="birthprofile.id", index=True)
    relationship_type: str
    status: str
    user_question: str | None = None
    origin_story: str | None = None
    known_themes_json: str = "[]"
    house_system: str = DEFAULT_HOUSE_SYSTEM

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class SavedRelationshipMotif(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    relationship_id: str = Field(foreign_key="savedrelationship.id", index=True)
    person_a_id: str = Field(foreign_key="birthprofile.id", index=True)
    person_b_id: str = Field(foreign_key="birthprofile.id", index=True)

    motif_key: str = Field(index=True)
    category: str = Field(index=True)
    title: str
    layer: str = Field(index=True)
    priority: int
    adjusted_priority: int | None = None
    confidence: str | None = None
    evidence_text: str | None = None
    lead_eligible: bool = False

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)


class SavedReport(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    relationship_id: str = Field(foreign_key="savedrelationship.id", index=True)
    markdown: str
    calculation_engine_version: str = "v0.1.0"
    interpretation_engine_version: str = "v0.1.0"
    report_template_version: str = "v0.1.0"
    generated_at: datetime = Field(default_factory=_utcnow)
    created_at: datetime = Field(default_factory=_utcnow)


class ReportFeedback(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    relationship_id: str | None = Field(default=None, foreign_key="savedrelationship.id", index=True)
    saved_report_id: str | None = Field(default=None, foreign_key="savedreport.id", index=True)

    usefulness_rating: int | None = None
    accuracy_rating: int | None = None
    clarity_rating: int | None = None
    felt_seen_rating: int | None = None
    too_long: bool | None = None
    too_intense: bool | None = None
    too_technical: bool | None = None

    freeform_comment: str | None = None
    what_landed: str | None = None
    what_felt_off: str | None = None
    central_theme_feedback: str | None = None
    tester_label: str | None = None
    report_version_metadata_json: str | None = None

    created_at: datetime = Field(default_factory=_utcnow)
