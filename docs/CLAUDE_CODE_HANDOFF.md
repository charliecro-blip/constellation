# Claude Code Master Handoff — Constellation

_Last updated: 2026-06-23_

This is the single high-level handoff for continuing Constellation in Claude Code without needing prior chat context.

Read this with:

- `CLAUDE.md`
- `README.md`
- `docs/PROJECT_STATUS.md`
- `docs/astrology_doctrine/README.md`
- any doctrine doc relevant to the current task

## Project identity

Constellation is a relational astrology application for generating non-scored Relationship Maps from natal charts, synastry, house overlays, composite charts, and structured relationship context.

It is not a compatibility-score app. It should not tell users whether a relationship is good, bad, doomed, fated, destined, or meant to be.

Its core task is to map relational patterns:

- what is activated between two people
- what repeats across a user's relational field
- what needs attention
- what repair or practice may help

## Absolute guardrails

Never add user-facing:

- compatibility scores
- match percentages
- soulmate / twin flame language
- fate / destiny / meant-to-be claims
- good/bad relationship verdicts
- toxic / doomed labels
- deterministic advice about whether to continue a relationship

The product voice should be:

- psychologically precise
- non-fatalistic
- agency-preserving
- intimate but not melodramatic
- concrete rather than cookbook-generic

## Architecture principle

Deterministic astrology is the source of truth.

AI enhancement may polish or synthesize prose from deterministic inputs, but it must not:

- calculate astrology
- invent placements
- invent aspects
- invent houses
- invent asteroid contacts
- invent timing/transit claims
- change ranked priorities
- add doctrine that is not present in deterministic data

Prefer structured data over markdown parsing.

## Current implemented systems

The repo now includes:

- FastAPI backend and browser prototype.
- Saved relationship creation, editing, regeneration, deletion, and latest-map flow.
- Tester feedback persistence and UI.
- Onboarding and empty states.
- Pattern registry and scoring weights.
- Convergence weighting.
- Lead-eligible report openings.
- Natalized synastry.
- House-overlay and angle-contact visibility improvements.
- Composite sequencing/depth improvements.
- Chart-specific repair principles.
- Dynamic `Read more` explanations.
- Element/modality temperament weaving.
- Asteroid gating.
- AI synthesis packets.
- Persisted motifs for Constellation Patterns.
- Report diagnostics.
- Golden report QA fixtures.
- Astrology doctrine docs in `docs/astrology_doctrine/`.

## Important modules

- `packages/astro-core/constellation_core/chart.py` — chart calculation.
- `packages/astro-core/constellation_core/relationship.py` — synastry/composite relationship calculations.
- `packages/astro-core/constellation_core/patterns.py` — pattern detection.
- `packages/astro-core/constellation_core/pattern_registry.py` — pattern categories, tiers, lead eligibility.
- `packages/astro-core/constellation_core/scoring_weights.py` — scoring constants.
- `packages/astro-core/constellation_core/weighting.py` — pattern weighting/ranking/convergence.
- `packages/astro-core/constellation_core/report.py` — report construction, dynamic details, diagnostics, synthesis packet.
- `packages/astro-core/constellation_core/ai_enhancement.py` — AI prose enhancement guardrails.
- `packages/astro-core/constellation_core/asteroid_policy.py` — asteroid surfacing rules.
- `packages/astro-core/constellation_core/temperament.py` — element/modality summaries.
- `packages/astro-core/constellation_core/motifs.py` — persisted motif extraction.
- `packages/astro-core/constellation_core/api.py` — backend endpoints.
- `packages/astro-core/constellation_core/static/` — prototype UI.

## Current state of research/doctrine

Earlier Cowork research produced 9 foundational doctrine documents covering:

- synastry weighting
- pattern taxonomy
- report prioritization
- composite doctrine
- asteroid policy
- report voice
- codebase review
- architecture suggestions
- MVP roadmap

Most of that roadmap has now been implemented.

A second Cowork research pass identified the next underdeveloped doctrine areas:

1. Relationship-house rulership significators.
2. House overlay doctrine.
3. Composite configurations.
4. Similarity/difference analysis.
5. Pattern-specific repair principles.
6. Timing/love-planning ideas for later only.

The highest-priority next implementation task is relationship-house rulership significators.

## Current next implementation task

Add a deterministic relationship-house rulership layer.

### Goal

Identify when one person activates another person's core relationship houses through rulers of the 5th, 7th, 8th, and Ascendant/Descendant axis.

This should deepen report priority, dynamic details, diagnostics, synthesis packets, and selected prose.

### Use traditional sign rulers for MVP

```python
TRADITIONAL_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}
```

Do not add optional modern co-rulers yet.

Do not implement composite chart rulerships.

### Rulerships to calculate for each natal chart

Only when reliable house/angle data exists:

- Ascendant sign and ruler.
- Descendant / 7th-house sign and ruler.
- 5th-house sign and ruler.
- 8th-house sign and ruler.

For each ruler, capture its natal placement if available:

- planet
- sign
- house
- degree if already available

If house data is unavailable, skip the rulership layer gracefully.

### Inter-chart activations to detect

Detect:

- Person A planet to Person B 5th ruler.
- Person A planet to Person B 7th ruler.
- Person A planet to Person B 8th ruler.
- Person A planet to Person B Ascendant ruler.
- Person A 7th ruler to Person B 7th ruler.
- reciprocal 7th-ruler contacts.
- reciprocal Asc/Desc ruler mirroring where applicable.

Use existing aspect detection where possible.

### Conservative weighting principles

Rulership is a context multiplier, not a replacement for base aspect scoring.

Suggested initial boosts:

- 5th-ruler contact: romance-axis boost, about x1.1 to x1.2.
- 7th-ruler contact: partnership-axis boost, about x1.15 to x1.25.
- reciprocal 7th-ruler contact: additional modest boost.
- reciprocal Asc/Desc ruler mirroring: stronger mirror-recognition boost.
- 8th-ruler contact: vulnerability/trust-axis boost, about x1.1.

Be conservative. Do not let ruler contacts automatically override tighter Tier 1 synastry unless convergence supports them.

### Interpretive meanings

5th ruler: romance, play, pleasure, flirtation, creative eros, desire-expression faculty.

7th ruler: partnership faculty, partner recognition, commitment relevance, archetype of the other.

8th ruler: vulnerability, trust, guarded interior, exposure, psychological access, transformation. Do not default to sex.

Ascendant ruler: identity, self-direction, embodiment, how the person enters life.

### House overlay doctrine to refine alongside rulerships

Use these overlay meanings:

- 5th house: play, romance, pleasure, flirtation, creative eros.
- 7th house: partner recognition, mirroring, “you carry something I look for.”
- 8th house: guarded interior, trust, exposure, vulnerability, psychological access.
- 1st house: physical/personality immediacy, direct impact.
- 4th house: roots, home, private/family feeling.
- 12th house: unconscious/subtle draw; use cautiously.

House person generally feels the overlay more than the planet person.

Detect reciprocal overlays separately. Reciprocal 7th-house or romantic-house overlays deserve stronger language than one-directional overlays.

### Dynamic detail integration

When a dynamic involves a relationship-house ruler, `Read more` detail should be able to say so.

Examples of desired logic:

- This is not just Venus contacting Mercury; Mercury rules Ellis's 5th house, so Charlie's Venus is touching Ellis's romance/play faculty.
- This is not just Moon contacting Saturn; Saturn rules Charlie's Descendant, so Ellis's Moon touches one of Charlie's partnership significators.
- This 8th-ruler contact speaks less to generic intensity and more to trust, exposure, and the guarded parts of the self.

Do not hardcode these examples. Build deterministic support and concise phrasing.

### Diagnostics and synthesis packet

Diagnostics should include:

- Person A 5th/7th/8th rulers.
- Person B 5th/7th/8th rulers.
- detected cross-ruler contacts.
- detected reciprocal ruler contacts.
- reciprocal romantic-house overlays.

Synthesis packet should include only selected high-priority rulership notes, not a full technical dump.

### Report integration

Rulership material may appear in:

- Relationship Profiles.
- How A Activates B.
- How B Activates A.
- Read More dynamic details.
- Overview only if it is one of the strongest organizing principles.

Do not create a standalone “Rulerships” section by default.

## What not to implement now

Do not implement:

- timing/love-planning/Venus-hour features.
- transit-based relationship forecasting.
- composite chart rulerships.
- minor synastry aspects beyond the existing intended set.
- Davison relocation chart.
- compatibility scores.
- public sharing/social features.
- billing/subscriptions.
- raw source PDF ingestion into runtime.

## Knowledge-base workflow

Book PDFs and source material should stay in research/Cowork space unless converted into short, copyright-safe source cards.

Do not paste long copyrighted source text into repo docs.

Workflow:

1. Extract short paraphrased source notes.
2. Preserve bibliographic metadata.
3. Distinguish source claims from synthesis.
4. Propose doctrine changes separately.
5. Human review.
6. Add concise doctrine docs.
7. Implement in code with tests.

## Required tests before finishing a code task

Run:

```bash
node -c packages/astro-core/constellation_core/static/app.js

PYTHONPATH=packages/astro-core pytest tests/test_ui_content.py tests/test_report.py tests/test_patterns.py tests/test_api.py tests/test_weighting.py tests/test_persistence_api.py tests/test_golden_report_cases.py -q

PYTHONPATH=packages/astro-core python -m ruff check packages/astro-core/constellation_core tests

git diff --check
```

If the task touches report priority, add or update golden fixtures or regression tests.

If the task touches persistence/API, include persistence/API tests.

## Suggested tests for rulership pass

Add tests for:

- traditional rulership map.
- 5th, 7th, and 8th rulers calculated when house data exists.
- rulership layer skipped when birth time/house data missing.
- 5th-ruler contact detected.
- 7th-ruler contact detected.
- reciprocal 7th-ruler contact detected.
- 8th-ruler contact detected.
- ruler contacts affect weighting conservatively.
- dynamic detail mentions relationship-ruler context when relevant.
- diagnostics include relationship-ruler summary.
- synthesis packet includes selected ruler activation only when high-priority.
- 5th overlay references play/pleasure, not generic compatibility.
- 7th overlay distinguishes one-directional vs reciprocal.
- 8th overlay references trust/exposure, not default eroticism.
- no composite chart rulerships.
- no compatibility score.
- no soulmate/twin flame/fated/destined/meant-to-be language.

## Suggested docs to add/update

Add:

```text
docs/astrology_doctrine/relationship_rulerships.md
```

Include:

- traditional ruler map.
- 5th ruler meaning.
- 7th ruler meaning.
- 8th ruler meaning.
- how ruler contacts act as context multipliers.
- why composite rulerships are excluded.
- how house overlays differ from aspects.

## Suggested PR title

Add relationship house rulership significators

## Working principle

Notion is the workshop. GitHub is the build system. Doctrine becomes code only after it is clarified, reviewed, and testable.
