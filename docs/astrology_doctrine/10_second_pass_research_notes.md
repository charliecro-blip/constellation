# Second Research Pass — Notes & Doctrine Proposals

Deliverable 10 for Constellation (relationship astrology app).

**Copyright compliance:** All source material below is paraphrased, not quoted verbatim. Source metadata is tracked. Claims attributed to sources are distinguished from synthesis.

---

## Part 1 — Implementation Status Update

Status of original 9 deliverables as confirmed by reading the current repo (README, CLAUDE.md, PROJECT_STATUS.md, and all `docs/astrology_doctrine/` files):

| Deliverable | Status in Repo | Notes |
|---|---|---|
| 1. Synastry weighting doctrine | ✅ Implemented | `synastry_weighting.md` with Tier 1–4 hierarchy |
| 2. Pattern taxonomy | ✅ Implemented | Expanded to 15 categories in `pattern_taxonomy.md` |
| 3. Report prioritization algorithm | ✅ Implemented | `report_prioritization.md`; convergence logic in place |
| 4. Composite chart doctrine | ✅ Implemented | `composite_doctrine.md` (condensed 4-section doc) |
| 5. Asteroid policy | ✅ Implemented | `asteroid_policy.md`; MVP vs. advanced gating in place |
| 6. Report voice guide | ✅ Implemented | `report_voice_guide.md`; 5-step interpretive movement |
| 7. App architecture suggestions | ✅ Implemented | `pattern_registry.py`, `scoring_weights.py`, `motifs.py` etc. |
| 8. Codebase review | ✅ Mostly addressed | Gaps from original review partially closed |
| 9. MVP roadmap | ✅ Mostly complete | `PROJECT_STATUS.md` confirms all major steps done |

**One significant item still scoped but not yet built:** relationship-house rulership significators. `PROJECT_STATUS.md` says explicitly: "The next astrology-depth pass should be relationship-house rulership significators." The current `report_prioritization.md` mentions 7th, 5th, and 8th rulers as context modifiers but does not document how to detect them or how to weight them.

**Also still thin:** house overlay doctrine (which houses matter, in what order, how to describe them experientially), composite T-square/stellium configurations, and similarity/difference framing beyond the temperament module.

---

## Part 2 — Still-Missing or Underdeveloped Doctrine Areas

Listed in order of priority (most impactful to MVP report quality first):

**1. Relationship-house rulership significators** — No implementation yet. The doctrine note in `report_prioritization.md` names the relevant rulers (5th, 7th, Asc/Desc, 8th) but provides no weighting logic, detection rules, or orb guidance. This is the named next step in `PROJECT_STATUS.md`.

**2. House overlays** — The current codebase handles house positions of partner planets but there is no doctrine doc on: which overlay houses should rank as relationship-relevant, when a house overlay should outweigh an isolated tight aspect, or how to describe overlays experientially vs. aspectually. The distinction matters because overlays feel different from aspects (ambient activation vs. direct energy exchange).

**3. Composite chart configurations** — `composite_doctrine.md` handles Sun/Moon/Saturn themes but does not address T-squares, stellia, Mars-Pluto contacts, or how to sequence narrative when multiple composite configurations conflict.

**4. Similarity vs. difference analysis** — `temperament.py` weaves in element/modality data, but there is no doctrine on when sameness creates comfort vs. stagnation, when difference creates growth vs. depletion, or how to frame the result without generic "opposites attract" filler.

**5. Repair principles at the pattern level** — `report_voice_guide.md` documents the voice arc (theme → felt experience → shadow → repair → agency), but the specific repair principles per pattern are underspecified. The taxonomy doc has repair entries but they are brief. No doctrine on what distinguishes "specific, actionable repair language" from generic coping advice.

**6. Timing/love-planning** — Flagged as future/backlog by user. Do not implement for MVP. Noted here for completeness.

---

## Part 3 — Source Cards

Paraphrased research organized by topic. Source metadata in brackets. Claims from sources are labeled [SOURCE]; synthetic conclusions from combining sources are labeled [SYNTHESIS].

---

### 3A. Relationship-House Rulerships

**The 5th house ruler as primary romance significator**

[SOURCE — Ruiz, *Prediction Techniques Regarding Romance*, pp. 1–61]: The 5th house ruler's sign, house, and aspects together form a "romance style profile" — indicating what a person finds pleasurable, how they express affection, their attitude toward flirtation and play, and their orientation toward children. In synastry, contacts to a person's 5th house ruler are contacts to their romance faculty itself. For committed relationships, the 7th house ruler takes on increased weight.

[SOURCE — Suskin, *Synastry*, pp. 82–104]: Expands the 5th ruler's scope: it colors "experiencing and expressing fun and pleasure," "the importance of sex and the nature of its expression," "beliefs and attitudes about romance," and "expectations regarding children." The ruler's placement describes the style, not the presence or absence of these qualities.

[SYNTHESIS]: In weighting terms, a synastry aspect to the 5th house ruler is not just an aspect to a planet — it's a contact to the person's romance-activation circuit. This is the logical basis for the "5th ruler as context multiplier" already noted in the existing `report_prioritization.md`.

---

**The 7th house ruler and Ascendant/Descendant rulers**

[SOURCE — Davison, *Synastry: Understanding Human Relations Through Astrology*, p. 50]: "A favorable aspect between the rulers of each partner's seventh house is a useful indicator of harmony, but more crucial still are the cross-aspects to any planets in the seventh house." This separates two distinct signals: ruler-to-ruler compatibility (background harmonic) vs. planets actually placed in the 7th (foreground activation).

[SOURCE — Ruiz, *Prediction Techniques*]: "Ruler of one's Ascendant ruling the Descendant sign of the other and vice versa" is identified as an excellent synastry aspect — a natural mirroring that suggests the people are each other's projected ideal partner. This is a specific, detectable configuration, not a general rule about Asc/Desc.

[SOURCE — Eddington, *Top 10 Best Synastry Aspects*, p. 93]: Cites that the Descendant ruler of one person aspecting the Ascendant (or Descendant ruler) of the other "is an excellent indication of happiness and compatibility." Angle conjunctions specifically "bring forth personal growth and the opportunity to explore ourselves through a partner who is strikingly similar to us."

[SYNTHESIS]: There are three distinct ruler-layer signals to detect, in decreasing specificity:
- (a) Reciprocal Asc/Desc ruler swap (Ruiz): Person A's Asc ruler = Person B's Desc sign ruler, and vice versa. Highest specificity, warrants a strong context boost.
- (b) Cross-ruler harmony (Davison): Person A's 7th ruler in favorable aspect to Person B's 7th ruler. Background harmonic; boosts stability signals.
- (c) Ruler-to-ruler contacts more generally (Eddington): Desc ruler aspecting partner's Asc/Desc ruler. Weaker but still relevant.

---

**The 8th house ruler as trust/vulnerability signal**

[SOURCE — Davison, *Synastry*, pp. 94–95]: The 8th house represents "transformations accomplished during the lifetime on other levels" that "release the consciousness from emotional, mental and spiritual bondage." On a mundane level it covers "the partner's resources and our psychological attitude toward the partner's resources."

[SYNTHESIS]: Contact to a person's 8th house ruler (or planets in the 8th) in synastry signals that the partner activates their vulnerability, trust, and exposure faculty. This is not the same as 8th house eroticism — it's about whether the partner reaches the person's defended interior. When both Eddington's overlay doctrine and the aspect layer agree on 8th house activation, the convergence is meaningful.

---

### 3B. House Overlays

**General overlay doctrine**

[SOURCE — Suskin, *Synastry*, pp. 143–146]: Partner's planets in angular houses (1st, 4th, 7th, 10th) produce the strongest impact. Planets in already-occupied natal houses modify the natal planet there. Planets in empty houses activate the house as if a planet had been natally placed there. Overlays do not permanently change the person — they activate natal potentials only in the context of the relationship.

[SOURCE — Davison, *Synastry*, p. 93]: Describes house overlays as a "personified transit" — the influence exists for as long as the relationship with that person lasts, and operates especially when that person is present. Partners with multiple planets in the same house create a concentrated activation of that life area.

[SOURCE — Eddington, *Top 10 Best*, pp. 25–36]: Names the "romantic houses" as 1st, 5th, 7th, and 8th. States that a strong synastry needs at least one or two significant overlays to these houses. A synastry chart "wholly reliant upon house overlays" without personal planet conjunctions has romantic potential but limited depth. Identifies a key asymmetry: the house person generally feels the overlay more than the planet person.

---

**5th house overlay specifically**

[SOURCE — Eddington, *Top 10 Best*, pp. 109–113]: The 5th house overlay produces feelings of playfulness, fun, and excitement. Describes it as "Disneyland energy" — not inherently commitment-oriented, but strongly romance-flavored. Good for dating; tends to stay dating-level unless other overlays (7th, 8th) are also present. Britney Spears / Justin Timberlake example: his Sun in her 5th = fun attraction; relationship stayed in dating-level despite strong synastry elsewhere.

[SOURCE — Eddington, *Top 10 Best*, pp. 111–112]: The natal planets already in the 5th house color how the overlay operates. If someone has a loaded natal 5th, an overlay there amplifies something already prominent in their identity. If the 5th is natally empty, the overlay activates a dormant romance-play faculty.

[SYNTHESIS]: 5th house overlay descriptions should emphasize lightness, play, mutual enjoyment of novelty, and a sense that this person makes life more fun — without promising depth or longevity that the 5th alone doesn't deliver.

---

**7th house overlay specifically**

[SOURCE — Eddington, *Top 10 Best*, pp. 97–99]: The Descendant angle and 7th house overlay indicates the planet person has qualities the house person subconsciously seeks in a partner — "character traits like empathy, understanding, and kindness." It transcends looks. Important caveat: a 7th house overlay from A to B does not guarantee B feels the same toward A. Reciprocal 7th house overlays (both people landing in each other's 7th) correlate more strongly with marriage potential.

[SOURCE — Davison, *Synastry*]: "Cross-aspects to any planets in the seventh house" are more crucial than ruler-to-ruler harmony alone. Planets actually placed in or near the 7th cusp = foreground activation, not background.

[SYNTHESIS]: 7th house overlay language should focus on recognition of the desired partner archetype — "they seem to carry what you've been looking for in a partner" — but should not promise outcome. Reciprocal overlays warrant stronger language.

---

**8th house overlay specifically**

[SOURCE — Eddington, *Top 10 Best*, pp. 114–117]: 8th house overlay creates a sense that one can share previously guarded interior territory — "what felt uncomfortable before now feels possible." The example used is partners who share deeply private fantasies or vulnerabilities. The overlay activates access to the person's defended self, not just their sexuality. Both the Fifty Shades example and subtler case studies emphasize that the 8th makes people feel permission to be exposed.

[SOURCE — Davison, *Synastry*, p. 95]: 8th house = "release from emotional, mental and spiritual bondage through transformation." In overlay terms, the partner becomes the agent of that release.

[SYNTHESIS]: 8th house overlay descriptions should emphasize felt permission to drop defenses, share what's usually guarded, and the sense that this person "gets access to rooms you don't normally open." Not just erotic — can be deeply revealing even in non-sexual relationships. The intensity of this overlay is partly why it feels fateful.

---

**12th house overlay (not in Eddington's top list, but relevant)**

[SYNTHESIS based on general doctrine]: 12th house overlays are conspicuously absent from Eddington's "romantic houses" list. This is consistent with the doctrine that 12th house activation is unconscious, regressive, or spiritually significant in ways that don't produce clear felt attraction signals. If implementing 12th house overlay, treat with caution: it can feel like an inexplicable draw or like the partner reaches something pre-personal.

---

**When overlays outrank aspects**

[SOURCE — Eddington, *Top 10 Best*, pp. 30–35]: A chart with three or four romantic house overlays but no tight personal planet conjunctions has romantic potential "wholly reliant" on those overlays. Conversely, a chart with strong conjunctions between personal planets but no romantic house overlays lacks the "where you land in each other's lives" layer. Both matter; neither alone is sufficient.

[SYNTHESIS]: Proposed weighting guideline: a house overlay to a romantic house (1st, 5th, 7th, 8th) by a personal planet (Sun, Moon, Venus, Mars) should be treated as a Tier 2 signal — not as strong as a direct tight aspect between personal planets, but stronger than supportive texture. Multiple overlays to the same romantic house (especially if stacked with conjunction to the cusp) warrant a Tier 1–adjacent boost. Overlays to non-romantic houses (2nd, 6th, etc.) remain Tier 3–4 texture.

---

### 3C. Composite Chart Configurations

**Reading order doctrine (Hand)**

[SOURCE — Hand, *Planets in Composite*, pp. 34–38]: Establishes this reading order for composite charts: (1) natal charts first to understand what each person needs, (2) house emphasis in composite (best houses = 1st/5th/7th/11th; 8th = fateful but intense; 6th/12th = least favorable for personal relationships), (3) Sun and Moon aspects, (4) Venus and Mars, (5) angular planets, (6) relational houses (4th, 7th, 8th), (7) Saturn.

[SOURCE — Hand]: Explicitly notes that outer planet aspects (Uranus, Neptune, Pluto) in composite should only be taken as significant if at least one of the pair is conjunct an angle. Otherwise they reflect generational dynamics, not the couple's specific relationship.

[SOURCE — Hand, p. 32]: Signs in composite charts may not function the same way as in natal charts. This is still an open question. The practical implication: do not weight composite sign placements as heavily as natal sign placements; house positions and aspects are more reliable.

---

**Composite Sun-Saturn and Moon-Saturn**

[SOURCE — Davison, *Synastry*, pp. 68–69]: Moon-Saturn cross-aspects in synastry can produce long-term bonds sustained by duty and habit rather than joy ("better the devil you know"). Saturn may feel obligated; Moon may become dependent as a father-figure dynamic forms. Not inherently negative if other contacts compensate — but this specific dynamic needs to be named.

[SOURCE — Hand, *Planets in Composite*, Step 8]: Saturn is given its own dedicated step in the reading protocol — examine it separately after Sun/Moon. Composite Saturn "can tell so much about the strengths and weaknesses of a relationship."

[SYNTHESIS]: In composite chart reports, Saturn's house and aspects should be treated as the "structural skeleton" layer — the thing that makes the relationship feel either solid or constrictive, and that determines whether difficulty produces growth or attrition. A composite Saturn conjunct the Sun or Moon is high-signal and warrants dedicated report language about long-term potential and where the load is carried.

---

**Composite Mars-Pluto**

[SOURCE — Davison, *Synastry*, pp. 82–84]: Mars-Saturn cross-aspect = "no combination of planets has achieved a worse reputation in astrology." Not uniformly bad — at best, Saturn plans and Mars executes; at worst, sado-masochistic friction. Best handling: "an agreement to differ can save a lot of wasted energy."

[SYNTHESIS — extending to Mars-Pluto in composite]: Mars-Pluto in composite is the intensity version of Mars-Saturn: less about restriction, more about power, compulsion, and whether shared drive finds constructive vs. destructive expression. Should not be labeled "toxic" — it's a high-energy signature that can produce extraordinary collaborative drive when well-directed.

---

**Composite 8th house emphasis**

[SOURCE — Hand, *Planets in Composite*, pp. 36–37]: 8th house in composite = "very fateful relationship." Not the least desirable house — but it signals intensity, transformation, and often a sense that this relationship will change both people profoundly. Combined with Hand's note that 6th and 12th are least favorable, the hierarchy for composite house emphasis is: 1st/5th/7th/11th best → 3rd/9th helpful → 4th important for cohabitation → 8th fateful/intense → 6th/12th challenging.

---

### 3D. Similarity vs. Difference Analysis

**Same element = most compatible, but not enlivening**

[SOURCE — Arroyo, *Person-to-Person Astrology*, pp. 108–111]: Same element is most compatible. But same Sun sign without other complementary attunements can produce "nervous system starvation" — neither person is receiving a slightly different and thus enlivening vibration. Compatibility is not sufficient for vitality.

[SOURCE — Arroyo, p. 109]: "The incompatible elements, such as Water with Fire, can cause a depletion of the individuals' magnetic fields at different levels." Fire-Water in particular is highlighted as draining rather than complementary.

[SOURCE — Arroyo, pp. 111–113]: The common claim that "opposites complement each other" sounds better on paper than it works in practice. Attraction to what one lacks may produce initial intrigue, but rarely produces sustained contentment in long-term intimate relationships. More likely to work as a short-term growth arrangement or business relationship.

[SYNTHESIS]: The app's existing element/modality temperament weaving is on the right track, but the language needs to distinguish three cases:
- **High similarity (same element):** "Comfort, mutual recognition, ease — but check whether there's enough novelty to sustain vitality long-term."
- **Complementary polarity (Air-Fire or Earth-Water):** "Naturally stimulating; each brings what the other is wired for."
- **Challenging combination (Fire-Water, Air-Earth):** "Energy often works at cross-purposes; requires conscious translation between different ways of experiencing life."

---

**Moon compatibility as domestic litmus test**

[SOURCE — Arroyo, pp. 113–114]: Compatible Moons = "incomparable help for domestic harmony and feeling comfortable with each other in the constant interactions of daily living." His test: "Would you feel at ease and relaxed with this person on a multiday cross-country drive?" If yes = good Moon harmony.

[SOURCE — Arroyo, p. 113]: If neither Sun nor Moon of one person harmonizes with either light of the other, long-term compatibility is significantly improved only if the Sun or Moon harmonizes with the other's Ascendant.

[SYNTHESIS]: Moon-to-Moon and Moon-to-Asc/Sun harmony is the correct place to anchor "domestic compatibility" report language. This layer is distinct from erotic charge (Venus-Mars) and should be described experientially as ease of daily contact, not as "emotional connection" in the abstract.

---

**Mercury similarity vs. difference**

[SOURCE — Arroyo, p. 114]: Mercury signs don't need to be in harmonious elements for a relationship to work — some of the most stimulating relationships involve sharply contrasting Mercury attunements. Requires mutual respect and goodwill, not compatibility.

[SYNTHESIS]: Mercury difference should not default to negative report language. Frame contrasting Mercury as "you process and communicate differently — this can be a source of friction or a source of genuine intellectual stimulation depending on how you each handle being misread."

---

### 3E. Repair Principles

**What repair language should actually do**

[SOURCE — Suskin, *Synastry*, p. 306]: In client work, repair-oriented reading means helping the person "understand the dynamics of her damaged relationship... guide her toward ways to accept what has happened... move toward healing it by revealing the essential problems." Note: revealing the essential problems is part of repair, not just the prelude to it.

[SOURCE — Arroyo, *Using Astrology Wisely*, pp. 376–387]: Astrology's proper role in relationship work is "to further depth of understanding in order to live more consciously" — not to evade responsibility, foster illusions, or predict perfect solutions. The aim is "perspective, objectivity, and insight." People who function unconsciously are more predictable; conscious people have real choice.

[SOURCE — Arroyo, p. 382]: "Every relationship that's going to be meaningful is not necessarily going to be pleasant." This frames the repair register: the goal of repair language is not to make the difficulty disappear but to give it meaning and direction.

---

**Specific repair signatures from sources**

[SOURCE — Davison, cross-aspect interpretations]: For Mars-Saturn: best arrangement is Saturn draws up the plans and Mars executes them. Provides a concrete practice, not just a reframe. For Moon-Saturn: acknowledgment that duty and habit are sustaining the bond, which can be consciously redirected toward chosen commitment.

[SYNTHESIS]: Good repair language is specific to the pattern, not generic. Examples of what "specific" looks like:
- Venus-Saturn cross-aspect: not "work on your communication" but "practice receiving affection without immediately qualifying it; the Saturn person may need explicit expressions of warmth before they can relax into giving."
- Moon-Uranus cross-aspect: not "embrace each other's differences" but "build in deliberate predictability (scheduled check-ins, routines) to give the Moon person an anchor when Uranus disrupts."
- Mars-Saturn cross-aspect: not "manage your energy" but "try structuring projects together where one plans and the other initiates — the arrangement takes the friction out of everyday contact."

---

## Part 4 — Doctrine Proposals

### 4A. Relationship-House Rulership Significators

**Proposed weighting logic for the rulership layer:**

The rulership layer is a context multiplier applied after base aspect scoring, analogous to how the existing convergence multiplier works. It should boost (not replace) the score of a pattern when a relationship-house ruler is involved.

**Detection rules:**

1. **5th house ruler contact** — Detect when a synastry aspect involves the Ascendant holder's 5th house ruler (the planet ruling the sign on the 5th cusp). If person A's planet aspects person B's 5th ruler, or vice versa, apply a **romance-axis boost** (suggested ×1.1–1.2). This signals that the partner activates the other's romance faculty directly.

2. **7th house ruler contact** — Detect when a synastry aspect involves either person's 7th house ruler. If person A's planet closely aspects person B's 7th ruler:
   - Apply a **partnership-axis boost** (suggested ×1.15–1.25).
   - If both people's 7th rulers aspect each other, apply an additional **reciprocal ruler bonus** (×1.1 stacked).

3. **Asc/Desc ruler swap** (Ruiz pattern) — Detect if person A's Ascendant ruler is the same planet as person B's Descendant ruler (i.e., A's Asc is in a sign ruled by person B's Desc planet). If this is reciprocal (each person's Asc ruler = the other's Desc ruler), apply a **mirror-recognition boost** (suggested ×1.3, treated as convergence-level significance).

4. **8th house ruler contact** — Detect when a synastry aspect involves either person's 8th house ruler. Apply a **vulnerability-axis boost** (suggested ×1.1). Note: 8th ruler contacts are not erotic by default — they are trust-circuit contacts. Language should reflect this.

**Implementation note:** These boosts require house data (birth time). Gate behind `birth_time_confidence` check. If birth time is unknown or low-confidence, skip the rulership layer entirely and fall back to planet-only weighting. This is the correct doctrine; do not attempt ruler calculation without reliable birth time.

**Sign rulership map to use** (traditional + modern for outer planets):
- Aries: Mars | Taurus: Venus | Gemini: Mercury | Cancer: Moon | Leo: Sun | Virgo: Mercury | Libra: Venus | Scorpio: Mars (trad) / Pluto (mod) | Sagittarius: Jupiter | Capricorn: Saturn | Aquarius: Saturn (trad) / Uranus (mod) | Pisces: Jupiter (trad) / Neptune (mod)

Use traditional rulers as primary for lightweight implementation; allow optional modern rulers.

---

### 4B. House Overlay Doctrine

**Proposed overlay scoring model:**

Overlays should be scored separately from direct aspects and added as a "house activation layer" to the report.

**Romantic house tier:**
- Tier R1 (highest): Conjunction to 1st, 5th, 7th, or 8th house cusp within 5° (personal planet conjunct angle = strongest overlay effect)
- Tier R2: Personal planet (Sun, Moon, Venus, Mars) in 5th, 7th, or 8th house
- Tier R3: Personal planet in 1st house
- Tier R4: Personal planet in 4th or 12th house
- Tier R5: Outer planet (Jupiter–Pluto) in any romantic house

**Reciprocity multiplier:** When both A's planets land in B's romantic houses AND B's planets land in A's romantic houses (reciprocal overlays), apply ×1.2 to overlay significance. One-directional overlays are real but asymmetric — the house person feels more.

**When to surface overlay in report:**
- If Tier R1 or R2 overlay is present without a corresponding strong direct aspect: include in report as distinct signal ("where you land in each other's life matters here, independent of the specific angles between your planets").
- If overlay and aspect both point to same house domain: treat as convergence (already handled by convergence multiplier, but note the double-confirmation in report language).
- If only weak overlays (Tier R4–R5) with no strong aspects: suppress or include as brief supporting texture.

**Experiential language for overlays (see Part 5 for full examples):**
- 5th house: playful, fun-activating, "makes life more enjoyable"
- 7th house: partner-recognition, "carries what you've been looking for"
- 8th house: access to the guarded self, permission to be exposed
- 1st house: physical presence, admiration of outward expression
- 4th house: roots-activation, home-feeling, private/domestic quality

---

### 4C. Similarity vs. Difference — Proposed Doctrine Statement

"Element and modality comparison should distinguish three cases: high similarity (ease, comfort, possible stagnation risk), complementary polarity (Air-Fire, Earth-Water: naturally enlivening), and challenging combination (Fire-Water, Air-Earth: requires conscious translation). Do not default to 'opposites attract' framing — sources consistently show this is appealing as a narrative but rarely produces sustained contentment in close, long-term relationships. Moon compatibility is the primary indicator of domestic ease and is distinct from erotic charge or intellectual rapport."

---

## Part 5 — Suggested Report Language Examples

These are example sentences demonstrating the voice arc applied to the new doctrine areas. Labeled as `[WEAK]` or `[STRONG]` per the existing voice guide.

---

**5th house overlay — WEAK:**
> "You have romantic compatibility through the 5th house, which rules fun and play."

**5th house overlay — STRONG:**
> "When you're together, there's a distinct sense that the ordinary becomes more enjoyable — that the two of you bring out something lighter and more playful in each other. This is a real romantic signal, even if it doesn't carry the weight of deeper commitment indicators. It's the 'I want to do things with you' feeling, which matters."

---

**7th house overlay (one-directional) — WEAK:**
> "Your planets in their 7th house indicate partnership potential."

**7th house overlay — STRONG:**
> "Something in how you show up seems to match what they've been unconsciously looking for in a partner — not just attraction, but recognition. They may feel, without being able to explain why, that you carry the qualities they want in someone they build a life with. Whether this becomes a relationship depends on what you bring to it; the overlay is a green light, not a guarantee."

---

**7th house overlay (reciprocal) — STRONG:**
> "You each land in the other's 7th house — the area of life where the partner-archetype lives. This is a mutual recognition, not just a one-sided pull. When this is reciprocal, it tends to mean both people are working with the same question: 'is this the one?'"

---

**8th house overlay — WEAK:**
> "This placement creates intense feelings and a strong physical connection."

**8th house overlay — STRONG:**
> "There's something about this person that makes the guarded parts of you feel accessible. What you normally keep private — the fears, the real desires, the things you don't say out loud — feels safer here. This isn't the same as everything being easy; it can also feel destabilizing to be this seen. But the access is real."

---

**Asc/Desc ruler swap (Ruiz pattern) — STRONG:**
> "The way this relationship is wired, each of you carries something the other has built their self-image around wanting. This is a rare configuration — it can create an unusually strong sense of 'this is what I've been looking for' from both directions."

---

**5th ruler contacted in synastry — STRONG:**
> "They activate your romance mode — not romance in the abstract, but the specific flavor of romance that's native to you: what you find playful, what makes you feel desire, how you naturally express affection. Their presence turns on something that's distinctly yours."

---

**Moon-to-Moon same element — STRONG:**
> "Your emotional rhythms are naturally compatible — you process feelings in recognizable ways to each other. This tends to show up as ease in daily contact: you don't have to explain yourselves as much, and small discomforts don't escalate into misunderstandings the way they might with less compatible Moons."

---

**Fire-Water element combination — STRONG:**
> "Fire and Water don't naturally speak the same language — one moves from action and optimism, the other from feeling and interiority. This doesn't mean incompatibility, but it does mean you'll often be in different modes at the same time, and understanding that will matter more than trying to convert each other."

---

**Mars-Saturn cross-aspect repair — STRONG:**
> "This works best when there's a conscious structure to how you direct energy together. The friction that shows up in spontaneous collaboration often disappears when one of you holds the map and the other moves. Try it as an explicit arrangement, not as a workaround."

---

**Composite Saturn conjunct Sun — STRONG:**
> "Saturn at the center of how this relationship identifies itself isn't a warning — it's a description. This relationship was never going to be light. It was built to carry something, and whether that's a shared commitment, a creative project, or simply the long slow work of knowing each other, there's a seriousness here that needs to be honored rather than fought. The question is whether the weight feels like meaning or burden."

---

**Composite 8th house emphasis — STRONG:**
> "This is a fateful relationship by nature — not in the sense that outcome is determined, but in the sense that both of you are likely to be changed by it. The 8th house in a composite chart means the relationship operates in the territory of transformation, depth, and things you don't talk about until you do. That's not a reason to be afraid of it. It's a reason to take it seriously."

---

## Part 6 — Suggested Test Assertions

These are behavioral assertions for future implementation testing. They describe what the system should do under specific input conditions. Written as natural-language test descriptions, not code.

---

**House overlay scoring:**

- `test_5th_house_overlay_personal_planet`: Given person A's Venus placed in person B's 5th house (by whole-sign or Placidus, specified by house system), the report should include overlay-layer content referencing the 5th house's romance/play activation, distinct from any Venus-aspect language.
- `test_7th_house_overlay_one_directional`: Given A's Sun in B's 7th house but B has no planets in A's 7th, the report should not use "mutual" or "reciprocal" language; it should note the one-directional quality ("they may feel this more than you do").
- `test_7th_house_overlay_reciprocal`: Given A's Sun in B's 7th AND B's Moon in A's 7th, report should include reciprocal overlay language and the overlay significance should be multiplied relative to the one-directional case.
- `test_8th_house_overlay_experiential_not_erotic`: Given A's Saturn in B's 8th house, the overlay language should reference depth/trust/access rather than defaulting to erotic language (Saturn is not a romance planet).
- `test_romantic_house_overlay_suppressed_without_birth_time`: Given unknown birth time (no house data), no overlay language should appear in the report. Test should confirm graceful degradation.

---

**Relationship-house ruler detection:**

- `test_5th_ruler_contact_detected`: Given person B's 5th house cusp in Gemini (Mercury rules the 5th) and person A's Venus conjunct person B's Mercury within 4°, the system should detect this as a 5th-ruler contact and apply the romance-axis context boost.
- `test_5th_ruler_contact_requires_birth_time`: Given no birth time for person B, no 5th-ruler context boost should be applied; test should confirm the boost is gated.
- `test_asc_desc_ruler_swap_both_directions`: Given A's Ascendant in Libra (Venus rules) and B's Descendant in Libra (so same ruler), AND B's Ascendant in Aries (Mars rules) and A's Descendant in Aries — the system should detect the reciprocal mirror pattern and apply the highest ruler-swap boost.
- `test_7th_ruler_reciprocal_cross_aspect`: Given A's 7th ruler (e.g., Pluto in Scorpio rising chart) in close trine to B's 7th ruler, the partnership-axis boost should apply AND an additional reciprocal bonus should apply if both rulers are involved.

---

**Composite chart configurations:**

- `test_composite_saturn_dedicated_step`: Given any composite chart, Saturn's house and aspects should be surfaced in the report as a distinct theme (not buried in general aspect list), consistent with Hand's Step 8 doctrine.
- `test_composite_outer_planet_angle_gating`: Given composite Uranus conjunct composite Ascendant within 5°, the Uranus-axis theme should appear in the report. Given composite Uranus in the 3rd house with no angular contact, Uranus should not surface as a primary theme.
- `test_composite_8th_house_sun_fateful_language`: Given composite Sun in the 8th house, report language should include transformation/depth/fateful framing, not generic "intense connection" filler.
- `test_composite_signs_not_primary_weight`: Given the same composite planet configuration in two different signs, the report should not change its primary themes based on sign alone (consistent with Hand's caveat about composite signs being uncertain).

---

**Similarity/difference analysis:**

- `test_fire_water_combination_language`: Given one person's Sun in Fire and the other's Sun in Water, report should not use "opposites attract" framing; should frame as "different modes that require conscious translation."
- `test_same_element_comfort_not_sufficient`: Given both people Sun in Earth signs, report should acknowledge ease/comfort but not claim this alone makes the relationship work well; should note vitality/novelty consideration.
- `test_moon_compatibility_domestic_framing`: Given both people's Moon in compatible elements (e.g., both Water), overlay language should focus on ease of daily contact, not abstract "emotional connection."
- `test_mercury_difference_neutral_framing`: Given Mercury in incompatible elements, report should not default to negative language; should offer "stimulating vs. friction" framing with repair note.

---

## Part 7 — What Not to Implement

The following items appeared in source material but should be explicitly excluded from Constellation, for reasons noted.

---

**1. Timing / love-planning features (all sources)**

Multiple sources (Ruiz: solar returns, progressions, lunations, eclipses; Arroyo: transits and predictive work; Davison: directions to synastry points) contain substantial timing doctrine. This is flagged explicitly by the user as **future/backlog, NOT MVP**. Do not implement transit-based relationship forecasting, Venus hour rituals, eclipse love timing, or any predictive-layer feature during this development phase. Capture the doctrine when source-reading; defer implementation.

---

**2. Composite house rulerships (Hand)**

[SOURCE — Hand, *Planets in Composite*, p. 32]: Hand explicitly states that in composite charts, signs may not function the same way as in natal charts, and that using sign-based house rulerships in composite is of "unknown" validity. Using composite sign placements to derive rulerships (e.g., "composite Gemini Ascendant rules Mercury") would introduce unreliable signal. Do not implement composite rulership logic. Composite house positions and aspects are reliable; sign-based composite rulerships are not.

---

**3. Minor aspects in synastry beyond quincunx (Arroyo)**

[SOURCE — Arroyo, *Person-to-Person Astrology*, pp. 366–367]: States that in the "vast majority of cases, the major aspects alone will yield far more data than you can ever incorporate" into an assessment. Minor aspects "contribute little toward a truly rewarding and incisive evaluation." This directly supports keeping the app's current aspect set (major aspects only, perhaps quincunx for specific patterns) and not expanding to semisextile, semisquare, sesquiquadrate, quintile etc. for the synastry layer.

---

**4. Computer-generated synastry readings without human nuance (Arroyo)**

[SOURCE — Arroyo, pp. 378–379]: Explicitly warns against computerized relationship compatibility assessments, which he describes as producing "deterministic, unrealistic, and usually wrong" impressions that short-circuit the discovery process. This is not a reason to stop building the app — but it is a doctrine warrant for: (a) never presenting Constellation's output as definitive or complete, (b) always framing findings as "tendencies and energies" rather than predictions, (c) including agency-affirming language in every report. Arroyo's warning is a voice/framing guideline, not a product prohibition.

---

**5. The "perfect balance of elements = ideal relationship" doctrine**

[SOURCE — Arroyo, pp. 111–112]: Explicitly refutes the idea that an ideal relationship should have one partner supply Fire/Earth and the other supply Water/Air to create perfect elemental balance. "Such people will often be so different that the gap between their particular types of consciousness and experience will grow wider with every year." Do not implement a compatibility score that treats elemental balance as the ideal. Same-element or adjacent-element emphasis = more reliable for sustained intimacy.

---

**6. Fully deterministic compatibility scores / "percentage match" outputs**

Multiple sources consistently warn against reducing relationship compatibility to a single score or percentage:
- Arroyo warns against "simplistic, black-and-white" assessments
- Hand emphasizes that every relationship fills a need that may be quite different from what appears on the surface
- Suskin frames repair-oriented readings as inherently nuanced

Do not implement a "compatibility percentage" or "match score" as a top-level output, even internally as a ranking tool visible to users. If scoring is needed internally for prioritization (which it is), keep it internal to the engine and present findings thematically.

---

**7. Davison-chart (different from midpoint composite) as primary relationship chart**

The Ronald Davison *Synastry* book reviewed here is about synastry cross-aspects — not the Davison relocation chart (a different technique also named after him, using the midpoint date/location as a new birthtime). The Davison relocation composite is a distinct, more complex technique that requires additional calculation and has less supporting doctrine in the sources reviewed. Stick with the midpoint composite (Hand's technique) as the composite layer. Do not implement the Davison relocation chart for MVP.

---

*End of Second Research Pass — Notes & Doctrine Proposals.*

*Sources cited: Ruiz (Prediction Techniques Regarding Romance), Davison (Synastry: Understanding Human Relations Through Astrology), Suskin (Synastry: Understanding the Astrology of Relationships), Arroyo (Person-to-Person Astrology), Eddington (Top 10 Best Synastry Aspects), Hand (Planets in Composite). All material paraphrased per copyright rules; no verbatim excerpts included.*
