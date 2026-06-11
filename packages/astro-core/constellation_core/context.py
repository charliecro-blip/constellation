"""Relationship context models.

Context lets the report distinguish romance, family, friendship, collaboration,
admired-figure resonance, and other relational fields without changing the
underlying chart calculation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .chart import DEFAULT_HOUSE_SYSTEM

RelationshipType = Literal[
    "romantic",
    "dating_exploring",
    "long_term_partner",
    "ex",
    "unresolved_connection",
    "parent",
    "child",
    "sibling",
    "friend",
    "collaborator",
    "admired_figure",
    "family_other",
    "other",
]

RelationshipStatus = Literal[
    "current",
    "past",
    "hypothetical",
    "complicated",
    "unresolved",
    "unknown",
]


class RelationshipContext(BaseModel):
    relationship_type: RelationshipType = "other"
    status: RelationshipStatus = "unknown"
    user_question: str | None = None
    origin_story: str | None = Field(
        None,
        description="Meaningful story, object, place, timing, dream, coincidence, or remembered beginning.",
    )
    known_themes: list[str] = Field(default_factory=list)
    house_system: str = DEFAULT_HOUSE_SYSTEM

    def has_origin_story(self) -> bool:
        return bool(self.origin_story and self.origin_story.strip())
