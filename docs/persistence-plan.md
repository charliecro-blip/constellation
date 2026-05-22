# Persistence plan (groundwork)

Constellation treats reports as outputs, not source of truth. The durable source should be reusable people records and relationship anchors.

## Model direction

- **BirthProfile** stores reusable people and their chart input data.
- **SavedRelationship** is the anchor object that links two birth profiles plus relationship context.
- **SavedReport** stores versioned markdown outputs generated from a saved relationship.

## Why this shape

- Reports can be regenerated when calculation or interpretation engines improve.
- Birth profiles can be reused across many relationships over time.
- Saved relationships preserve context and become the base for future journaling/chat/timing layers.

## Future tables (not included in this handoff)

- Journal entries
- Chat threads and messages
- Divination sessions
- Timing events
- Analytics events

## Privacy and lifecycle

- Future phases should include export and delete flows.
- User-scoped data controls become critical once authentication exists.

## Versioning

Saved reports include calculation, interpretation, and template version fields so output provenance remains explicit over time.
