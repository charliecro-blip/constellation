"""Persistence models for saved birth profiles and relationships."""

from __future__ import annotations

from datetime import date, datetime, time
from uuid import uuid4

from sqlmodel import Field, SQLModel


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
    house_system: str = "placidus"

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
