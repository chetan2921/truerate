.PHONY: api web test types

api:
	cd api && uv run uvicorn truerate.app:app --reload --port 8000

web:
	cd web && npm run dev

test:
	cd api && uv run pytest -q

# Regenerate the web types from the API schema (api-surface contract)
types:
	cd api && uv run python -c "import json; from truerate.app import app; print(json.dumps(app.openapi()))" > ../web/openapi.json
	cd web && npx openapi-typescript openapi.json -o src/lib/api-types.ts
