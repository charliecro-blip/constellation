# Relationship-House Rulership Significators

_Doctrine status: implemented in MVP, traditional rulers only._

## Purpose

Rulership analysis asks a more specific question than raw synastry: does one person's planet contact a body that governs the other person's core relational faculty? A Venus–Mercury conjunction is generic until you know that Mercury rules the other person's 7th house. That fact changes the interpretive weight.

Rulership is a **context multiplier**, not a replacement signal. It deepens an existing aspect's meaning. It does not override a tighter Tier 1 synastry pattern unless convergence also supports that elevation.

---

## Traditional ruler map

```
Aries       → Mars
Taurus      → Venus
Gemini      → Mercury
Cancer      → Moon
Leo         → Sun
Virgo       → Mercury
Libra       → Venus
Scorpio     → Mars
Sagittarius → Jupiter
Capricorn   → Saturn
Aquarius    → Saturn
Pisces      → Jupiter
```

Modern co-rulers (Uranus for Aquarius, Neptune for Pisces, Pluto for Scorpio) are **intentionally excluded** from the MVP. They introduce ambiguity in interpretation and in ranking, and the traditional map is sufficient for this depth layer.

---

## Houses calculated for each natal chart

When reliable house or angle data exists:

- **Ascendant** sign and ruler.
- **Descendant / 7th house** sign and ruler.
- **5th house** sign and ruler.
- **8th house** sign and ruler.

For each ruler, the natal placement is captured: planet, sign, house, degree.

If house data is unavailable (no birth time), the rulership layer is skipped gracefully. Interpretation should not fabricate rulers from solar houses.

---

## Interpretive meanings

### 5th-house ruler — romance faculty

The 5th house governs romance, play, pleasure, flirtation, creative eros, and the desire-expression faculty. The ruler of the 5th describes how that faculty is embodied: which planet carries it, where it lives in the chart, what sign temperament it moves through.

When another person's planet contacts someone's 5th-house ruler, they are touching that person's romance/play axis — not as a generic attraction, but as a chart-specific point of creative and erotic aliveness.

Language: "play," "pleasure," "romance," "creative risk," "desire expression." Avoid: "compatibility," "right match," "meant for each other."

### 7th-house ruler — partnership faculty

The Descendant and 7th house govern direct encounter, mirroring, projection, partnership recognition, and the architecture of commitment. The ruler of the 7th is the chart's primary partnership significator.

When another person's planet contacts someone's 7th-house ruler, they are activating that person's partner-recognition faculty — the function that registers "this person matters to how I do relationship."

Language: "partner recognition," "mirroring," "commitment relevance," "encounter." Avoid: "the one," "soulmate," "fated partner."

Reciprocal 7th-ruler activation (both people have their 7th ruler contacted cross-chart) is a stronger signal and is called out separately in diagnostics.

### 8th-house ruler — trust and vulnerability faculty

The 8th house governs vulnerability, trust, guarded interior, psychological access, exposure, and transformation. The default interpretation should be trust and depth of access — **not** sex or eroticism by default.

When another person's planet contacts someone's 8th-house ruler, they are touching that person's trust/exposure faculty. This can describe where a bond asks for real psychological risk or deep mutual disclosure.

Language: "trust," "exposure," "vulnerability," "guarded interior," "psychological access." Avoid: defaulting to sex, "power struggle" as the only frame.

### Ascendant ruler — identity faculty

The Ascendant and its ruler describe identity, self-direction, embodiment, and how a person enters the world. When another person's planet contacts someone's Ascendant ruler, they touch the way that person shows up and moves through life.

Reciprocal Ascendant-ruler activation (both Ascendant rulers contacted cross-chart) is a strong identity-mirror signature — each person activates the other's self-directional faculty.

---

## Rulership as a context multiplier

Ruler contacts are applied as weighting multipliers after convergence, not as standalone base scores:

| Ruler contact | Multiplier |
|---|---|
| 7th-house ruler (Descendant ruler) | ×1.20 |
| 5th-house ruler | ×1.15 |
| 8th-house ruler | ×1.10 |
| Ascendant ruler | ×1.10 |
| Reciprocal 7th-ruler activation | ×1.10 additional |
| Reciprocal Asc-ruler mirroring | ×1.12 |
| Descendant axis contact (Asc conj/opp) | ×1.20 |

These multipliers are intentionally conservative. A ruler contact on a modest synastry aspect (base priority ~62) reaches roughly 74–80 after multiplier — still below a tight Tier 1 aspect (which lands at ~90+). Ruler contacts should deepen a reading, not manufacture false lead patterns.

---

## Composite chart rulerships — excluded

Composite chart rulerships are not implemented in the MVP and are excluded from Constellation's default rule set.

Reasons:

- The composite chart is a derived midpoint chart; assigning house rulerships to it without established doctrine introduces interpretive noise.
- The synastry and natal-overlay ruler layer already provides sufficient relational depth without composite ruler claims.
- Composite configurations are used as synthesis (T-squares, stellia, Venus/Mars aspects) rather than as a second rulership system.

This may be revisited in a future doctrine pass if a clear, testable doctrine emerges.

---

## House overlays vs. aspects

House overlays and synastry aspects are different layers:

| | Synastry aspect | House overlay |
|---|---|---|
| What it measures | Angular relationship between two planets | One person's planet landing in the other's natal house |
| Who feels it | Both people feel the contact | The **house person** generally feels the overlay more than the planet person |
| Rulership relevance | Aspect can touch a ruler directly | Overlay activates the house field; ruler of that house adds a further layer |
| Reciprocal | Double-whammy if same pair reversed | Reciprocal overlay (each person's planet in the other's same house) is a stronger signal |

Reciprocal 5th-house and 7th-house overlays deserve stronger interpretive language than one-directional overlays. An 8th-house overlay speaks to trust and exposure before it speaks to eroticism.
