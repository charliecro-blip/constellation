# Deployment Checklist

This checklist is for the first public/mobile-testable prototype deployment.

## Before Deploying

- Confirm GitHub Actions is green.
- Confirm `/health` passes locally or in hosted logs.
- Confirm the web UI loads at `/`.
- Confirm `/places/search?q=Austin` returns a response even without a provider key.

## Required Hosting Settings

Use the repository's existing `render.yaml` settings if deploying to Render.

Build command:

```bash
python -m pip install --upgrade pip && pip install -e .
```

Start command:

```bash
uvicorn constellation_core.api:app --host 0.0.0.0 --port $PORT
```

Health check path:

```text
/health
```

## Environment Variables

Required:

```text
PYTHON_VERSION=3.11.9
```

Optional but recommended for real place search:

```text
GEOAPIFY_API_KEY=<paste in host settings, never commit to GitHub>
```

The app also accepts:

```text
GEOCODING_API_KEY=<paste in host settings, never commit to GitHub>
```

## Smoke Test After Deployment

Open the deployed URL on desktop and mobile.

1. Confirm homepage loads.
2. Search Person A place: Austin, TX.
3. Select a result.
4. Confirm latitude, longitude, and timezone autofill.
5. Generate report.
6. Confirm report preview appears.
7. Copy Markdown.
8. Open `/docs` and confirm API docs load.
9. Open `/health` and confirm `{"status":"ok"}`.

## Known Prototype Limits

- No accounts.
- No saved reports.
- No payments.
- No polished final design.
- Geocoding is provider-dependent unless using built-in presets.
- Historical timezone handling needs validation against known birth charts.
- Report language is still deterministic and early-stage.
