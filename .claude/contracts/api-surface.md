# API surface

| Side | Files |
|------|-------|
| server | `api/truerate/app.py` routes and the Pydantic response models they declare |
| client | `web/src/lib/api.ts` (fetch calls) and `web/src/lib/api-types.ts` (generated from `http://localhost:8000/openapi.json` with `openapi-typescript`) |

Change a route or a response model, then regenerate `api-types.ts` and fix `api.ts` in the same session. The client fails at runtime, not at build time, when a field is renamed.
