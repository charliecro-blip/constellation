"""Relationship context models.

Context lets the report distinguish romance, family, friendship, collaboration,
admired-figure resonance, and other relational fields without changing the
underlying chart calculation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

RelationshipType = Literal[
    "romantic",
    "long_term_partner",
    "ex",
    "parent",
    "child",
    "sibling",
    "friend",
    "collaborator",
    "admired_figure",
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

    def has_origin_story(self) -> bool:
        return bool(self.origin_story and self.origin_story.strip())
