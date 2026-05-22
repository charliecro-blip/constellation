# Secrets and Environment Variables

Do not commit real API keys to GitHub.

## Geocoding

Constellation supports a provider-optional geocoding layer. The app works without a key using built-in place presets. When a geocoding key is available, set it in the deployment provider as an environment variable.

Supported variable names:

```text
GEOAPIFY_API_KEY
```

or:

```text
GEOCODING_API_KEY
```

## Local Development

For local development, create a private environment file and do not commit it. The repository includes `.env.example` as a template only.

## Deployment

For Render or another host:

1. Open the service settings.
2. Go to Environment.
3. Add `GEOAPIFY_API_KEY`.
4. Redeploy.

The frontend should never receive the raw key. Browser requests go to the backend endpoint `/places/search`, and the backend calls the provider.
