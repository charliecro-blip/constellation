"""Surface vs engine interpretation helpers.

This layer distinguishes visible/socially readable relationship patterns from
deeper mechanics that drive intensity, volatility, bonding, or repair demands.
"""

from __future__ import annotations

from .patterns import Pattern


SURFACE_CATEGORIES = {
    "recognition",
    "communication",
    "affection",
    "relationship_identity",
    "identity_body",
    "public_direction",
    "romance_creativity",
}

ENGINE_CATEGORIES = {
    "desire",
    "attraction_intensity",
    "emotional_intensity",
    "intensity",
    "emotional_structure",
    "bond_structure",
    "relationship_structure",
    "action_structure",
    "emotional_variability",
    "intimacy_depth",
    "hidden_field",
    "home_roots",
    "daily_life",
}


def surface_patterns(patterns: list[Pattern], limit: int = 5) -> list[Pattern]:
    selected = [pattern for pattern in patterns if pattern.category in SURFACE_CATEGORIES]
    return sorted(selected, key=lambda pattern: pattern.priority, reverse=True)[:limit]


def engine_patterns(patterns: list[Pattern], limit: int = 5) -> list[Pattern]:
    selected = [pattern for pattern in patterns if pattern.category in ENGINE_CATEGORIES]
    return sorted(selected, key=lambda pattern: pattern.priority, reverse=True)[:limit]


def surface_engine_markdown(patterns: list[Pattern]) -> str:
    surface = surface_patterns(patterns)
    engine = engine_patterns(patterns)

    if not surface and not engine:
        return "No surface/engine distinction has been selected yet."

    lines: list[str] = []
    lines.append(
        "This section separates what may be easy to notice at first contact from the deeper mechanism that can drive the relationship over time."
    )
    lines.append("")

    if surface:
        lines.append("### Surface")
        lines.append("")
        lines.append("These are the more visible or immediately legible parts of the field:")
        for pattern in surface:
            evidence = "; ".join(pattern.evidence)
            lines.append(f"- **{pattern.title}** — {evidence}")
        lines.append("")

    if engine:
        lines.append("### Engine")
        lines.append("")
        lines.append("These are the deeper mechanics that may determine intensity, bonding, strain, or repair requirements:")
        for pattern in engine:
            evidence = "; ".join(pattern.evidence)
            lines.append(f"- **{pattern.title}** — {evidence}")
        lines.append("")

    if surface and engine:
        lines.append(
            "The interpretive task is to avoid mistaking the surface for the whole story. A relationship can look friendly, romantic, easy, or familiar while being powered by a much more demanding engine underneath."
        )
    elif engine:
        lines.append(
            "The current map is driven more by engine than by surface. This can make the relationship feel consequential, compelling, or hard to keep casual."
        )
    else:
        lines.append(
            "The current map is led more by surface signatures than by deeper pressure signatures. This may feel easier to name, but still needs lived context."
        )

    return "\n".join(lines)
