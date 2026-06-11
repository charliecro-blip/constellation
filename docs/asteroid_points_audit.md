# Asteroid and relationship point calculation audit

This audit records the current calculation surface only. It is intentionally not a new interpretive policy for relationship reports.

## Currently calculated

The calculation engine can request Swiss Ephemeris positions for these relationship-relevant asteroids and points when ephemeris data is available:

- Chiron (`swe.CHIRON`)
- Juno (`swe.JUNO`)
- Ceres (`swe.CERES`)
- Vesta (`swe.VESTA`)
- Psyche (`swe.AST_OFFSET + 16`)
- Eros (`swe.AST_OFFSET + 433`)

If asteroid ephemeris data is unavailable, the chart calculator omits those bodies and adds a calculation warning instead of fabricating positions.

## Current report policy

This pass does not add new asteroid doctrine or new asteroid-led report sections. Existing calculation support remains available for deterministic tests and future policy work, but asteroid interpretation should stay subordinate to luminaries, angles, personal planets, Saturn/Pluto, house overlays, and composite anchors until the separate synastry/romance research process produces a fuller policy.

## Needed before expanding asteroid interpretation

Before Chiron, Juno, Ceres, Vesta, Psyche, or Eros become primary report material, the project should define:

1. Which relationship contexts can use each point.
2. Which aspects and orbs are allowed for each point.
3. Whether natal, synastry, composite, and overlay uses differ.
4. Priority limits so asteroid contacts cannot outrank stronger luminary, angle, personal-planet, Saturn/Pluto, or composite signatures by exactness alone.
5. Copy rules that avoid fate language, compatibility scoring, and overclaiming from a single minor point.
6. Tests proving asteroid signatures remain supporting texture unless repeated with major relationship signatures.
