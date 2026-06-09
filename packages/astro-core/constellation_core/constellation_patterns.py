"""Deterministic summaries of recurring themes across saved relationships."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

RELATIONSHIP_TYPE_LABELS = {
    "ex": "Ex",
    "romantic": "Romantic / current",
    "long_term_partner": "Long-term partner",
    "dating_exploring": "Dating / exploring",
    "unresolved_connection": "Unresolved connection",
    "friend": "Friend",
    "collaborator": "Collaborator",
    "parent": "Parent",
    "sibling": "Sibling",
    "child": "Child",
    "family_other": "Family / other",
    "admired_figure": "Admired figure / mentor",
    "other": "Other",
}

MOTIF_KEYWORDS = [
    {
        "id": "moon_uranus",
        "label": "Moon–Uranus / closeness-distance rhythm",
        "summary_label": "closeness and distance",
        "keywords": ["moon–uranus", "moon-uranus", "moon uranus"],
    },
    {
        "id": "saturn",
        "label": "Saturn / commitment and boundaries",
        "summary_label": "commitment and boundaries",
        "keywords": ["saturn"],
    },
    {
        "id": "pluto",
        "label": "Pluto / intensity and transformation",
        "summary_label": "intensity and transformation",
        "keywords": ["pluto"],
    },
    {
        "id": "mars",
        "label": "Mars / action and friction",
        "summary_label": "action and friction",
        "keywords": ["mars"],
    },
    {
        "id": "venus",
        "label": "Venus / attraction and affection",
        "summary_label": "attraction and affection",
        "keywords": ["venus"],
    },
    {
        "id": "4th_house",
        "label": "4th-house emotional roots",
        "summary_label": "emotional roots",
        "keywords": ["4th house", "4th-house", "fourth house"],
    },
    {
        "id": "5th_house",
        "label": "5th-house creativity and play",
        "summary_label": "creativity and play",
        "keywords": ["5th house", "5th-house", "fifth house"],
    },
    {
        "id": "7th_house",
        "label": "7th-house partnership mirror",
        "summary_label": "partnership mirrors",
        "keywords": ["7th house", "7th-house", "seventh house"],
    },
    {
        "id": "8th_house",
        "label": "8th-house trust, privacy, and emotional depth",
        "summary_label": "trust, privacy, and emotional depth",
        "keywords": ["8th house", "8th-house", "eighth house"],
    },
    {
        "id": "10th_house",
        "label": "10th-house visibility and life direction",
        "summary_label": "visibility and life direction",
        "keywords": ["10th house", "10th-house", "tenth house"],
    },
    {
        "id": "12th_house",
        "label": "12th-house unconscious material",
        "summary_label": "unconscious material",
        "keywords": ["12th house", "12th-house", "twelfth house"],
    },
    {
        "id": "capricorn",
        "label": "Capricorn / structure and steadiness",
        "summary_label": "structure and steadiness",
        "keywords": ["capricorn"],
    },
    {
        "id": "cancer",
        "label": "Cancer / care and emotional safety",
        "summary_label": "care and emotional safety",
        "keywords": ["cancer"],
    },
    {
        "id": "scorpio",
        "label": "Scorpio / depth and trust",
        "summary_label": "depth and trust",
        "keywords": ["scorpio"],
    },
    {
        "id": "libra",
        "label": "Libra / balance and mutuality",
        "summary_label": "balance and mutuality",
        "keywords": ["libra"],
    },
    {
        "id": "conjunction_cluster",
        "label": "Conjunction cluster / concentrated emphasis",
        "summary_label": "concentrated emphasis",
        "keywords": ["conjunction cluster", "conjunctions cluster"],
    },
    {
        "id": "house_overlays",
        "label": "House overlays / repeated natal-zone activation",
        "summary_label": "repeated natal-zone activation",
        "keywords": ["house overlays", "house overlay"],
    },
    {
        "id": "composite",
        "label": "Composite / shared relationship field",
        "summary_label": "shared relationship fields",
        "keywords": ["composite"],
    },
]


@dataclass(frozen=True)
class RelationshipPatternInput:
    """Minimal saved relationship data needed for constellation pattern summaries."""

    relationship_type: str
    person_name: str
    known_themes: list[str] = field(default_factory=list)
    report_markdown: str | None = None


def human_relationship_type(value: str) -> str:
    return RELATIONSHIP_TYPE_LABELS.get(value, value.replace("_", " ").title())


def _normalize_theme(theme: str) -> str:
    return " ".join(theme.strip().lower().split())


def _motifs_for_markdown(markdown: str | None) -> set[str]:
    text = (markdown or "").lower()
    if not text:
        return set()
    motif_ids = set()
    for motif in MOTIF_KEYWORDS:
        if any(keyword in text for keyword in motif["keywords"]):
            motif_ids.add(motif["id"])
    return motif_ids


def build_constellation_pattern_summary(
    relationships: list[RelationshipPatternInput],
) -> dict[str, object]:
    """Build a deterministic first-version summary for saved relationship patterns."""

    relationship_count = len(relationships)
    if relationship_count < 2:
        return {
            "relationship_count": relationship_count,
            "has_enough_data": False,
            "empty_state": "Save two or more relationships to see recurring patterns across your constellation.",
            "relationship_type_counts": [],
            "known_theme_counts": [],
            "recurring_motifs": [],
            "plain_language_summary": "",
        }

    type_counts = Counter(item.relationship_type for item in relationships)
    theme_counts: Counter[str] = Counter()
    for item in relationships:
        unique_themes = {_normalize_theme(theme) for theme in item.known_themes if theme.strip()}
        theme_counts.update(unique_themes)

    motif_people: dict[str, list[str]] = defaultdict(list)
    for index, item in enumerate(relationships, start=1):
        display_name = item.person_name.strip() or f"Relationship {index}"
        for motif_id in _motifs_for_markdown(item.report_markdown):
            motif_people[motif_id].append(display_name)

    recurring_motifs = []
    motif_lookup = {motif["id"]: motif for motif in MOTIF_KEYWORDS}
    for motif in MOTIF_KEYWORDS:
        people = motif_people.get(motif["id"], [])
        if len(people) >= 2:
            recurring_motifs.append(
                {
                    "id": motif["id"],
                    "label": motif["label"],
                    "count": len(people),
                    "people": people,
                    "summary_label": motif["summary_label"],
                }
            )

    relationship_type_counts = [
        {
            "type": relationship_type,
            "label": human_relationship_type(relationship_type),
            "count": count,
        }
        for relationship_type, count in sorted(
            type_counts.items(), key=lambda pair: (-pair[1], human_relationship_type(pair[0]))
        )
    ]
    known_theme_counts = [
        {"theme": theme, "count": count}
        for theme, count in sorted(theme_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    ]

    summary_parts = [motif_lookup[motif["id"]]["summary_label"] for motif in recurring_motifs[:3]]
    if not summary_parts:
        summary_parts = [item["theme"] for item in known_theme_counts[:3]]
    if not summary_parts:
        summary_parts = [item["label"].lower() for item in relationship_type_counts[:2]]

    if summary_parts:
        emphasis = ", ".join(summary_parts[:-1]) + (
            f", and {summary_parts[-1]}" if len(summary_parts) > 1 else summary_parts[0]
        )
        plain_summary = (
            f"Your current saved maps suggest emerging repeats around {emphasis}. "
            "As more relationships are added, this pattern may clarify."
        )
    else:
        plain_summary = (
            "Your current saved maps are beginning to form a constellation. "
            "As more relationships are added, recurring patterns may clarify."
        )

    return {
        "relationship_count": relationship_count,
        "has_enough_data": True,
        "empty_state": None,
        "relationship_type_counts": relationship_type_counts,
        "known_theme_counts": known_theme_counts,
        "recurring_motifs": recurring_motifs,
        "plain_language_summary": plain_summary,
    }
