"""House overlay calculations."""

from __future__ import annotations

from .chart import house_for_longitude
from .schemas import Chart, HouseOverlay


def calculate_house_overlays(person_a: Chart, person_b: Chart) -> list[HouseOverlay]:
    """Calculate where each person's planets land in the other person's houses.

    The house owner's selected house system is used. If a birth time is unknown
    and Ascendant/houses are unavailable, that direction of overlays is omitted.
    """
    overlays: list[HouseOverlay] = []

    if "ascendant" in person_b.angles:
        for body, placement in person_a.placements.items():
            house = house_for_longitude(person_b, placement.longitude)
            if house is None:
                continue
            overlays.append(HouseOverlay(
                planet_owner="person_a",
                house_owner="person_b",
                body=body,
                house=house,
                body_longitude=placement.longitude,
            ))

    if "ascendant" in person_a.angles:
        for body, placement in person_b.placements.items():
            house = house_for_longitude(person_a, placement.longitude)
            if house is None:
                continue
            overlays.append(HouseOverlay(
                planet_owner="person_b",
                house_owner="person_a",
                body=body,
                house=house,
                body_longitude=placement.longitude,
            ))

    return overlays
