# Relationship House Rulership Significators

This document defines how Constellation uses house rulerships as a secondary weighting layer in synastry scoring. Rulerships act as context multipliers — they amplify the significance of an already-detected aspect when that aspect involves a relationship-house ruler. They do not generate new patterns on their own.

---

## Traditional Ruler Map (MVP)

```python
TRADITIONAL_RULERS = {
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

Modern co-rulers (Uranus for Aquarius, Neptune for Pisces, Pluto for Scorpio) are deferred. Traditional rulers are sufficient for MVP and avoid introducing ambiguity in weighting.

---

## House Gating

The rulership layer requires reliable house data. Gate on `BirthData.time_known = True` AND `Chart.houses` being non-None AND `Chart.angles` being non-empty. If any condition fails, skip the rulership layer entirely for that person. Do not attempt ruler calculation without a known birth time.

---

## The Five Relationship Significators

### Ascendant Ruler

The planet ruling the sign on the Ascendant. Contacts to the Ascendant ruler describe how a partner reaches someone's core self-expression and immediate personal identity. These contacts feel personally direct — the partner seems to touch who the person fundamentally is, not just what they do or feel.

### Descendant / 7th House Ruler

The planet ruling the sign on the 7th house cusp (opposite the Ascendant). Contacts to the 7th ruler activate the partnership faculty — the person's deep template for what a partner should be. When someone's planet aspects another person's 7th ruler, the planet person tends to enter the other's "partner archetype" territory.

A favorable aspect between both people's 7th rulers is a background harmonic (general partnership receptivity). Cross-aspects to the 7th ruler itself are foreground activation.

**Reciprocal Asc/Desc ruler swap:** If Person A's Ascendant is in a sign ruled by the same planet as Person B's Descendant, and vice versa — each person's self-expression is literally ruled by the other's partnership axis. This is a rare, high-signal configuration. Treat as the strongest ruler-layer contact.

### 5th House Ruler

The planet ruling the sign on the 5th house cusp. The 5th house governs romance, play, pleasure, creative eros, flirtation, and the expression of desire. Contacts to the 5th ruler describe how a partner activates the other person's romance-and-play faculty — not love in the abstract, but the specific flavor of romantic enjoyment native to that person.

5th ruler contacts are romance-axis signals. They are distinct from and often lighter than 7th ruler contacts — they describe dating chemistry, playfulness, and mutual pleasure, not necessarily commitment relevance.

### 8th House Ruler

The planet ruling the sign on the 8th house cusp. The 8th house governs trust, psychological exposure, vulnerability, and transformation. Contacts to the 8th ruler are not primarily erotic — they describe access to guarded interior material: the parts of the self a person does not normally share.

When someone's planet aspects another's 8th ruler, the planet person gains access to (or activates) the other's defended self. This can feel intimate, destabilizing, or both. Report language for 8th ruler contacts should reference trust, exposure, and the permission to be seen — not default to intensity or sexuality.

---

## Weighting Guidance

Ruler contacts are context multipliers applied after base aspect scoring:

| Contact type | Category | Suggested boost |
|---|---|---|
| 5th ruler contact | `romance_axis_contact` | ×1.1–1.2 |
| 7th ruler contact | `partnership_axis_contact` | ×1.15–1.25 |
| 8th ruler contact | `vulnerability_axis_contact` | ×1.1 |
| Asc ruler contact | `identity_axis_contact` | ×1.05–1.1 |
| Reciprocal 7th ruler | Additional modest boost on top | ×1.1 stacked |
| Reciprocal Asc/Desc swap | `mirror_recognition` | Strongest ruler boost |

Cap total priority at 100. Ruler contacts do not override a tighter Tier 1 synastry aspect on their own — they require convergence with a real aspect to matter.

---

## How House Overlays Differ from Aspects

Aspects describe direct energy exchange between two planets — dynamic, active, immediately felt.

House overlays describe where someone lands in the other person's life — which area of life they activate by their presence. This is ambient and situational, not a direct energetic connection.

The house person generally feels the overlay more than the planet person. Reciprocal overlays (both people landing in each other's romantic houses) are meaningfully stronger than one-directional overlays.

Romantic overlay houses in priority order: 7th, 8th, 5th, 1st, 4th, 12th.
Non-romantic overlay houses (2nd, 3rd, 6th, 9th, 10th, 11th) should be penalized more heavily in romantic report contexts.

---

## Why Composite Sign Rulerships Are Excluded

Robert Hand (Planets in Composite) explicitly notes that sign behavior in composite charts is of uncertain validity — the zodiac in a composite may function only as a measurement tool rather than carrying its usual symbolic meaning. House positions and aspects in composite charts are reliable; sign-based rulerships derived from composite cusps are not. Do not implement composite house rulerships.

---

## Sources

- Ruiz, *Prediction Techniques Regarding Romance*: 5th ruler as primary romance significator; Asc/Desc ruler swap as excellent synastry indicator
- Davison, *Synastry: Understanding Human Relations Through Astrology*: 7th ruler contacts; house overlays as "personified transits"
- Suskin, *Synastry: Understanding the Astrology of Relationships*: 5th ruler scope (play, sex attitudes, romance expectations); overlay activation of natal potential
- Eddington, *Top 10 Best Synastry Aspects*: romantic house hierarchy; house person feels overlay more; reciprocal overlay significance
- Hand, *Planets in Composite*: composite sign uncertainty; reading order; outer planet gating
