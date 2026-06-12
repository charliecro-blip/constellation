"""Persistence helpers for structured relationship motifs."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, delete, select

from .models import SavedRelationship, SavedRelationshipMotif
from .pattern_registry import get_pattern_metadata
from .schemas import RankedPatternSummary, ReportSynthesisPacket
from .scoring_weights import SUPPRESSION_THRESHOLDS

MAX_SAVED_MOTIFS = 10


def _is_suppressed(pattern: RankedPatternSummary) -> bool:
    adjusted = pattern.adjusted_priority if pattern.adjusted_priority is not None else pattern.priority
    return adjusted < SUPPRESSION_THRESHOLDS["omit"]


def _is_default_gated_asteroid(pattern: RankedPatternSummary) -> bool:
    """Return True for asteroid-like details that should not enter saved motifs.

    The detector already excludes advanced/default-gated asteroids from default reports. This
    extra guard keeps any future advanced asteroid packet entries out of constellation storage.
    """

    return ".asteroid." in pattern.key or pattern.category in {"asteroid_support", "asteroid_overlay"}


def _motif_identity(pattern: RankedPatternSummary) -> tuple[str, str, str]:
    return (pattern.key, pattern.category, pattern.layer)


def select_motifs_for_persistence(
    packet: ReportSynthesisPacket,
    *,
    max_motifs: int = MAX_SAVED_MOTIFS,
) -> list[RankedPatternSummary]:
    """Select compact, deduplicated motifs from the deterministic synthesis packet."""

    candidates: list[RankedPatternSummary] = []
    if packet.lead_pattern is not None:
        candidates.append(packet.lead_pattern)
    candidates.extend(packet.top_ranked_patterns)
    candidates.extend(packet.friction_patterns)
    candidates.extend(packet.composite_themes)

    selected: list[RankedPatternSummary] = []
    seen: set[tuple[str, str, str]] = set()
    for pattern in candidates:
        identity = _motif_identity(pattern)
        if identity in seen or _is_suppressed(pattern) or _is_default_gated_asteroid(pattern):
            continue
        seen.add(identity)
        selected.append(pattern)
        if len(selected) >= max_motifs:
            break
    return selected


def replace_relationship_motifs(
    session: Session,
    relationship: SavedRelationship,
    packet: ReportSynthesisPacket,
) -> list[SavedRelationshipMotif]:
    """Replace stored motifs for a relationship with the current report packet motifs."""

    session.exec(delete(SavedRelationshipMotif).where(SavedRelationshipMotif.relationship_id == relationship.id))
    now = datetime.utcnow()
    motifs: list[SavedRelationshipMotif] = []
    for pattern in select_motifs_for_persistence(packet):
        metadata = get_pattern_metadata(pattern.key)
        motif = SavedRelationshipMotif(
            relationship_id=relationship.id,
            person_a_id=relationship.person_a_id,
            person_b_id=relationship.person_b_id,
            motif_key=pattern.key,
            category=pattern.category,
            title=pattern.title,
            layer=pattern.layer,
            priority=pattern.priority,
            adjusted_priority=pattern.adjusted_priority,
            confidence=pattern.confidence,
            evidence_text=pattern.evidence_text,
            lead_eligible=metadata.lead_eligible,
            created_at=now,
            updated_at=now,
        )
        session.add(motif)
        motifs.append(motif)
    return motifs


def list_relationship_motifs(session: Session, relationship_id: str) -> list[SavedRelationshipMotif]:
    return list(
        session.exec(
            select(SavedRelationshipMotif)
            .where(SavedRelationshipMotif.relationship_id == relationship_id)
            .order_by(SavedRelationshipMotif.priority.desc(), SavedRelationshipMotif.created_at.asc())
        )
    )
