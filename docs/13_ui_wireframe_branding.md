# 13 — UI Wireframe & Brand Direction

**Constellation — relationship astrology app**
Companion document to `constellation_wireframe.html`

---

## Overview

Constellation is an intimate, intelligent app for understanding the dynamics between people. The visual language should feel considered, literary, and slightly cosmic — not mystical or New Age. Think midnight observatory meets personal journal. Every design decision should serve the sense that the user is being given something real.

---

## 7 Key Screens

### 1. Home / Constellation Hub

The app opens onto the user's relational world rendered as a living star map. The user is the center node in gold; each saved relationship is a dot connected by a line, color-coded by relationship type. Recent insights appear as cards below the map as return-entry points.

**Design notes:**
- The constellation SVG is the brand metaphor made literal — the app is named this and the home screen proves it
- Relationship type color badges must be consistent with every other surface in the app
- "Recent insights" cards give returning users an immediate re-entry path without navigating
- The wordmark "Constellation" appears here in small-caps with the gold accent

**What the user feels:** *My relational world is visible and organized. I can see it.*

---

### 2. New Reading — Type Selection

First step of every reading flow. The user selects which kind of relationship they're reading before any names are entered. The choice sets the doctrine layer for the entire report: which patterns surface, which suppress, and what vocabulary is permitted throughout.

**Design notes:**
- 2-column grid of type cards: Romantic, Committed, Family, Friendship, Ex, Professional, Other
- Each card has a small color-coded icon, label, and one-line sub-description
- The selected type shows a subtle tinted background and a checkmark
- A "Continue as [Type]" CTA button at bottom using the type's color
- Type color coding must match exactly what will appear in report badges and constellation dots

**Why this matters:** Type is not just metadata — it is the report's interpretive filter. "Ex" suppresses eros language entirely; "Professional" suppresses 8th house and physical attraction content; "Romantic" brings the full pattern set. This screen is the first moment the user declares intent.

---

### 3. People Picker — The Vault

The vault is the primary retention mechanism. Users enter birth data once and it persists across all future readings. The screen shows Person A (pre-filled with the user's data) and Person B (search or add from vault).

**Design notes:**
- Person A section uses gold accent border — confirmed and locked
- Birth time flagged as optional with explicit note: "· houses unavailable" when absent
- The app should not hide what's limited — show it plainly and let the user decide
- "Add someone new" uses a dashed border and muted treatment — invitation, not imperative
- People already in the vault show birth data at a glance for quick selection

**Retention logic:** Every new person added to the vault is a micro-investment. The more people in the vault, the stickier the app. Removing friction from the return visit (not re-entering data) is the core mechanism.

---

### 4. Report — Surface View

The report opens with "The Bond" — 2-3 sentences in italic serif that name what the connection is at its core. Pattern cards follow in a scrollable list, each with a title, a one-line frame ("What feels easy," "The attraction," "What's harder"), a five-dot signal strength indicator, and a one-paragraph description. Read More reveals the full depth layer.

**Design notes:**
- "The Bond" uses a left gold border and italic serif — visually distinct from pattern cards
- Five-dot signal strength: filled dots in gold, empty in dark border color
- Difficult patterns use a muted rose border (not red — never alarm language)
- Two bottom CTAs: "Explore by theme" (muted) and "Share insight" (type-colored)
- Type badge and person names persist in the header throughout the report
- Bookmark and share icons in the top-right from page one

**The hook:** The Bond is the pull that gets users to read further. Pattern cards are the substance. Read More is where the interpretive depth lives. The surface sells the depth.

---

### 5. Question Mode — The Retention Feature

A themed navigator over the same pattern set. Theme pills at the top: Communication, Conflict style, Closeness, Independence, Long term, Fun & play, Family patterns. Selecting a theme pulls the relevant patterns and frames them for that context. A synthesis paragraph at the bottom distills the theme-level takeaway.

**Design notes:**
- Theme pills use a pill/capsule shape with a subtle background tint when selected
- Left-border color on pattern cards signals positive/difficult: teal for easy, rose for hard
- Synthesis paragraph at bottom is a unique surface — not a pattern card, but a thematic read
- No back-and-forth navigation required — the user taps a theme and gets the view

**Why this is the retention feature:** Users don't re-read a full report. They return to the app during a specific moment — a conflict, a silence, a question. Question Mode makes Constellation useful in real-time. This is the reason a user opens the app 3 months after their initial read.

---

### 6. Insight Card — The Viral Engine

A single sentence from the report rendered as a designed shareable card. The user picks which pattern to surface (The Bond, or any pattern card), previews the card, and sends it to the person in the report or copies it for public sharing.

**Design notes:**
- The card preview must look beautiful enough to screenshot voluntarily — this is a high bar
- Card background: deepest midnight (#0A1428), gold logotype, italic serif pull quote, duo avatar at bottom
- Two CTA buttons: "Copy image" (muted, secondary) and "Send to [Name]" (primary, type-colored)
- "Send to [Name]" should open a sharing flow that reaches the other person — ideally via a link that lands on a page prompting them to download the app and see their side of the reading
- The pull quote must be a genuine human line, not a generic sentiment

**Acquisition logic:** Sending the card to the person in the report is the highest-conversion acquisition path. That person receives something personal and resonant about their relationship. The implicit question is "what else does it say?" — which drives a download. Every share is a potential new user.

---

### 7. Constellation View — Patterns Across Your World

Unlocks after 3+ saved readings. Shows the user what keeps appearing across all their relationships — not as a personality assessment but as a relational mirror. Pattern cards show which relationships share the theme, with relationship-type badges for each.

**Design notes:**
- Header: "Your constellation" in gold small-caps; "Patterns across your world" in display serif
- Each cross-relationship pattern shows: theme name, relationship badges (color-coded), description, "What does this mean?" CTA
- "Add more readings to deepen your pattern map" — encourages growth of the vault
- Accessible from the "patterns" tab in bottom navigation (the branch/diagram icon)

**The self-pattern seeker:** This is the feature that turns a report tool into a long-term companion. Users who are interested in their own patterns — not just one relationship — are the most retentive segment and the most likely to recommend. Constellation View is why they stay.

---

## Navigation Structure

**Bottom tab bar (5 items):**

| Tab | Icon | Links to |
|-----|------|----------|
| Home | Star (outlined) | Home / Constellation Hub |
| People | Users | People vault / picker |
| + (center, gold circle) | Plus | New reading flow |
| Patterns | Branch/diagram | Constellation View |
| You | User circle | Profile, birth data, settings |

The center button (gold circle with plus) is the primary action trigger and visually dominant. All other nav items use muted color; active tab uses gold.

---

## Color System

### Base Palette

| Role | Hex | Usage |
|------|-----|-------|
| Midnight (background) | `#0C1220` | App background, phone exterior |
| Card surface | `#131C30` | All card and list item backgrounds |
| Border | `#1A2338` | Dividers, card outlines, separator lines |
| Gold (accent) | `#C9A84C` | Primary CTAs, active states, The Bond accent, wordmark |
| Cream (primary text) | `#EAE4D8` | All body and heading text on dark |
| Muted (secondary text) | `#6E7A96` | Labels, timestamps, secondary descriptions |
| Deep muted | `#3D4A68` | Tertiary text, inactive icons |

### Relationship Type Colors

| Type | Hex | Notes |
|------|-----|-------|
| Romantic (dating) | `#C47A8A` | Rose — warm but not aggressive |
| Committed (long-term) | `#A86080` | Deeper rose — signals gravity |
| Family | `#5AADA0` | Teal — connective, grounding |
| Friendship | `#6A9BC4` | Blue — open, trustworthy |
| Professional | `#7A8B9B` | Slate — neutral, restrained |
| Ex | `#505A72` | Grey — present but receded |

These colors appear on: constellation dot, type badge in report header, share card border, people vault avatar ring, and pattern card borders for positive/hard signals.

---

## Typography

### Display / Interpretive Prose
**Cormorant Garamond** (or Playfair Display as fallback)

Used for:
- "The Bond" section (italic, 12–14px in-app)
- Report pattern body text (regular, 11–12px)
- Share card pull quote (italic, 13–14px)
- Screen titles (regular, 17–19px)
- App wordmark

*Why:* This is where the app's intelligence lives. The prose should feel like a thoughtful person wrote it after careful reflection — not like a horoscope and not like a data readout. The serif signals intentionality and weight.

### UI Chrome
**Inter** or **DM Sans** (geometric sans)

Used for:
- Navigation labels
- Timestamps and dates
- Type badges
- Button text
- Section headers (all-caps, tracked)
- Search fields and input labels

*Why:* The contrast between serif (meaning) and sans (navigation) is load-bearing. The user should feel the shift between "content I'm reading" and "interface I'm operating." If everything is the same typeface, that distinction collapses.

---

## Voice & Copy Principles

The app has a point of view. It should feel like it was written by someone intelligent who has thought carefully about the subject — not generated, not cautious, not clinical.

**Do:**
- "Your world" — not "Your dashboard"
- "The Bond" — not "Overview" or "Summary"
- "What do you want to understand right now?" — not "Select a topic"
- "This keeps showing up" — not "Pattern detected"
- "What feels easy" — not "Positive aspects"
- "What's harder" — not "Challenges" or "Difficult aspects"
- "There's a charge here" — earned specificity
- "At moments, Jordan's presence can feel like pressure to Charlie — not unkindly, but there's a weight here" — nuanced, non-alarming

**Don't:**
- Never cite astrological mechanisms in user-facing text ("because Venus squares your Mars")
- Never use clinical language ("compatibility score", "synastry analysis", "natal chart data")
- Never use alarm language for difficult patterns ("warning", "red flag", "danger")
- Never use certainty language ("this means", "you will", "always")
- Never use astrology-speak the user didn't bring ("your 7th house ruler", "applying trine")

---

## App Icon & Wordmark

**Icon:** A single six-point asterisk (★) or a three-node connected mark (three dots with connecting lines forming a small triangle) on deep midnight. Simple enough to read at 44px. Avoid zodiac wheels, planet imagery, moon glyphs, and traditional astrology symbols — those are the category clichés. The asterisk is a star and a marker at once — both reading a text and looking up at the sky.

**Wordmark:** "CONSTELLATION" set in Cormorant Garamond, all-caps, generous tracking (0.12–0.15em), paired with the asterisk mark to the left or above. Gold on midnight for app launch and marketing materials. Dark ink on cream for light-mode contexts (web, press kit).

**App store presentation:** The icon should read as a premium, literary product — not a mystical one. The category signal should be "thoughtful personal tool" not "fortune telling app." The icon is the first filter that qualifies or disqualifies the right user.

---

## What This App Is Not

These are as important as the positive direction:

- **Not a horoscope app.** No daily predictions, no "your week ahead," no zodiac personality content.
- **Not a compatibility scorer.** No percentage match, no compatibility rating, no ranking.
- **Not a fortune teller.** Nothing about what will happen. Only what tends to happen and why.
- **Not a therapy app.** The tone is observational and interpretive, not prescriptive or supportive.
- **Not a mystical product.** The design is cool, considered, and literary — not celestial, swirly, or purple.

The user is an adult who is curious about their relationships and willing to engage with an intelligent lens. They deserve a product that treats them that way.
