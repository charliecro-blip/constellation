# Constellation

A relational astrology MVP for generating non-scored Relationship Field Maps from natal charts, synastry, and composite charts.

## Current Build Target

Phase 0 is a calculation spike:

1. Accept birth date, local birth time, latitude, longitude, and timezone.
2. Calculate natal placements.
3. Calculate Ascendant, MC, and houses when birth time is known.
4. Output normalized JSON.
5. Validate against known chart examples before building interpretation.

## Product Doctrine

- No compatibility scores.
- No verdicts.
- No fatalism.
- Synastry describes mutual activation.
- Composite describes the relationship as its own living field.
- Strong contact is not the same as healthy contact.
- Every friction point should eventually produce a repair path.

## Setup

Install the package in editable mode with development dependencies, then run the tests.

```bash
python -m pip install --upgrade pip
pip install -e '.[dev]'
pytest -q
```

## CLI Usage

The Phase 0 CLI accepts birth data with latitude, longitude, and timezone directly. Place lookup comes later.

```bash
python -m constellation_core.cli --name Example --date YYYY-MM-DD --time HH:MM --lat 0 --lon 0 --timezone UTC --house-system whole_sign
```

The relationship CLI accepts two birth-data JSON fixture files.

```bash
python -m constellation_core.relationship_cli --person-a data/fixtures/person_a_birth.json --person-b data/fixtures/person_b_birth.json --house-system whole_sign --output data/sample-output/relationship.json
```

## Near-Term Roadmap

- Phase 0: chart calculation core.
- Phase 1: synastry and midpoint composite JSON.
- Phase 2: ranked signature detector.
- Phase 3: structured Relationship Field Map generator.
- Phase 4: minimal web UI.

## Working Principle

Notion is the workshop. GitHub is the build system.
