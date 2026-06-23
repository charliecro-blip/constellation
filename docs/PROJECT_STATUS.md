# Constellation Project Status

_Last updated: 2026-06-23_

## High-level overview

Constellation is a relational astrology application for generating non-scored Relationship Maps from natal charts, synastry, house overlays, composite charts, and structured relationship context.

The product is not a compatibility-score app and should not tell users whether a relationship is good, bad, doomed, fated, or meant to be. Its core job is to map relational patterns: what is activated between two people, what repeats across a user's relational field, what needs attention, and what repair or practice may help.

The current product spine is:

1. Calculate natal charts with houses and angles.
2. Calculate synastry aspects, house overlays, angular contacts, composite placements, and selected pattern signatures.
3. Rank and filter the patterns using deterministic doctrine.
4. Generate a Relationship Map with a coherent narrative, repair guidance, chart check, diagnostics, and optional AI-polished prose.
5. Save relationships and persist compact motifs so Constellation Patterns can aggregate what repeats across multiple saved maps.
6. Collect tester feedback on generated maps.

## Current build state

The app is now beyond the first raw prototype. It has the beginning of a real product architecture:

- FastAPI backend and browser prototype.
- Saved relationship creation, editing, regeneration, deletion, and latest-map flow.
- Placidus as the default intended house system.
- Deterministic report generation with optional AI enhancement.
- Pattern registry, scoring weights, convergence logic, and lead-eligible report opening rules.
- Report composition improvements so the reading starts from a broader relational field rather than a single harsh aspect.
- Natalized synastry: aspects can refer to sign, house, and the role of each planet in each person's chart.
- Expanded dynamic explanations behind `Read more` controls.
- Element/modality temperament weaving in profiles, dynamic details, diagnostics, and synthesis packets.
- Asteroid gating: default reports allow Juno, Chiron, Ceres, and optionally Vesta, while Eros/Psyche/Lilith/Vertex and asteroid-to-asteroid contacts remain suppressed from default reports.
- Synthesis packets that carry deterministic priorities into the AI enhancement layer.
- Persisted motifs for Constellation Patterns, so recurring relational patterns are aggregated structurally rather than by parsing report prose.
- Report diagnostics for ranking, motifs, temperament, chart sanity, synthesis packet, and suppressed/surfaced material.
- Golden QA fixtures that protect major report-priority assumptions.
- Tester feedback persistence and UI.
- Onboarding and empty-state copy for first-time testers.
- Doctrine docs in `docs/astrology_doctrine/`.

## Recent development milestones

Recent merged PRs include:

- #41 — Clean up saved relationship management.
- #42 — Add tester feedback for Relationship Maps.
- #43 — Improve report composition and natalized synastry.
- #45 — Add onboarding and empty states from latest main.
- #46 — Add expandable dynamic explanations.
- #47 — Add element and modality temperament weaving.

Earlier foundational PRs added pattern registry/scoring, convergence weighting, lead-eligible openings, asteroid gating, synthesis packets, persisted motifs, diagnostics, doctrine docs, and golden report QA fixtures.

## Current product strengths

Constellation now has a serious interpretive infrastructure:

- Deterministic astrology remains the source of truth.
- The AI layer is constrained to prose synthesis and must not invent astrology.
- The report engine can prioritize patterns, suppress weak/noisy material, and expose diagnostics.
- The product has a clear doctrine: no scores, no fate claims, no soulmate framing, no generic AI filler.
- Saved maps now feed a higher-level Constellation Patterns view.
- Reports can now support deeper explanations without making the main report overly dense.

## Known current gap

The app should now be tested with real examples. The most important next question is not whether more infrastructure can be added, but whether the generated Relationship Map feels like a strong astrologer wrote it.

Specifically inspect:

- Does the Overview open on the true relational field, including sweetness, attraction, play, or recognition when present?
- Are hard composite aspects contextualized instead of over-weighted?
- Are house overlays and angle contacts, especially 5th/7th/8th and Ascendant/Descendant contacts, visible enough?
- Does synastry feel chart-specific rather than generic planet cookbook text?
- Do `Read more` details deepen rather than clutter?
- Does temperament language clarify actual dynamics rather than become filler?
- Are repair principles specific to the chart signatures?
- Does the AI enhancer preserve deterministic priorities?

## Immediate recommended next build layer

The next astrology-depth pass should be relationship-house rulership significators:

- Ascendant ruler.
- Descendant / 7th-house ruler.
- 5th-house ruler.
- 8th-house ruler.
- Contacts to those rulers from the other person's planets.
- Relationship-ruler activations in dynamic details, diagnostics, synthesis packets, and report priority.

This should be a compact depth layer, not a full traditional astrology treatise. It should help explain why a contact matters to a particular person's relationship pattern.

## Knowledge base status

Claude-generated doctrine files have already been partially translated into code and repo docs. The repo docs in `docs/astrology_doctrine/` should now be treated as the implementation-facing source of truth.

The next knowledge-base expansion will come from book PDFs and other source material. Those should not be dumped into the repo as raw text. Instead, use a source-extraction workflow:

1. Ingest source PDFs privately in Claude/Cowork or a research workspace.
2. Extract short, copyright-safe notes, not long excerpts.
3. Create source cards with bibliographic metadata and short paraphrased insights.
4. Propose doctrine additions or revisions.
5. Translate accepted doctrine into concise repo docs.
6. Only then update code modules, tests, and prompts.

Recommended knowledge-base artifacts:

- `docs/astrology_doctrine/source_notes/` for short source cards if kept in repo.
- `docs/astrology_doctrine/doctrine_proposals/` for proposed changes before implementation.
- Updates to existing doctrine docs only after review.
- No long copyrighted passages.

## Claude Code / Claude Cowork workflow

Claude Code is well-suited for codebase-aware development: it can read the project, edit files, run commands, write tests, and create commits or PRs. Use `CLAUDE.md` or a comparable project instruction file to keep its behavior aligned with the Constellation doctrine.

Recommended Claude workflow:

1. Pull latest `main`.
2. Read `README.md`, `docs/PROJECT_STATUS.md`, and `docs/astrology_doctrine/README.md`.
3. Read the specific module docs relevant to the task.
4. Ask Claude to make a plan before editing.
5. Keep each task narrow.
6. Require tests and lint before PR.
7. Review any changes that alter astrology doctrine, ranking, report prose, or AI prompts.
8. Prefer deterministic data structures over prose parsing.

Claude/Cowork is especially useful for:

- Sorting source PDFs into concise doctrine notes.
- Auditing report outputs against doctrine.
- Improving interpretive prose within guardrails.
- Writing tests for known regressions.
- Adding focused backend or frontend changes.

## Shipper.now / external app-builder workflow

Shipper or similar app-building infrastructure tools may be useful for moving Constellation from prototype to product surface, especially around deployment, authentication, database-backed accounts, polished UI, billing, or infrastructure scaffolding.

Recommended Shipper workflow:

1. Do not ask it to invent astrology logic.
2. Treat the existing repo as the source of truth for calculations, report generation, and doctrine.
3. Use Shipper for product infrastructure and UI shell work:
   - auth
   - accounts
   - saved maps dashboard
   - deployment
   - database management
   - responsive layouts
   - feedback/admin views
   - maybe subscriptions later
4. Keep the astrology engine in `packages/astro-core/constellation_core` unless there is a deliberate architecture migration.
5. Require API boundary preservation: Shipper should call backend endpoints rather than replacing the report engine.
6. Review generated code carefully before merging.

Good Shipper candidate tasks:

- Build a polished account/dashboard shell.
- Build a mobile-friendly saved relationships interface.
- Improve landing page and onboarding UX.
- Add admin/tester feedback dashboards.
- Connect deployment/database/auth plumbing.

Poor Shipper candidate tasks:

- Rewrite astrology ranking.
- Create new interpretive doctrine.
- Parse source PDFs into doctrine without human review.
- Replace deterministic calculations with AI-generated astrology.

## Practical next process

### Short term

1. Finish/merge the relationship-house rulership pass.
2. Generate 1–2 real reports.
3. Inspect diagnostics, synthesis packet, dynamic details, temperament, and report prose.
4. Capture issues as test fixtures or narrow PRs.

### Knowledge-base track

1. Put PDFs into Claude/Cowork research workspace.
2. Ask for source cards, not code.
3. Review source-card insights manually.
4. Promote accepted ideas into `docs/astrology_doctrine/`.
5. Only then create code tasks.

### Infrastructure track

1. Use Shipper or another app-builder for shell/product infrastructure.
2. Keep the astrology core intact.
3. Work through API boundaries.
4. Build authentication/dashboard/admin/deployment only after the report engine is trustworthy.

## Development guardrails

- No compatibility scores.
- No fate, destiny, soulmate, or twin-flame framing.
- No deterministic claims about whether a relationship should continue.
- No AI-invented astrology.
- No raw copyrighted source dumps in repo docs.
- Prefer ranked structured data over markdown parsing.
- Prefer diagnostics and tests over vibes-only QA.

## Working principle

Notion is the workshop. GitHub is the build system. The astrology doctrine should become code only after it has been clarified, reviewed, and made testable.