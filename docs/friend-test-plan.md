# Friend-Test Plan

## Tester Journey
1. Add Person A with birth date/time.
2. Search birthplace (city/state or city/country), pick a search result, and confirm timezone + coordinates autofill.
3. Add Person B and repeat birthplace search/selection.
4. Save relationship.
5. Generate report.
6. Open Constellation View and generate reports from saved relationships.

## City Lookup Notes
- Birthplace search calls backend `/places/search`.
- When `GEOAPIFY_API_KEY` (or `GEOCODING_API_KEY`) is configured, live search should return city matches.
- Without a provider key, built-in presets still work and manual timezone/latitude/longitude entry remains available.
- If no result appears, testers should try a broader query (e.g., `Austin, TX` -> `Austin Texas`) or use manual fields.

## Relationship Map Notes
- Unknown birth time is supported (`Time known? = No`) with reduced house/angle reliability.
- Reports are deterministic prototype output, not final narrative quality.
- Constellation View shows saved relationships and lets tester regenerate reports from those saved relationships.

## Known Limits
- No auth/accounts yet.
- SQLite prototype persistence only.
- No compatibility scoring.
- No payments/chat/journaling systems.

## Feedback Questions
- Was birthplace search easy to understand without guidance?
- Did search result selection feel obvious?
- Were fallback messages clear when live provider search was unavailable?
- Could you complete save relationship + generate report + regenerate from Constellation View?
- Which copy/UI labels still felt too technical?
