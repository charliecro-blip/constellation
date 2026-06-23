# Claude Code Handoff — Relationship House Rulership Significators

## What this is

An astrology-depth pass for the Constellation app (`charliecro-blip/constellation`, main branch). Add a deterministic relationship-house rulership layer: detect when one person's planets aspect another person's 5th, 7th, or 8th house ruler, and apply context multipliers to the scoring weights. Also refine house overlay doctrine and add Read More detail for ruler contacts.

This is backend only — no UI changes, no API shape changes.

---

## Before you start — read these files

```
packages/astro-core/constellation_core/schemas.py
packages/astro-core/constellation_core/patterns.py
packages/astro-core/constellation_core/weighting.py
packages/astro-core/constellation_core/scoring_weights.py
packages/astro-core/constellation_core/report.py
docs/astrology_doctrine/report_prioritization.md
docs/astrology_doctrine/synastry_weighting.md
```

Key schema facts (so you don't have to infer):
- `Chart.angles` is `dict[str, Angle]` — keys are lowercase `"ascendant"` / `"midheaven"`
- `Angle.sign` is title-case, e.g. `"Libra"`
- `Chart.houses` is `HouseCusps | None` — `cusps` is `dict[int, float]` (longitude per cusp)
- `BirthData.time_known: bool` — use this to gate the rulership layer, not just presence of `time`
- `Placement.sign` and all sign names elsewhere are title-case
- Ruler planet names in `patterns.py` are lowercase (`"venus"`, `"mars"` etc.)
- Existing `synastry_aspects` in `RelationshipCalculation` are pre-filtered to standard orbs — use them for ruler-contact detection rather than recomputing aspect distances
- `zodiac.py` likely has a longitude-to-sign helper — check before writing your own

---

## Task 1 — Create `rulerships.py`

File: `packages/astro-core/constellation_core/rulerships.py`

### Traditional ruler map (MVP — no modern co-rulers yet)

```python
TRADITIONAL_RULERS: dict[str, str] = {
    "Aries": "mars",
    "Taurus": "venus",
    "Gemini": "mercury",
    "Cancer": "moon",
    "Leo": "sun",
    "Virgo": "mercury",
    "Libra": "venus",
    "Scorpio": "mars",
    "Sagittarius": "jupiter",
    "Capricorn": "saturn",
    "Aquarius": "saturn",
    "Pisces": "jupiter",
}
```

### Significator dataclass / model

```python
@dataclass
class RelationshipSignificators:
    has_houses: bool           # False = birth time unknown; skip all ruler logic
    asc_sign: str | None
    asc_ruler: str | None      # lowercase planet name
    desc_sign: str | None
    desc_ruler: str | None
    fifth_sign: str | None
    fifth_ruler: str | None
    seventh_sign: str | None
    seventh_ruler: str | None
    eighth_sign: str | None
    eighth_ruler: str | None
```

### Builder function

```python
def get_significators(chart: Chart) -> RelationshipSignificators:
    ...
```

- Gate on `chart.birth.time_known` AND `chart.angles` being non-empty AND `chart.houses` being non-None
- If any gate fails → return `RelationshipSignificators(has_houses=False, ...all None)`
- Ascendant sign: `chart.angles["ascendant"].sign`
- Descendant sign: opposite sign of Ascendant
- 5th, 7th, 8th house cusp signs: convert `chart.houses.cusps[N]` longitude to sign (check `zodiac.py`)
- Rulers: look up each sign in `TRADITIONAL_RULERS`

Do not store anything on `RelationshipCalculation` schema — calculate inline.

---

## Task 2 — Ruler-contact detection in `patterns.py`

Add a new detection function:

```python
def detect_ruler_contact_patterns(
    relationship: RelationshipCalculation,
    sig_a: RelationshipSignificators,
    sig_b: RelationshipSignificators,
) -> list[Pattern]:
```

Detect these contacts using the existing `relationship.synastry_aspects` list:

| Contact | Category | Axis label |
|---|---|---|
| Person A planet aspects Person B's 5th ruler | `romance_axis_contact` | `ruler_5th` |
| Person A planet aspects Person B's 7th ruler | `partnership_axis_contact` | `ruler_7th` |
| Person A planet aspects Person B's 8th ruler | `vulnerability_axis_contact` | `ruler_8th` |
| Person A planet aspects Person B's Asc ruler | `identity_axis_contact` | `ruler_asc` |
| Both directions of any of the above | flag as `reciprocal=True` on the pattern |

Pattern keys: `synastry.ruler_contact.5th`, `synastry.ruler_contact.7th`, `synastry.ruler_contact.8th`, `synastry.ruler_contact.asc`

Base priorities (before orb bonus):
- 5th ruler contact: 68
- 7th ruler contact: 72
- 8th ruler contact: 66
- Asc ruler contact: 64

Add a `ruler_axis` field to `Pattern` if needed, or store axis info in `evidence`.

Reciprocal Asc/Desc ruler swap (Ruiz pattern): detect if `sig_a.asc_ruler == sig_b.desc_ruler` AND `sig_b.asc_ruler == sig_a.desc_ruler`. If both directions match, create a high-priority pattern (`mirror_recognition`, priority 82).

Wire `detect_ruler_contact_patterns` into `detect_relationship_patterns` at the bottom of `patterns.py`, only when `sig_a.has_houses` and `sig_b.has_houses`.

---

## Task 3 — Weighting multipliers in `weighting.py`

Add ruler-contact boosts to `weight_patterns`. These are multipliers applied on top of base priority, not replacements:

```python
RULER_CONTACT_BOOSTS = {
    "romance_axis_contact": 10,       # 5th ruler
    "partnership_axis_contact": 14,   # 7th ruler
    "vulnerability_axis_contact": 8,  # 8th ruler
    "identity_axis_contact": 6,       # Asc ruler
    "mirror_recognition": 20,         # reciprocal Asc/Desc swap
}
```

Do not let ruler contacts override a tighter Tier 1 synastry pattern. Cap total priority at 100. The ruler layer is a signal amplifier, not a lead generator on its own.

Also add overlay weighting refinements — split the existing `house_overlay` tier-down into house-specific values:

```python
ROMANTIC_OVERLAY_HOUSES = {1, 5, 7, 8}
NON_ROMANTIC_OVERLAY_PENALTY = -18   # 2nd, 3rd, 6th, 9th, 10th, 11th
ROMANTIC_OVERLAY_PENALTY = -10       # 1st, 5th, 7th, 8th (still down from aspects, but less so)
```

Apply these in `weight_patterns` where house overlays are currently penalized with a flat `-14`.

---

## Task 4 — Read More detail for ruler contacts

When a pattern is a ruler-contact pattern, the dynamic Read More expansion should include the ruler context. Find where dynamic detail is built (likely in `report.py` or `interpretations.py`) and add a branch:

If `pattern.key` starts with `synastry.ruler_contact`:
- Extract the axis (`5th`, `7th`, `8th`, `asc`) from pattern key or evidence
- Add a sentence explaining why this contact matters beyond the raw aspect

Example logic (do not hardcode exact prose — use template strings):

```python
RULER_AXIS_CONTEXT = {
    "5th": (
        "{planet_a} isn't just contacting {planet_b} — {planet_b} rules {name_b}'s 5th house, "
        "so {name_a}'s {planet_a} is touching {name_b}'s romance and pleasure faculty directly."
    ),
    "7th": (
        "{planet_b} rules {name_b}'s 7th house — the partnership axis. "
        "This contact isn't just {planet_a}/{planet_b} energy; it reaches {name_b}'s partner-recognition circuit."
    ),
    "8th": (
        "{planet_b} rules {name_b}'s 8th house. This contact speaks less to intensity in general "
        "and more to trust, exposure, and access to the guarded interior."
    ),
    "asc": (
        "{planet_b} rules {name_b}'s Ascendant — how they project and identify. "
        "This contact has an immediate personal quality beyond what the aspect alone suggests."
    ),
}
```

---

## Task 5 — Diagnostics and synthesis packet

In diagnostics output (wherever `diagnostics` dict is built):

```python
"relationship_significators": {
    "person_a": {
        "has_houses": sig_a.has_houses,
        "asc_ruler": sig_a.asc_ruler,
        "fifth_ruler": sig_a.fifth_ruler,
        "seventh_ruler": sig_a.seventh_ruler,
        "eighth_ruler": sig_a.eighth_ruler,
    },
    "person_b": { ... same ... },
    "ruler_contacts_detected": [p.key for p in ruler_patterns],
    "reciprocal_contacts": [p.key for p in ruler_patterns if "reciprocal" in p.id],
}
```

Synthesis packet: include ruler-contact patterns only when their final weighted priority >= 70 (same threshold as other synthesis packet entries). Do not dump the full significator table into the synthesis packet.

---

## Task 6 — Doctrine doc

Create: `docs/astrology_doctrine/relationship_rulerships.md`

Include:
- Traditional ruler map (the dict above)
- 5th ruler meaning: romance/play/desire-expression faculty; contacts describe how a partner activates flirtation, enjoyment, creative eros, dating chemistry
- 7th ruler meaning: partnership faculty; contacts describe partner-recognition and commitment relevance
- 8th ruler meaning: vulnerability/trust/exposure faculty; contacts are about access to guarded interior material, NOT default eroticism
- How ruler contacts act as context multipliers (not replacements)
- Why composite sign rulerships are excluded (Hand: sign behavior in composite is unreliable; house positions and aspects are reliable)
- How house overlays differ from aspects: overlays describe where someone lands in your life; aspects describe direct energy exchange. Overlay = ambient/situational; aspect = dynamic/active. The house person feels the overlay more than the planet person.

---

## Task 7 — Tests

Add tests covering:

**rulerships.py:**
- Traditional ruler map has all 12 signs
- `get_significators` returns `has_houses=False` when `time_known=False`
- `get_significators` returns `has_houses=False` when `chart.houses is None`
- `get_significators` returns correct 5th, 7th, 8th rulers for a known chart (pick a chart where cusps are unambiguous)
- Opposite sign logic for Descendant is correct (e.g., Aries Asc → Libra Desc, ruler = Venus)

**patterns.py / ruler contact detection:**
- 5th-ruler contact detected when person A's Venus aspects person B's Mercury and Mercury rules person B's 5th
- 7th-ruler contact detected and categorized as `partnership_axis_contact`
- 8th-ruler contact detected and categorized as `vulnerability_axis_contact`
- Reciprocal 7th-ruler contact flagged as reciprocal
- Asc/Desc ruler swap (both directions) detected as `mirror_recognition`
- No ruler patterns emitted when `has_houses=False` for either person

**weighting.py:**
- 7th-ruler contact pattern gets partnership boost applied
- Final priority capped at 100
- Romantic-house overlays (5th, 7th, 8th) penalized less than non-romantic overlays

**report / Read More:**
- Dynamic detail for a `synastry.ruler_contact.7th` pattern mentions the 7th house axis
- Dynamic detail for a `synastry.ruler_contact.8th` pattern references trust/exposure, not generic intensity
- Dynamic detail for a `synastry.ruler_contact.5th` pattern references romance/play faculty

**Doctrine guardrails (regression tests):**
- No composite chart rulerships generated from any composite pattern
- No "compatibility score" or percentage in any report output
- No soulmate/twin flame/fated/destined/meant-to-be language in ruler-contact report sections

---

## Task 8 — Run and verify

```bash
# JS syntax check
node -c packages/astro-core/constellation_core/static/app.js

# Full test suite
PYTHONPATH=packages/astro-core pytest tests/test_ui_content.py tests/test_report.py tests/test_patterns.py tests/test_api.py tests/test_weighting.py tests/test_persistence_api.py tests/test_golden_report_cases.py -q

# Lint
PYTHONPATH=packages/astro-core python -m ruff check packages/astro-core/constellation_core tests

# Whitespace/merge check
git diff --check
```

All tests must pass. No new ruff violations. No new golden fixture diffs unless the change is intentional and the fixture is updated with a clear comment.

---

## What not to do

- Do not modify `RelationshipCalculation` schema (no new fields)
- Do not add composite sign rulerships — Hand explicitly flags composite sign behavior as unreliable
- Do not add modern co-rulers (Uranus for Aquarius, Neptune for Pisces, Pluto for Scorpio) — traditional only for MVP
- Do not create a standalone "Rulerships" report section — ruler material belongs in existing sections (Profiles, How A Activates B, Read More)
- Do not add compatibility scores or percentage outputs
- Do not use fate/destiny/soulmate language in any ruler-contact prose

---

## Suggested PR title

`Add relationship house rulership significators`
