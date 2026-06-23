# Claude Code Instructions for Constellation

Read this before making changes.

## Project identity

Constellation is a relational astrology app for generating non-scored Relationship Maps from natal charts, synastry, house overlays, composite charts, and relationship context.

It is not a compatibility-score app. It should never imply that astrology decides whether a relationship is good, bad, doomed, fated, destined, or meant to be.

The product voice is psychologically precise, non-fatalistic, and agency-preserving.

## Required orientation files

Before planning a task, read:

1. `README.md`
2. `docs/PROJECT_STATUS.md`
3. `docs/astrology_doctrine/README.md`
4. Any doctrine doc relevant to the task.

## Core architecture principle

Deterministic astrology is the source of truth.

AI may polish or synthesize prose from deterministic inputs, but it must not:

- calculate astrology
- invent placements
- invent aspects
- invent houses
- invent asteroid contacts
- change ranked priorities
- add timing/transit claims unless deterministic timing data exists

Prefer structured data over markdown parsing.

## Report doctrine

Relationship Maps should:

- open with the broad relational field, not an isolated hard aspect
- include sweetness, attraction, play, recognition, and generativity when present
- contextualize friction and intensity
- interpret aspects in the context of each person's natal chart
- give house overlays and angle contacts proper weight
- use composite configurations as synthesis, not generic filler
- provide chart-specific repair guidance
- use `Read more` details for deeper technical/interwoven material

Avoid:

- compatibility score
- soulmate / twin flame
- fated / destined / meant to be
- toxic / doomed
- generic AI filler such as “navigate the complexities” or “unique entity”
- raw cookbook paragraphs

## Current major systems

The app currently includes:

- pattern registry and scoring weights
- convergence weighting
- lead-eligible report openings
- natalized synastry
- element/modality temperament weaving
- expandable dynamic explanations
- asteroid gating
- synthesis packets for AI enhancement
- persisted relationship motifs
- Constellation Patterns aggregation
- report diagnostics
- golden QA fixtures
- tester feedback
- saved relationship management

## Important modules

- `packages/astro-core/constellation_core/chart.py` — chart calculation
- `packages/astro-core/constellation_core/patterns.py` — pattern detection
- `packages/astro-core/constellation_core/pattern_registry.py` — categories, tiers, lead eligibility
- `packages/astro-core/constellation_core/scoring_weights.py` — weights, thresholds, suppression
- `packages/astro-core/constellation_core/weighting.py` — weighted ranking/convergence
- `packages/astro-core/constellation_core/report.py` — report construction, diagnostics, synthesis packets, dynamic details
- `packages/astro-core/constellation_core/ai_enhancement.py` — AI prompt and prose enhancement guardrails
- `packages/astro-core/constellation_core/asteroid_policy.py` — default asteroid surfacing rules
- `packages/astro-core/constellation_core/motifs.py` — persisted motifs for Constellation Patterns
- `packages/astro-core/constellation_core/temperament.py` — element/modality temperament summaries
- `packages/astro-core/constellation_core/static/app.js` — browser prototype behavior
- `packages/astro-core/constellation_core/static/index.html` — browser prototype structure
- `packages/astro-core/constellation_core/static/styles.css` — browser prototype styles

## Testing commands

Run these before finishing a code task:

```bash
node -c packages/astro-core/constellation_core/static/app.js

PYTHONPATH=packages/astro-core pytest tests/test_ui_content.py tests/test_report.py tests/test_patterns.py tests/test_api.py tests/test_weighting.py tests/test_persistence_api.py tests/test_golden_report_cases.py -q

PYTHONPATH=packages/astro-core python -m ruff check packages/astro-core/constellation_core tests

git diff --check
```

If the task touches persistence, feedback, or saved relationships, make sure persistence tests are included.

If the task touches report priority or interpretation, update or add golden report fixtures rather than relying only on exact prose assertions.

## Knowledge-base workflow

Do not paste long copyrighted source text into repo docs.

When working from book PDFs or source material:

1. Extract short paraphrased source notes.
2. Preserve bibliographic metadata.
3. Propose doctrine changes separately from code changes.
4. Only implement reviewed doctrine.
5. Add tests for any doctrine that changes ranking, surfacing, report composition, or AI prompt behavior.

## Good task shape

Good tasks are narrow, testable, and preserve existing architecture.

Examples:

- Add relationship-house rulership summaries to diagnostics.
- Add 7th-ruler activation weighting.
- Improve composite T-square dynamic details.
- Add source-card docs for a reviewed astrology text.
- Polish saved-relationship UI without changing report logic.

Avoid broad rewrites unless explicitly requested.

## Working principle

Notion is the workshop. GitHub is the build system. Doctrine becomes code only after it is clarified, reviewed, and testable.