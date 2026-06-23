# Constellation

Constellation is a relational astrology app for generating non-scored Relationship Maps from natal charts, synastry, house overlays, composite charts, and relationship context.

It is designed to map relational patterns, not decide whether a relationship is good, bad, fated, doomed, or compatible.

## Current Build Target

The current prototype is a calculation-first Relationship Map pipeline:

1. Accept birth date, local birth time, birthplace/location, timezone, and relationship context.
2. Calculate natal placements, Ascendant, MC, and houses when birth time is known.
3. Calculate synastry aspects, house overlays, angle contacts, midpoint composite placements, and selected relationship patterns.
4. Detect, weight, and rank relationship signatures using deterministic doctrine.
5. Generate a Relationship Map with overview, profiles, directional activation, composite field, friction/repair, chart check, dynamic details, and diagnostics.
6. Optionally pass deterministic markdown plus synthesis packet to AI enhancement for prose polish only.
7. Save relationships, regenerate maps, persist motifs, aggregate Constellation Patterns, and collect tester feedback.

## Product Doctrine

Constellation is not a compatibility-score app. It ranks relationship signatures to decide report narrative priority: what should be opened, developed, briefly noted, or omitted. A high-ranking signature is an editorial signal for the Relationship Map, not a verdict about whether a relationship is good, bad, fated, or doomed.

Astrology calculations remain deterministic. The calculation layer produces natal placements, synastry, overlays, composites, detected patterns, diagnostics, temperament summaries, dynamic details, and synthesis packets. Optional AI enhancement may rewrite or synthesize report prose from those deterministic inputs, but it must not calculate astrology, invent placements, add aspects, or change the underlying ranking.

Reports should be non-fatalistic, psychologically precise, and agency-preserving. The writing should name concrete relational dynamics, describe likely felt experience and shadow, and offer repair principles without implying certainty or removing choice.

The doctrine flows through:

- Pattern registry categories, tiers, and lead eligibility.
- Scoring weights, thresholds, and convergence constants.
- Context-aware convergence weighting and ranked pattern selection.
- Report opening rules that prioritize lead-eligible relationship themes.
- Natalized synastry and house/angle overlay visibility.
- Element/modality temperament weaving.
- Expanded dynamic explanations behind `Read more` controls.
- Voice and repair guidance for deterministic and AI-enhanced prose.
- Asteroid gating that keeps minor points supporting by default.
- Synthesis packets that carry deterministic priorities into AI enhancement.
- Motif persistence for compact recurring relationship themes.
- Diagnostics that expose ranked, surfaced, and suppressed report material.

See [docs/astrology_doctrine/](docs/astrology_doctrine/) for implementation-oriented doctrine and [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) for the current handoff/status overview.

## Claude / agent handoff

Claude Code and other coding agents should read [CLAUDE.md](CLAUDE.md) before making changes. That file contains project-specific guardrails, required orientation docs, important modules, and test commands.

## Setup

Install the package in editable mode with development dependencies, then run the tests.

```bash
python -m pip install --upgrade pip
pip install -e '.[dev]'
pytest -q
```

## CLI Usage

The chart CLI accepts birth data with latitude, longitude, timezone, and a house system.

```bash
python -m constellation_core.cli --name Example --date YYYY-MM-DD --time HH:MM --lat 0 --lon 0 --timezone UTC --house-system placidus
```

The relationship CLI accepts two birth-data JSON fixture files.

```bash
python -m constellation_core.relationship_cli --person-a data/fixtures/example_person_a_birth.json --person-b data/fixtures/example_person_b_birth.json --house-system placidus --output data/sample-output/relationship.json
```

Generate ranked patterns:

```bash
python -m constellation_core.patterns_cli --person-a data/fixtures/example_person_a_birth.json --person-b data/fixtures/example_person_b_birth.json --house-system placidus
```

Generate a draft Markdown Relationship Map:

```bash
python -m constellation_core.report_cli --person-a data/fixtures/example_person_a_birth.json --person-b data/fixtures/example_person_b_birth.json --context data/fixtures/example_romantic_context.json --house-system placidus --output data/sample-output/report.md
```

Validate a known chart fixture:

```bash
python -m constellation_core.validate_fixture_cli data/fixtures/my_validation_fixture.json --house-system placidus
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

Core endpoint families include:

- chart calculation
- relationship calculation
- report generation
- saved relationships
- saved relationship reports
- relationship motifs
- constellation patterns
- report feedback
- AI enhancement

## Deployment

The repo includes a Render blueprint in `render.yaml`.

Suggested first web deployment:

1. Connect this GitHub repository to Render.
2. Create a new Blueprint or Web Service from `render.yaml`.
3. Use the default build and start commands from the blueprint.
4. Deploy.
5. Open the generated Render URL on desktop and mobile.

The current deployment target is still internal/tester-grade. The report engine and saved-relationship workflows are more mature than the final product UI.

## Near-Term Roadmap

- Add relationship-house rulership significators: Ascendant ruler, 7th ruler, 5th ruler, 8th ruler, and cross-chart activations.
- Generate and inspect 1–2 real reports using diagnostics, dynamic details, and synthesis packets.
- Use tester feedback to identify report-quality regressions.
- Expand the astrology doctrine knowledge base through copyright-safe source cards and reviewed doctrine proposals.
- Consider Shipper or another app-builder for product infrastructure: auth, accounts, dashboard, deployment, billing, and admin views.
- Keep the astrology engine deterministic and protected behind API boundaries.

## Working Principle

Notion is the workshop. GitHub is the build system. Doctrine becomes code only after it is clarified, reviewed, and testable.