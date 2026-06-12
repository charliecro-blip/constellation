"""Golden Relationship Map QA fixtures.

These cases protect report-priority doctrine without requiring manual report
reading. They intentionally use compact synthetic charts so tests can assert
structured diagnostics rather than brittle full-report prose.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from constellation_core.context import RelationshipContext
from constellation_core.schemas import Angle, Aspect, BirthData, Chart, HouseOverlay, Placement, RelationshipCalculation


@dataclass(frozen=True)
class RelationshipGoldenCase:
    name: str
    relationship: RelationshipCalculation
    context: RelationshipContext
    expected_categories: list[str] = field(default_factory=list)
    alternate_contexts: dict[str, RelationshipContext] = field(default_factory=dict)


def _birth(name: str = "A") -> BirthData:
    return BirthData(
        name=name,
        date="1992-01-03",
        time="17:37",
        time_known=True,
        latitude=29.4252,
        longitude=-98.4946,
        timezone="America/Chicago",
    )


def placement(body: str, longitude: float, sign: str = "Aries", house: int | None = None) -> Placement:
    return Placement(
        body=body,
        longitude=longitude,
        sign=sign,
        sign_index=0,
        degree=longitude % 30,
        house=house,
    )


def synthetic_chart(name: str, *, house_system: str = "placidus", placements: dict[str, Placement] | None = None) -> Chart:
    return Chart(
        name=name,
        birth=_birth(name),
        julian_day_ut=None,
        house_system=house_system,
        placements=placements
        or {
            "sun": placement("sun", 10, "Aries", 1),
            "moon": placement("moon", 45, "Taurus", 2),
            "venus": placement("venus", 78, "Gemini", 3),
            "mars": placement("mars", 112, "Cancer", 4),
        },
        angles={
            "ascendant": Angle(name="Ascendant", longitude=0, sign="Aries", sign_index=0, degree=0),
            "midheaven": Angle(name="Midheaven", longitude=90, sign="Cancer", sign_index=3, degree=0),
        },
    )


def relationship(*, aspects: list[Aspect], overlays: list[HouseOverlay] | None = None, composite_aspects: list[Aspect] | None = None, composite: Chart | None = None) -> RelationshipCalculation:
    return RelationshipCalculation(
        person_a=synthetic_chart("A"),
        person_b=synthetic_chart("B"),
        synastry_aspects=aspects,
        house_overlays=overlays or [],
        composite=composite,
        composite_aspects=composite_aspects or [],
    )


ROMANTIC_CONTEXT = RelationshipContext(relationship_type="romantic", status="current")


GOLDEN_RELATIONSHIP_CASES: dict[str, RelationshipGoldenCase] = {
    "emotional_recognition_leads": RelationshipGoldenCase(
        name="emotional_recognition_leads",
        context=ROMANTIC_CONTEXT,
        expected_categories=["emotional_recognition", "communication_heat"],
        relationship=relationship(
            aspects=[
                Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.2),
                Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1),
            ]
        ),
    ),
    "communication_context_exception": RelationshipGoldenCase(
        name="communication_context_exception",
        context=RelationshipContext(
            relationship_type="romantic",
            status="current",
            user_question="Why do our texts become conflict so quickly, and how should we communicate?",
            known_themes=["communication", "texting"],
        ),
        expected_categories=["communication_heat"],
        relationship=relationship(
            aspects=[Aspect(point_a="mercury", point_b="mars", aspect="square", exact_angle=90, orb=0.1)]
        ),
    ),
    "public_life_context_exception": RelationshipGoldenCase(
        name="public_life_context_exception",
        context=ROMANTIC_CONTEXT,
        alternate_contexts={
            "work": RelationshipContext(
                relationship_type="collaborator",
                status="current",
                user_question="How does our work collaboration, career visibility, and public direction function?",
                known_themes=["work", "collaboration"],
            )
        },
        expected_categories=["emotional_recognition", "public_life"],
        relationship=relationship(
            aspects=[
                Aspect(point_a="midheaven", point_b="sun", aspect="conjunction", exact_angle=0, orb=0.1),
                Aspect(point_a="sun", point_b="moon", aspect="trine", exact_angle=120, orb=5.8),
            ],
            overlays=[
                HouseOverlay(
                    planet_owner="person_a",
                    house_owner="person_b",
                    body="sun",
                    house=10,
                    body_longitude=10,
                )
            ],
        ),
    ),
    "trust_depth_persists": RelationshipGoldenCase(
        name="trust_depth_persists",
        context=ROMANTIC_CONTEXT,
        expected_categories=["emotional_recognition", "trust_depth"],
        relationship=relationship(
            aspects=[
                Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.4),
                Aspect(point_a="moon", point_b="pluto", aspect="conjunction", exact_angle=0, orb=0.2),
            ],
            overlays=[
                HouseOverlay(
                    planet_owner="person_a",
                    house_owner="person_b",
                    body="venus",
                    house=8,
                    body_longitude=78,
                )
            ],
        ),
    ),
    "saturn_container_repair": RelationshipGoldenCase(
        name="saturn_container_repair",
        context=ROMANTIC_CONTEXT,
        expected_categories=["stability_container"],
        relationship=relationship(
            aspects=[Aspect(point_a="moon", point_b="saturn", aspect="opposition", exact_angle=180, orb=0.2)]
        ),
    ),
    "asteroid_gating": RelationshipGoldenCase(
        name="asteroid_gating",
        context=ROMANTIC_CONTEXT,
        expected_categories=["emotional_recognition"],
        relationship=relationship(
            aspects=[
                Aspect(point_a="sun", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.3),
                Aspect(point_a="juno", point_b="venus", aspect="conjunction", exact_angle=0, orb=0.1),
                Aspect(point_a="eros", point_b="venus", aspect="conjunction", exact_angle=0, orb=0.1),
                Aspect(point_a="psyche", point_b="moon", aspect="conjunction", exact_angle=0, orb=0.1),
            ],
        ),
    ),
}
