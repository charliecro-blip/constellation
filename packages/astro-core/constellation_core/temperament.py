"""Deterministic element, modality, and relational temperament helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .natal_profile import SIGN_ELEMENTS, SIGN_MODES
from .schemas import Chart

ELEMENTS = ("fire", "earth", "air", "water")
MODALITIES = ("cardinal", "fixed", "mutable")
PERSONAL_POINTS = ("sun", "moon", "mercury", "venus", "mars")
RELATIONSHIP_POINTS = ("moon", "mercury", "venus", "mars")
RELATIONSHIP_HOUSES = {4, 5, 7, 8}


def sign_temperament(sign: str | None) -> dict[str, str | None]:
    return {"element": SIGN_ELEMENTS.get(sign or ""), "modality": SIGN_MODES.get(sign or "")}


def _empty_counts(keys: tuple[str, ...]) -> dict[str, int]:
    return {key: 0 for key in keys}


def _placement_note(chart: Chart, body: str) -> dict[str, Any] | None:
    placement = chart.placements.get(body)
    if placement is None:
        return None
    note: dict[str, Any] = {"sign": placement.sign, **sign_temperament(placement.sign)}
    if placement.house is not None:
        note["house"] = placement.house
    return note


def _ascendant_note(chart: Chart) -> dict[str, Any] | None:
    asc = chart.angles.get("ascendant")
    if asc is None:
        return None
    return {"sign": asc.sign, **sign_temperament(asc.sign)}


def chart_temperament_summary(chart: Chart) -> dict[str, Any]:
    """Return compact deterministic temperament emphasis for one chart."""
    element_counts: Counter[str] = Counter()
    modality_counts: Counter[str] = Counter()
    personal_element_counts: Counter[str] = Counter()
    personal_modality_counts: Counter[str] = Counter()
    house_emphasis: list[dict[str, Any]] = []

    for body, placement in chart.placements.items():
        element = SIGN_ELEMENTS.get(placement.sign)
        modality = SIGN_MODES.get(placement.sign)
        if element:
            element_counts[element] += 1
        if modality:
            modality_counts[modality] += 1
        if body in PERSONAL_POINTS:
            if element:
                personal_element_counts[element] += 1
            if modality:
                personal_modality_counts[modality] += 1
        if body in RELATIONSHIP_POINTS and placement.house in RELATIONSHIP_HOUSES:
            house_emphasis.append({"body": body, "house": placement.house, "sign": placement.sign, "element": element, "modality": modality})

    asc = chart.angles.get("ascendant")
    if asc:
        element = SIGN_ELEMENTS.get(asc.sign)
        modality = SIGN_MODES.get(asc.sign)
        if element:
            element_counts[element] += 1
        if modality:
            modality_counts[modality] += 1

    return {
        "name": chart.name,
        "elements": _empty_counts(ELEMENTS) | dict(element_counts),
        "modalities": _empty_counts(MODALITIES) | dict(modality_counts),
        "personal_planets": {
            "elements": _empty_counts(ELEMENTS) | dict(personal_element_counts),
            "modalities": _empty_counts(MODALITIES) | dict(personal_modality_counts),
        },
        "moon": _placement_note(chart, "moon"),
        "mercury": _placement_note(chart, "mercury"),
        "venus": _placement_note(chart, "venus"),
        "mars": _placement_note(chart, "mars"),
        "ascendant": _ascendant_note(chart),
        "relationship_house_emphasis": house_emphasis[:6],
    }


def _top_keys(counts: dict[str, int], *, minimum: int = 2) -> list[str]:
    if not counts:
        return []
    high = max(counts.values())
    if high < minimum:
        return []
    return [key for key, value in counts.items() if value == high]


def _pair_note(a: str | None, b: str | None, kind: str) -> str | None:
    if not a or not b:
        return None
    if a == b:
        return f"shared {a} {kind}"
    pairs = {frozenset(("fire", "air")): "movement, speech, curiosity, and pursuit can amplify", frozenset(("earth", "water")): "containment, care, embodied trust, and steadiness may be easier to recognize", frozenset(("fire", "earth")): "momentum and readiness may need translation", frozenset(("air", "water")): "naming a feeling and feeling it may need translation"}
    if kind == "elemental tone":
        return pairs.get(frozenset((a, b)), f"{a}/{b} elemental translation")
    mode_pairs = {frozenset(("cardinal", "mutable")): "initiation and adaptation can move at different speeds", frozenset(("fixed", "mutable")): "continuity and change need explicit pacing", frozenset(("cardinal", "fixed")): "will, response, and pace can become the negotiation"}
    return mode_pairs.get(frozenset((a, b)), f"{a}/{b} modality pacing difference")


def compare_temperaments(chart_a: Chart, chart_b: Chart) -> dict[str, Any]:
    a = chart_temperament_summary(chart_a)
    b = chart_temperament_summary(chart_b)
    a_elements = set(_top_keys(a["personal_planets"]["elements"]))
    b_elements = set(_top_keys(b["personal_planets"]["elements"]))
    a_modes = set(_top_keys(a["personal_planets"]["modalities"]))
    b_modes = set(_top_keys(b["personal_planets"]["modalities"]))

    notes: list[str] = []
    for body, label in [("mercury", "communication"), ("moon", "emotional processing"), ("venus", "affection"), ("mars", "desire")]:
        ae = (a.get(body) or {}).get("element")
        be = (b.get(body) or {}).get("element")
        am = (a.get(body) or {}).get("modality")
        bm = (b.get(body) or {}).get("modality")
        if ae and be and (ae != be or am != bm):
            pieces = [part for part in [_pair_note(ae, be, "elemental tone"), _pair_note(am, bm, "modality")] if part]
            notes.append(f"{label}: " + "; ".join(pieces))

    return {
        "person_a": a,
        "person_b": b,
        "shared_elements": sorted(a_elements & b_elements),
        "contrasting_elements": sorted(a_elements ^ b_elements),
        "shared_modalities": sorted(a_modes & b_modes),
        "contrasting_modalities": sorted(a_modes ^ b_modes),
        "notes": notes[:6],
    }


def compact_temperament_text(comparison: dict[str, Any]) -> str:
    parts: list[str] = []
    if comparison.get("shared_modalities"):
        parts.append("shared modality: " + ", ".join(comparison["shared_modalities"]))
    if comparison.get("shared_elements"):
        parts.append("shared element: " + ", ".join(comparison["shared_elements"]))
    if comparison.get("contrasting_elements"):
        parts.append("element translation: " + ", ".join(comparison["contrasting_elements"]))
    parts.extend(comparison.get("notes", [])[:2])
    return "; ".join(parts)
