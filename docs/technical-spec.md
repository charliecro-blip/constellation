# Technical Spec — Constellation MVP

## Goal
Build a calculation-first relational astrology prototype.

The first engineering milestone is:

> Birth data in → natal placements out → synastry/composite JSON out.

Interpretation should come after calculation correctness.

## MVP Scope

### Phase 0 — Natal Calculation Spike
Accept:
- name
- birth date
- local birth time
- latitude
- longitude
- IANA timezone
- house system

Return:
- planetary longitudes
- signs and degrees
- Ascendant and MC when birth time is known
- houses when birth time is known
- normalized JSON

### Phase 1 — Relationship Calculation
Given two calculated natal charts:
- detect synastry aspects
- detect house overlays when houses are available
- calculate midpoint composite placements
- calculate composite aspects
- output relationship JSON

### Phase 2 — Signature Detection
Turn raw chart data into ranked signatures:
- angular contacts
- luminary contacts
- Venus/Mars contacts
- Mercury polarities
- Moon/Saturn and Moon/Pluto patterns
- Juno/Saturn/Uranus/Chiron patterns later
- composite Moon, Sun, Venus, Mars, Saturn emphasis
- composite high-intensity patterns

### Phase 3 — Report Generation
Generate a structured Relationship Field Map:
1. Archetype / Title
2. Bird's-Eye View
3. Individual Relational Profiles
4. Mutual Activation
5. Desire & Affection
6. Emotional Safety
7. Communication
8. Partnership Pattern
9. The Field Between You
10. Surface vs Engine
11. Friction Loop
12. Repair Path
13. One-Sentence Summary

## Calculation Requirements

### Required Bodies
- Sun
- Moon
- Mercury
- Venus
- Mars
- Jupiter
- Saturn
- Uranus
- Neptune
- Pluto
- North Node
- South Node derived from North Node
- Ascendant when birth time is known
- Midheaven when birth time is known

### Later Bodies
- Chiron
- Juno
- Ceres
- Pallas
- Vesta
- Lilith
- Part of Fortune
- fixed stars

## House System
Store the house system in chart metadata. The first calculation core supports at least:
- Whole Sign
- Placidus, if available through the calculation backend

Interpretive doctrine should not be hard-coded to one house system.

## Design Principle
The calculation layer must be deterministic and testable. The interpretation layer should consume normalized chart/signature JSON, not raw ephemeris calls.
