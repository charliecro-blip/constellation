"""Shared doctrine constants for relationship-pattern report prioritization.

These values describe report emphasis, not relationship quality. They are kept
separate from the current weighting implementation so future ranking work can
be tuned without hunting through detector and report code.
"""

from __future__ import annotations

TIER_WEIGHTS = {
    1: 100,
    2: 70,
    3: 40,
    4: 15,
}

SUPPRESSION_THRESHOLDS = {
    "omit": 25,
    "supporting": 45,
    "brief": 70,
}

LEAD_ELIGIBLE_CATEGORIES = {
    "emotional_recognition",
    "erotic_charge",
    "stability_container",
    "devotion_contract",
}

# Placeholders for the next ranking pass. These are intentionally conservative
# until the full prioritization algorithm is introduced.
ORB_CURVE = {
    "exact": 1.25,
    "close": 1.10,
    "moderate": 1.00,
    "wide": 0.85,
}

ASPECT_MULTIPLIERS = {
    "conjunction": 1.15,
    "opposition": 1.05,
    "square": 1.00,
    "trine": 0.95,
    "sextile": 0.85,
}

PLANET_WEIGHTS = {
    "sun": 1.15,
    "moon": 1.20,
    "venus": 1.10,
    "mars": 1.05,
    "mercury": 0.85,
    "jupiter": 0.80,
    "saturn": 1.10,
    "uranus": 0.90,
    "neptune": 0.90,
    "pluto": 1.00,
    "north_node": 0.95,
    "south_node": 0.95,
}

HOUSE_BONUSES = {
    1: 8,
    4: 8,
    5: 6,
    7: 10,
    8: 8,
    10: 2,
}

CONVERGENCE_MULTIPLIERS = {
    "repeated_theme": 1.15,
    "cross_layer_echo": 1.20,
    "context_requested": 1.10,
}
