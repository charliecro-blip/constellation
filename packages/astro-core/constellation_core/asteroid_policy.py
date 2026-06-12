"""Policy for asteroid calculation versus default report surfacing.

Constellation may calculate more minor points than the default Relationship Map
should interpret.  These constants keep the MVP report layer narrow while leaving
advanced points available internally for a later explicit advanced mode.
"""

from __future__ import annotations

MVP_ASTEROIDS = {"juno", "chiron", "ceres"}
OPTIONAL_MVP_ASTEROIDS = {"vesta"}
ADVANCED_ASTEROIDS = {"eros", "psyche", "lilith", "vertex"}

DEFAULT_REPORT_ASTEROIDS = MVP_ASTEROIDS | OPTIONAL_MVP_ASTEROIDS
SUPPORTED_ASTEROID_POINTS = DEFAULT_REPORT_ASTEROIDS | ADVANCED_ASTEROIDS

ASTEROID_CENTRAL_TARGETS = {"sun", "moon", "venus", "mars", "ascendant", "descendant"}
RELATIONSHIP_RELEVANT_HOUSES = {1, 5, 7, 8, 12}
DEFAULT_ASTEROID_ORB = 2.0
