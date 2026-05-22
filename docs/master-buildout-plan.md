# Constellation Master Buildout Plan

## Product Thesis

Constellation is not a compatibility-score app.

It is a relational observatory: a place where users map important relationships, understand the field of activation between people, track what is being stirred over time, and receive practical language for reflection, repair, timing, and decision-making.

The core product should help users answer:

- What part of me becomes activated in contact with this person?
- What is the relationship itself trying to become?
- Where is there attraction, recognition, safety, friction, or pressure?
- What is surface-level chemistry versus the deeper engine?
- What is being activated now?
- What kind of repair, reflection, or response is possible?

## Product Doctrine

Do not build:

- compatibility scores
- good match / bad match verdicts
- deterministic fate claims
- trauma predictions
- moralized red-flag language
- meant-to-be conclusions

Do build:

- relationship maps
- confidence notes
- chart-backed evidence
- pattern language
- timing context
- practical repair paths
- user reflection and journaling
- optional divination as reflective support, not deterministic command
- a bridge from automated insight into deeper study and, later, human work

## Core Interpretive Principles

- Exactness matters more than volume.
- Strong contact is not the same as healthy contact.
- Intensity is not the same as safety.
- Composite chart describes the relationship as its own field or being.
- Synastry describes mutual activation.
- House overlays show where one person enters another person’s life terrain.
- Soft aspects facilitate connection and can amplify other patterns.
- Saturn can stabilize or constrain.
- South Node can indicate familiarity, conditioning, or old patterning.
- North Node can indicate hunger, desire, ambition, or growth.
- The map cannot override lived reality.

## Six-Month Target Scenario

Assume:

- 10,000 people have tried the app.
- 100 users are paying $13/month.
- Revenue is roughly $1,300/month before fees, infrastructure, support, and taxes.

This is validation, not stability.

The risk is that the app becomes interesting enough to create demand but not structured enough to retain users, support them, or reduce founder burden.

## Likely Six-Month Problems

### 1. One-Time Novelty

Users generate a report, feel recognition, and leave.

Solution:

- saved relationships
- weekly activation/timing layer
- journal prompts
- transit/progression alerts to relationship points
- recurring relational weather
- reflection history

### 2. Too Much Insight, Not Enough Action

Long reports may be beautiful but overwhelming.

Solution:

Every report should have layers:

1. Quick Read
2. Core Dynamic
3. What Pulls You Together
4. What Gets Hard
5. Repair Path
6. Deep Dive
7. Technical Evidence

### 3. Users Want Verdicts

Users will ask whether to stay, leave, trust, return, commit, or detach.

Solution:

- explicit non-verdict design
- decision-support boundaries
- safety-sensitive language
- lived behavior as final authority
- prompts that return agency to the user

### 4. Edge-Case Hell

Common issues:

- unknown birth times
- approximate times
- birthplace ambiguity
- timezone disagreements
- chart discrepancies with other sites
- house system questions
- emotionally charged ex/affair/trauma use cases

Solution:

- confidence scoring
- visible data-quality notes
- support docs
- chart validation fixtures
- clear house/angle limitations

### 5. Interpretive Drift

The framework will evolve.

Solution:

- version the interpretation engine
- store report generation version
- preserve old reports with their original engine version
- test major interpretive changes against known fixtures

### 6. Flying Blind

Without analytics, it will be unclear why users subscribe or churn.

Solution:

Track non-invasive events:

- report generated
- relationship type selected
- birth-time confidence
- section expanded/clicked
- copy/download clicked
- chat started
- divination used
- saved relationship revisited
- subscription conversion/cancellation

### 7. Support Burden

Users will ask why charts differ, how to cancel, how to interpret lines, and whether the app is telling them to make life decisions.

Solution:

Create help docs early:

- What if I don’t know my birth time?
- Why does my chart differ from another site?
- Does this tell me if we’re compatible?
- Can this predict abuse or trauma?
- How do I delete my data?
- How do subscriptions work?

## Product Tiers

### Free Trial / Free Mode

Purpose: lead generation and product education.

Possible limits:

- one relationship map
- limited report sections
- no saved history or limited saved relationships
- no ongoing timing layer
- no AI relationship chat
- no divination integrations

### $13/month Core Tier

Purpose: self-guided relational observatory.

Features:

- saved relationships
- full Relationship Field Maps
- report regeneration when context changes
- relationship context updates
- core timing / relational weather
- journal/reflection prompts
- Markdown/PDF export eventually
- basic history

### $29/month Deep Dialogue Tier

Purpose: ongoing interactive relationship work.

Features:

- everything in Core
- AI chat about relationship patterns
- chat grounded in saved relationship maps, user journals, timing, and chart evidence
- optional Tarot integration
- optional Lenormand integration
- optional I Ching integration
- deeper transit/progression timing
- recurring reflection practices
- more saved relationships
- advanced exports

Important boundary:

The AI chat should be framed as reflective pattern dialogue, not therapy, not crisis counseling, and not deterministic decision-making.

### Later Human-Bridge Tier / Ecosystem

This may come later, not immediately.

Potential bridges:

- book a reading
- bring this map to a session
- relationship astrology course
- composite chart guide
- monthly relational weather workshop
- practitioner version
- reading preparation tool

This should not be rushed until the self-serve product loop is stable.

## AI Chat Feature

### Product Role

The AI chat is likely the key retention layer.

A static report answers:

> What is the pattern?

A chat answers:

> How is this pattern showing up in my life right now?

### What Chat Should Know

The chat should be grounded in:

- user profile
- saved relationships
- natal charts
- synastry patterns
- composite patterns
- house overlays
- relationship context
- prior generated reports
- user journal entries
- timing layer
- optional divination history

### What Chat Should Not Do

The chat should not:

- make definitive relationship decisions for the user
- diagnose abuse or trauma from astrology
- encourage dependency
- replace therapy or emergency support
- imply that divination commands action
- invent chart evidence not present in the calculation data

### Suggested Chat Modes

1. Explain this pattern
2. What is being activated right now?
3. Help me reflect before I message them
4. What is the repair path?
5. What am I projecting?
6. What should I journal about?
7. Compare this person to another relationship pattern
8. Ask Tarot / Lenormand / I Ching as a reflection layer

### Chat Memory Rules

The chat should cite or reference the specific relationship map it is using.

It should distinguish:

- chart-derived pattern
- user-entered context
- journaled experience
- divination result
- generated interpretation
- model inference

## Divination Layer

Divination can be powerful if framed correctly.

It should be a reflective layer, not an oracle that overrides user judgment.

### Possible Tools

- Tarot
- Lenormand
- I Ching

### Product Framing

Divination asks:

- What image helps me reflect on this moment?
- What pattern wants attention?
- What is the dao of this situation?
- What stance would be wise?

It should not ask:

- Will they come back?
- Are they my soulmate?
- Should I ignore all lived evidence?

### Data to Store

For every divination session:

- relationship_id if applicable
- question
- system used: tarot, lenormand, i_ching
- spread/cast details
- generated interpretation
- user notes
- timestamp
- linked report/timing context if applicable

## Data Architecture Principles

### Separate Calculation Data from Generated Prose

Do not make the generated report the source of truth.

Source of truth should be structured data:

- birth records
- chart placements
- aspects
- overlays
- composite placements
- detected patterns
- relationship context
- engine version

Reports and chats are outputs generated from structured data.

### Version Everything That Can Change

Version:

- calculation engine
- interpretation engine
- pattern detector set
- report template
- AI prompt pack
- divination interpretation template

### Preserve User Trust

Relationship data is sensitive.

Users should eventually be able to:

- delete birth data
- delete relationships
- delete reports
- delete chat history
- export their data
- understand what is stored

### Store Confidence and Provenance

Every major output should know:

- what birth data was used
- whether birth time was known
- what house system was used
- what geocoding source was used
- what interpretation engine version was used
- what report version was used

## Suggested Core Database Tables

### users

- id
- email
- created_at
- subscription_status
- subscription_tier
- privacy_preferences

### birth_profiles

Represents a person in the user’s constellation.

- id
- user_id
- display_name
- birth_date
- birth_time
- time_known
- latitude
- longitude
- timezone
- birthplace_label
- geocoding_source
- created_at
- updated_at

### charts

Stores calculated chart output or cache.

- id
- birth_profile_id
- house_system
- calculation_engine_version
- placements_json
- angles_json
- houses_json
- warnings_json
- created_at

### relationships

Represents a relationship field between two birth profiles.

- id
- user_id
- person_a_birth_profile_id
- person_b_birth_profile_id
- relationship_type
- status
- user_question
- origin_story
- known_themes_json
- created_at
- updated_at

### relationship_calculations

Structured astrology data for a relationship.

- id
- relationship_id
- house_system
- calculation_engine_version
- synastry_aspects_json
- house_overlays_json
- composite_chart_json
- composite_aspects_json
- confidence_json
- created_at

### detected_patterns

Structured pattern outputs from rule engine.

- id
- relationship_calculation_id
- pattern_detector_version
- pattern_key
- layer
- category
- priority
- confidence
- evidence_json
- created_at

### reports

Generated prose output.

- id
- relationship_id
- relationship_calculation_id
- interpretation_engine_version
- report_template_version
- markdown
- summary_json
- created_at

### journal_entries

User reflection layer.

- id
- user_id
- relationship_id nullable
- title
- body
- mood_tags_json
- activation_tags_json
- created_at
- updated_at

### chat_threads

- id
- user_id
- relationship_id nullable
- chat_mode
- created_at
- updated_at

### chat_messages

- id
- chat_thread_id
- role: user/assistant/system/tool
- content
- source_context_json
- model_name
- prompt_version
- created_at

### divination_sessions

- id
- user_id
- relationship_id nullable
- system: tarot/lenormand/i_ching
- question
- cast_json
- interpretation
- linked_chat_thread_id nullable
- created_at

### timing_events

For transits/progressions/relationship weather.

- id
- relationship_id
- timing_system
- event_key
- exact_at
- orb_start
- orb_end
- description
- created_at

### analytics_events

Non-invasive product analytics.

- id
- user_id nullable
- anonymous_id nullable
- event_name
- properties_json
- created_at

## Development Phases

### Phase 0 — Current Prototype

- chart calculation
- synastry
- composite
- house overlays
- pattern detection
- deterministic report
- FastAPI
- web form
- manual/preset/geocode-ready place handling

### Phase 1 — Tester-Ready Web Prototype

- static UI refactor
- better error display
- sample relationship presets
- export metadata
- report section tests
- deployment readiness

### Phase 2 — Accounts and Saved Relationships

- auth
- users
- saved birth profiles
- saved relationships
- saved reports
- delete/export data basics
- basic subscription infrastructure

### Phase 3 — Recurring Use Loop

- relationship dashboard
- weekly relational weather
- timing to relationship points
- journal prompts
- revisit reports over time
- section expansion/collapse analytics

### Phase 4 — AI Relationship Chat

- chat grounded in saved relationship data
- source-aware context retrieval
- chat modes
- safety/decision boundaries
- chat history
- prompt versioning
- $29 tier candidate

### Phase 5 — Divination Integrations

- Tarot
- Lenormand
- I Ching
- divination sessions linked to relationship context
- reflective framing
- saved divination history

### Phase 6 — Human Work Bridge

Later stage.

- reading booking bridge
- course upsells
- practitioner guide
- educational content
- bring-this-map-to-session workflow

## Near-Term Build Priorities

1. Finish tester-ready web UI refactor.
2. Add report hierarchy: quick read, core dynamic, deep dive.
3. Add report metadata/versioning.
4. Add data model docs and migration plan.
5. Add saved relationship architecture, even before full auth.
6. Add privacy/delete/export plan.
7. Add analytics event plan.
8. Add AI chat architecture doc.
9. Add divination architecture doc.
10. Deploy only when the tester flow is coherent.
