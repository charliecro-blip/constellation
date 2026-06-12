# Architecture Map

This map links the astrology doctrine to the modules that implement or consume it.

- `packages/astro-core/constellation_core/pattern_registry.py` — categories, tiers, default report sections, pattern descriptions, and lead eligibility.
- `packages/astro-core/constellation_core/scoring_weights.py` — tier weights, suppression thresholds, orb/aspect/body/house emphasis, and convergence constants.
- `packages/astro-core/constellation_core/weighting.py` — context-aware weighted pattern ranking, convergence adjustments, and communication/public-life exceptions.
- `packages/astro-core/constellation_core/report.py` — report construction, chart check, diagnostics, synthesis packet creation, asteroid surfacing, and lead-theme selection.
- `packages/astro-core/constellation_core/interpretations.py` — deterministic interpretation text used before optional prose enhancement.
- `packages/astro-core/constellation_core/ai_enhancement.py` — prose enhancement prompt that rewrites and synthesizes without calculating astrology.
- `packages/astro-core/constellation_core/asteroid_policy.py` — asteroid defaults, supported advanced points, central targets, relevant houses, and default orb.
- `packages/astro-core/constellation_core/motifs.py` — persisted structured relationship motifs selected from the deterministic synthesis packet.
- `packages/astro-core/constellation_core/constellation_patterns.py` — aggregate recurring motifs across saved relationships.
- `packages/astro-core/constellation_core/static/app.js` — frontend report panel display for generated reports and diagnostics.
