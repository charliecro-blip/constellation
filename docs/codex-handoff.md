# Codex Handoff

## Project
Constellation is a relational astrology MVP.

The build target is a calculation-first prototype that can generate a structured Relationship Field Map from two birth records.

## Current Pipeline

1. Birth fixtures provide normalized birth data.
2. `calculate_chart` generates natal placements, nodes, angles, and houses.
3. `calculate_relationship` generates person A chart, person B chart, synastry aspects, midpoint composite placements, and composite aspects.
4. `detect_relationship_patterns` ranks early deterministic relationship patterns.
5. `generate_relationship_report` produces a first-pass Markdown Relationship Field Map.

## Current Stack

- Python 3.11
- Swiss Ephemeris via `pyswisseph`
- Pydantic schemas
- Pytest
- GitHub Actions

## Setup

```bash
python -m pip install --upgrade pip
pip install -e '.[dev]'
pytest -q
```

## Important Files

- `packages/astro-core/constellation_core/chart.py`
- `packages/astro-core/constellation_core/relationship.py`
- `packages/astro-core/constellation_core/composite.py`
- `packages/astro-core/constellation_core/patterns.py`
- `packages/astro-core/constellation_core/interpretations.py`
- `packages/astro-core/constellation_core/report.py`
- `packages/astro-core/constellation_core/context.py`
- `docs/technical-spec.md`
- `docs/report-structure.md`
- `docs/product-doctrine.md`

## Product Doctrine

Do not build a compatibility scorer.

The app should describe:
- mutual activation
- emotional regulation
- desire and affection
- communication patterns
- composite relationship-being
- friction loops
- repair paths
- biographical activation

Avoid:
- good match / bad match
- doomed
- meant to be as a verdict
- deterministic claims
- trauma prediction
- moralizing difficult signatures

## Next Engineering Tasks

### 1. Debug and strengthen calculation core
- Confirm Swiss Ephemeris house outputs.
- Confirm Whole Sign behavior.
- Confirm Ascendant and MC against known charts.
- Add real validation fixtures.

### 2. Expand relationship pattern detection
Add detectors for:
- Sun / Moon contacts
- Mercury / Mercury contacts
- Venus / Pluto
- Mars / Pluto
- Moon / Moon
- Moon / Venus
- Moon / Mars
- Saturn / Venus
- Saturn / Mars
- nodal contacts
- angle contacts beyond Venus / Ascendant
- composite Venus / Mars
- composite Venus / Saturn
- composite Sun / Saturn
- composite stelliums
- composite T-squares

### 3. Add house overlays
Once houses are validated, implement overlay detection:
- A planets in B houses
- B planets in A houses
- emphasize 1st, 4th, 5th, 6th, 7th, 8th, 10th, 12th

### 4. Move report toward target structure
Use `docs/report-structure.md` as the target.

### 5. Add relationship type weighting
Use `RelationshipContext.relationship_type` to prioritize patterns differently for romance, family, friendship, collaboration, etc.

## Non-Goals Right Now

- No polished web UI yet.
- No iOS app.
- No geocoding API yet.
- No payments or accounts.
- No LLM dependency until deterministic pipeline is stable.

## Engineering Principle

Keep calculation deterministic. Let interpretation consume structured chart and pattern data. Do not have the report generator reason directly from raw ephemeris data.
