# Constellation Product Strategy

Implementation-facing reference. Not a pitch deck. Use this to orient feature decisions and prioritization.

---

## Core product thesis

Constellation gives users language for relational experiences they feel but cannot articulate.

Most people sense the texture of their relationships — the pull, the friction, the patterns that repeat — but lack a framework for naming what they are experiencing. Constellation generates that framework from deterministic astrology: what is actually in the charts, not what a compatibility algorithm assigns as a score.

This makes Constellation a **relational atlas**, not a compatibility app. The output is a Relationship Map that describes the terrain — where the warmth is, where the friction lives, what keeps repeating — so that users can bring more agency to their relationships. It does not tell users whether a relationship is good or bad, fated or doomed, a match or a mismatch.

The value is articulation, not verdict.

---

## Primary user segments

### Dating / new romance
Users generating a first map on someone they are newly interested in. High curiosity, high emotional investment, low patience for complexity. They want the highlights: what draws attention, what to watch for early.

Design implication: the Overview section and the leading dynamic carry disproportionate weight here. The thematic reader helps them jump to "Eros & Attraction" or "Communication" without reading the whole map.

### Committed partnership
Users returning with an ongoing relationship — often with specific questions. "Why do we keep fighting about this?" "Why does intimacy feel hard right now?" These users tolerate depth and return repeatedly.

Design implication: saved relationships, the ability to add context and questions, and the thematic reader for targeted exploration are most valuable here.

### Troubled partnership / repair
Users seeking language for real difficulty. They need the friction named honestly, the repair guidance to be practical, and the framing to be non-fatalistic. This segment is the most vulnerable to harm from bad language choices.

Design implication: the Friction and Repair section must be chart-specific, not generic. Repair guidance must point to behaviors, not verdicts. Forbidden language guardrails are most critical here.

### Family relationships
Parent-child, sibling, or extended family maps. These users need language that is relational without being romantic. Attachment, emotional translation, and home-axis overlays are more relevant than erotic charge or romance.

Design implication: the `relationship_type` system must suppress romantic framing in family contexts. Section titles, lead selection, and dynamic detail language should adapt to the relationship type.

### Friendships
Often used to understand long-term or complicated friendships: why they feel so close, why they sometimes clash. Communication patterns and the 11th/3rd house axis matter here more than the 5th/7th/8th.

Design implication: `friend` and `collaborator` relationship types need their own context boosts and section framing.

### Self-pattern seekers
Users who are less focused on any one relationship and more interested in their own recurring patterns across relationships. They want to know: what do I keep doing, what do I keep attracting, what themes recur?

Design implication: Constellation Patterns / cross-relationship view is the primary product surface for this segment. Saved people and saved relationships are prerequisites.

### Astrology enthusiasts
Users who already know astrology and want to see their synastry interpreted through a structured, non-generic lens. They will look at the Calculated Chart Check section, notice the house overlays, and evaluate the interpretive quality.

Design implication: technical accuracy is a trust signal. The chart check section, diagnostic precision, and non-cookbook prose are how this segment evaluates quality.

### Social sharers
Users who want to post resonant insights — an aspect interpretation, a repair principle, a theme card — to social platforms. They are not always deep users; sometimes a shareable card is the product.

Design implication: shareable insight cards are a distribution mechanism, not just a feature. They need to be standalone-readable without requiring chart context, and must never carry forbidden language.

---

## Core product loops

### 1. Create a map
User enters two birth profiles → chart is calculated → Relationship Map is generated → user reads it.

This is the acquisition loop. First-use value must be felt in the Overview section within the first 30 seconds of reading.

### 2. Save people
User saves a birth profile (themselves, a partner, a family member). The vault of saved people makes returning faster and enables multi-relationship maps.

This is the retention foundation. A user who has saved three people has anchored themselves to the product.

### 3. Save relationships
User saves a generated map so they can return to it, add context, or compare it later.

A saved relationship is a persistent relationship object with a type, a context, and a map. It is the unit of the archive.

### 4. Return to the archive
User comes back to a saved map — to re-read it after something happened, to add a question, to explore a different section, or to regenerate with updated context.

The archive is the primary retention surface. Users who return are the engaged segment.

### 5. Explore recurring patterns
User views Constellation Patterns — a cross-relationship view that surfaces what themes, categories, and dynamics recur across their saved maps.

This is the self-pattern discovery loop and the highest-value long-term feature. It requires at least 3–4 saved relationships to become meaningful.

### 6. Share resonant insight cards
User shares a card from a Relationship Map — a single aspect interpretation, a theme, a repair principle — to social media or directly to a partner.

This is the viral/distribution loop. Cards should be visually distinctive and standalone-readable.

---

## Strategic architecture implications

### `relationship_type` system
Already implemented. Every saved relationship has a type that controls:
- which patterns are boosted or suppressed
- what section framing is used
- whether romantic language is suppressed
- which context boosts apply in weighting

The relationship_type enum must cover: `romantic`, `dating_exploring`, `long_term_partner`, `ex`, `unresolved_connection`, `friend`, `collaborator`, `parent`, `child`, `sibling`, `family_other`, `admired_figure`.

### Saved people vault
A user's collection of saved birth profiles. Once someone is saved, they can be pulled into any new relationship map without re-entering birth data. This is the prerequisite for the archive and for Constellation Patterns.

Requirements:
- Per-user or per-device storage
- Edit/update capability (birth time corrections are common)
- Privacy: saved profiles should never be shared without user action

### Searchable / thematic reader
The thematic atlas feature (now implemented as `theme_index` on every report). Enables users to jump to "Communication", "Eros & Attraction", "Conflict / Friction", or any of the 12 reader themes without reading the full report linearly.

The frontend reads `theme_index` from the API — it does not parse prose to infer themes. Theme tags come only from deterministic pattern categories and section anchors.

### Question mode (later)
A future mode where the user enters a specific question before generating or re-reading a map ("why do we fight about money?", "what's the sexual dynamic?"). The question influences context boosts and synthesis packet priorities without changing the deterministic astrology.

The `user_question` field in `RelationshipContext` is already in the schema. The report generation pipeline already uses it for context weighting. The product feature is the UI surface that makes it feel intentional.

### Shareable insight cards
Structured outputs from the Relationship Map that can be formatted as visual cards:
- A single dynamic detail (title + summary)
- A theme card ("Eros & Attraction" presence + two supporting patterns)
- A repair principle
- A Constellation Pattern summary ("You have 5 relationships with strong emotional-dynamics themes")

Cards must be visually distinct from the full report, must carry the Constellation brand, and must never include forbidden language. They should include a subtle chart attribution (sign, aspect) so they feel astrologically grounded without requiring the viewer to own the full map.

### Constellation View / cross-relationship patterns
The aggregated view of recurring motifs across all of a user's saved relationships. Already partially implemented as `constellation_patterns.py` and the `SavedRelationshipMotif` persistence layer.

The product surface is a dedicated screen or section that answers: "Across your relationships, here is what keeps showing up." This requires:
- Enough saved motifs to be statistically meaningful (gated at 3+ relationships)
- Category-level aggregation (not just raw pattern keys)
- Plain-language summary generation

---

## Guardrails

These are non-negotiable constraints on all product surfaces, copy, and AI-generated prose.

### No compatibility scores
No numerical match percentage, compatibility rating, or score of any kind. Not "87% compatible", not a star rating, not a suitability index. This includes implicit scoring through superlatives ("one of the strongest connections possible").

### No fate / destiny / soulmate / twin-flame language
Forbidden phrases: soulmate, twin flame, fated, destined, meant to be, meant-to-be, karmic contract (in a fated sense), written in the stars (in a prescriptive sense). These phrases imply that astrology determines outcomes. Constellation describes tendencies, not fates.

### No romantic language in family / friend / professional reports
A parent-child map must not use erotic charge, romantic pull, or attraction language — even when the underlying patterns would use those categories in a romantic context. The `relationship_type` system handles this through section framing and category suppression, but copy review must apply this standard to all AI-generated prose and UI text.

### No frontend-invented astrology
The frontend never calculates, infers, or generates astrological content. All theme tags, section anchors, pattern data, and interpretive prose come from the backend. The frontend's job is to display deterministic output faithfully.

This applies to AI enhancement as well: the AI layer may polish prose from deterministic inputs, but it may not calculate placements, invent aspects, invent houses, or change priority rankings.

---

## Roadmap

### MVP — core map experience
- Birth data entry (manual coordinates + timezone)
- Chart calculation (pyswisseph, Placidus)
- Relationship Map generation (full report with all sections)
- Dynamic details / expandable Read more
- Thematic reader with jump navigation
- Calculated chart check section
- Basic saved relationships (local or simple backend)
- Saved people vault

Success metric: a user can generate a meaningful Relationship Map, feel the interpretive quality in the Overview, and return to a specific section they care about.

### Paid retention features
- Unlimited saved relationships (free tier gated at 2–3)
- Context and question mode (re-generation with a specific question)
- Full Constellation Patterns / cross-relationship view
- Re-generation with updated relationship type or status
- Map archive with timestamps and version history

These features are valuable only after a user has already experienced the core map. They monetize depth and return behavior, not first-use curiosity.

### Viral / share features
- Shareable insight cards (single dynamic, theme card, repair principle)
- Share a full map with a partner (view-only link)
- "My recurring patterns" shareable card from Constellation Patterns
- Partner invite flow (share a map → partner enters their own data → both see the map)

These features drive acquisition through social distribution. The shareable content must be self-contained and brand-legible without requiring the viewer to understand astrology.

### Future features
- **Question mode UI**: explicit question entry before map generation, not just as a context field
- **Geocoding / place lookup**: replace manual lat/long entry with city search
- **Place presets**: common birth locations with pre-filled coordinates
- **Relationship timeline**: re-generate the same relationship at different relationship_type stages and compare maps over time
- **AI enhancement toggle**: option to receive AI-polished prose vs. deterministic-only output
- **Practitioner / astrologer mode**: full diagnostic view exposed as a primary surface, not a developer tool
- **Composite chart emphasis mode**: for users who want the composite field foregrounded over synastry
- **Notifications / prompts**: "You haven't revisited this map in 3 months. Something to return to?"

---

*This document reflects product strategy as of June 2026. Update the roadmap section as features ship. Do not update the thesis or guardrails sections without a deliberate product decision.*
