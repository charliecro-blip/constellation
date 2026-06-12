"""Deterministic summaries of recurring themes across saved relationships."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import TypedDict

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

CATEGORY_LABELS = {
    "emotional_recognition": "Emotional Recognition",
    "erotic_charge": "Erotic Charge",
    "trust_depth": "Trust / Depth",
    "stability_container": "Stability / Container",
    "communication_heat": "Communication Heat",
    "volatility": "Volatility",
    "private_roots": "Private Roots",
    "devotion_contract": "Devotion / Contract",
    "projection_mirror": "Projection / Mirror",
    "familiar_pull": "Familiar Pull",
    "repair_capacity": "Repair Capacity",
    "wounding_healing": "Tenderness / Repair",
    "public_life": "Public Life",
    "supporting_texture": "Supporting Texture",
}

CATEGORY_DESCRIPTIONS = {
    "emotional_recognition": "Where someone feels familiar, legible, or emotionally known.",
    "erotic_charge": "Where attraction, pursuit, chemistry, or creative heat concentrates.",
    "stability_container": "Where commitment, time, limits, or responsibility shape the bond.",
    "trust_depth": "Where vulnerability, honesty, and deeper psychological contact are emphasized.",
    "communication_heat": "Where language, timing, nervous systems, or conflict patterns matter.",
    "private_roots": "Where home, family patterns, memory, or attachment history are activated.",
    "devotion_contract": "Where loyalty, vows, care, or relational obligation become central.",
    "projection_mirror": "Where the other person reflects disowned or amplified parts of the self.",
    "repair_capacity": "Where the bond shows pathways for working through friction.",
}


class StructuredMotifInput(TypedDict, total=False):
    key: str
    category: str
    title: str
    relationship_id: str
    evidence_text: str | None


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
    relationship_id: str | None = None
    known_themes: list[str] = field(default_factory=list)
    report_markdown: str | None = None
    structured_motifs: list[StructuredMotifInput] = field(default_factory=list)


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


def _category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category.replace("_", " ").title())


def _category_description(category: str | None) -> str:
    if not category:
        return "A recurring relationship motif that may become clearer as more maps are generated."
    return CATEGORY_DESCRIPTIONS.get(
        category,
        "A recurring relationship motif that may become clearer as more maps are generated.",
    )


def _compact_evidence(text: str | None) -> str | None:
    cleaned = " ".join((text or "").strip().split())
    if not cleaned:
        return None
    return cleaned if len(cleaned) <= 180 else f"{cleaned[:177].rstrip()}…"


def _summary_label(label: str) -> str:
    return label.replace(" / ", "/").lower()


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
            "top_motif_categories": [],
            "relationship_motifs": [],
            "plain_language_summary": "",
        }

    type_counts = Counter(item.relationship_type for item in relationships)
    theme_counts: Counter[str] = Counter()
    for item in relationships:
        unique_themes = {_normalize_theme(theme) for theme in item.known_themes if theme.strip()}
        theme_counts.update(unique_themes)

    motif_people: dict[str, list[str]] = defaultdict(list)
    motif_relationship_ids: dict[str, list[str]] = defaultdict(list)
    motif_evidence: dict[str, list[str]] = defaultdict(list)
    motif_labels: dict[str, str] = {}
    motif_categories: dict[str, str] = {}
    relationship_motifs: list[dict[str, object]] = []
    category_relationships: dict[str, set[str]] = defaultdict(set)
    has_structured_motifs = any(item.structured_motifs for item in relationships)

    if has_structured_motifs:
        for index, item in enumerate(relationships, start=1):
            display_name = item.person_name.strip() or f"Relationship {index}"
            relationship_key = item.relationship_id or display_name
            seen_in_relationship: set[str] = set()
            for motif in item.structured_motifs:
                motif_id = motif["category"]
                if motif_id in seen_in_relationship:
                    continue
                seen_in_relationship.add(motif_id)
                motif_people[motif_id].append(display_name)
                motif_relationship_ids[motif_id].append(motif.get("relationship_id", relationship_key))
                evidence = _compact_evidence(motif.get("evidence_text"))
                if evidence and evidence not in motif_evidence[motif_id]:
                    motif_evidence[motif_id].append(evidence)
                motif_labels[motif_id] = _category_label(motif["category"])
                motif_categories[motif_id] = motif["category"]
                category_relationships[motif["category"]].add(relationship_key)
            if item.structured_motifs:
                seen_relationship_titles: set[tuple[str, str]] = set()
                compact_motifs = []
                for motif in item.structured_motifs:
                    title = motif.get("title") or _category_label(motif["category"])
                    identity = (motif["category"], title)
                    if identity in seen_relationship_titles:
                        continue
                    seen_relationship_titles.add(identity)
                    compact_motifs.append(
                        {
                            "title": title,
                            "category": motif["category"],
                            "category_label": _category_label(motif["category"]),
                            "description": _category_description(motif["category"]),
                            "evidence": _compact_evidence(motif.get("evidence_text")),
                        }
                    )
                relationship_motifs.append(
                    {
                        "relationship_id": relationship_key,
                        "label": display_name,
                        "motifs": compact_motifs[:4],
                    }
                )
    else:
        motif_lookup = {motif["id"]: motif for motif in MOTIF_KEYWORDS}
        for index, item in enumerate(relationships, start=1):
            display_name = item.person_name.strip() or f"Relationship {index}"
            for motif_id in _motifs_for_markdown(item.report_markdown):
                motif_people[motif_id].append(display_name)
                motif_labels[motif_id] = motif_lookup[motif_id]["label"]
                motif_categories[motif_id] = motif_id

    recurring_motifs = []
    motif_lookup = {motif["id"]: motif for motif in MOTIF_KEYWORDS}
    ordered_ids = list(motif_people.keys()) if has_structured_motifs else [motif["id"] for motif in MOTIF_KEYWORDS]
    for motif_id in ordered_ids:
        people = motif_people.get(motif_id, [])
        if len(people) >= 2:
            fallback = motif_lookup.get(motif_id, {})
            label = motif_labels.get(motif_id, fallback.get("label", _category_label(motif_id)))
            recurring_motifs.append(
                {
                    "id": motif_id,
                    "label": label,
                    "count": len(people),
                    "people": people,
                    "summary_label": fallback.get("summary_label", _summary_label(label)),
                    "category": motif_categories.get(motif_id),
                    "category_label": _category_label(motif_categories.get(motif_id) or motif_id),
                    "description": _category_description(motif_categories.get(motif_id) or motif_id),
                    "evidence": motif_evidence.get(motif_id, [])[:2],
                    "relationship_ids": motif_relationship_ids.get(motif_id, []),
                }
            )

    recurring_motifs.sort(key=lambda item: (-item["count"], item["label"]))

    top_motif_categories = [
        {
            "category": category,
            "label": _category_label(category),
            "description": _category_description(category),
            "count": len(relationship_ids),
        }
        for category, relationship_ids in sorted(
            category_relationships.items(), key=lambda pair: (-len(pair[1]), _category_label(pair[0]))
        )[:5]
    ]

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

    summary_parts = [motif["summary_label"] for motif in recurring_motifs[:3]]
    if not summary_parts:
        summary_parts = [_summary_label(item["label"]) for item in top_motif_categories[:3]]
    if not summary_parts:
        summary_parts = [item["theme"] for item in known_theme_counts[:3]]
    if not summary_parts:
        summary_parts = [item["label"].lower() for item in relationship_type_counts[:2]]

    if summary_parts:
        emphasis = ", ".join(summary_parts[:-1]) + (
            f", and {summary_parts[-1]}" if len(summary_parts) > 1 else summary_parts[0]
        )
        plain_summary = (
            f"Your saved maps currently emphasize {emphasis}. "
            "As you add more relationships, this pattern will become clearer."
        )
    else:
        plain_summary = (
            "Your saved maps are beginning to form a constellation. "
            "As you add more relationships, recurring patterns may become clearer."
        )

    return {
        "relationship_count": relationship_count,
        "has_enough_data": True,
        "empty_state": None,
        "relationship_type_counts": relationship_type_counts,
        "known_theme_counts": known_theme_counts,
        "recurring_motifs": recurring_motifs,
        "top_motif_categories": top_motif_categories,
        "relationship_motifs": relationship_motifs[:6],
        "plain_language_summary": plain_summary,
    }
