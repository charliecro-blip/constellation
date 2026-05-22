# Constellation

A relational astrology MVP for generating non-scored Relationship Field Maps from natal charts, synastry, and composite charts.

## Current Build Target

The current prototype is a calculation-first pipeline:

1. Accept birth date, local birth time, latitude, longitude, and timezone.
2. Calculate natal placements, Ascendant, MC, and houses when birth time is known.
3. Calculate synastry aspects, house overlays, and midpoint composite placements.
4. Detect and weight relationship patterns.
5. Generate a draft Markdown Relationship Field Map.
6. Expose the pipeline through CLI commands, a minimal FastAPI app, and a browser prototype UI.

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
python -m constellation_core.relationship_cli --person-a data/fixtures/example_person_a_birth.json --person-b data/fixtures/example_person_b_birth.json --house-system whole_sign --output data/sample-output/relationship.json
```

Generate ranked patterns:

```bash
python -m constellation_core.patterns_cli --person-a data/fixtures/example_person_a_birth.json --person-b data/fixtures/example_person_b_birth.json --house-system whole_sign
```

Generate a draft Markdown Relationship Field Map:

```bash
python -m constellation_core.report_cli --person-a data/fixtures/example_person_a_birth.json --person-b data/fixtures/example_person_b_birth.json --context data/fixtures/example_romantic_context.json --house-system whole_sign --output data/sample-output/report.md
```

Validate a known chart fixture:

```bash
python -m constellation_core.validate_fixture_cli data/fixtures/my_validation_fixture.json --house-system whole_sign
```

## API and Browser Prototype

Run the local API:

```bash
uvicorn constellation_core.api:app --reload
```

Then open the browser prototype:

```text
http://127.0.0.1:8000/
```

Or open the API docs:

```text
http://127.0.0.1:8000/docs
```

Available endpoints:

- `GET /`
- `GET /health`
- `POST /chart`
- `POST /relationship`
- `POST /report`

## Deployment

The repo includes a Render blueprint in `render.yaml`.

Suggested first web deployment:

1. Connect this GitHub repository to Render.
2. Create a new Blueprint or Web Service from `render.yaml`.
3. Use the default build and start commands from the blueprint.
4. Deploy.
5. Open the generated Render URL on desktop and mobile.

The deployed prototype will show a JSON editor and Markdown report output. It is intentionally internal/tester-grade, not the final product UI.

## Near-Term Roadmap

- Validate calculations against trusted chart software.
- Add real validation fixtures.
- Add more pattern detectors and interpretation blocks.
- Add geocoding and historical timezone lookup.
- Improve the browser UI from JSON editor to form-based input.

## Working Principle

Notion is the workshop. GitHub is the build system.
