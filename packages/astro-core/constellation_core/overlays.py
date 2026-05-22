"""House overlay calculations."""

from __future__ import annotations

from .chart import whole_sign_house
from .schemas import Chart, HouseOverlay


def calculate_house_overlays(person_a: Chart, person_b: Chart) -> list[HouseOverlay]:
    """Calculate where each person's planets land in the other person's houses.

    Phase 1 uses whole-sign house logic based on the house owner's Ascendant.
    If either birth time is unknown and Ascendant is unavailable, that direction
    of overlays is omitted.
    """
    overlays: list[HouseOverlay] = []

    if "ascendant" in person_b.angles:
        b_asc = person_b.angles["ascendant"].longitude
        for body, placement in person_a.placements.items():
            overlays.append(HouseOverlay(
                planet_owner="person_a",
                house_owner="person_b",
                body=body,
                house=whole_sign_house(placement.longitude, b_asc),
                body_longitude=placement.longitude,
            ))

    if "ascendant" in person_a.angles:
        a_asc = person_a.angles["ascendant"].longitude
        for body, placement in person_b.placements.items():
            overlays.append(HouseOverlay(
                planet_owner="person_b",
                house_owner="person_a",
                body=body,
                house=whole_sign_house(placement.longitude, a_asc),
                body_longitude=placement.longitude,
            ))

    return overlays
