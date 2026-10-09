.PHONY: api web test

api:
	cd api && uv run uvicorn truerate.app:app --reload --port 8000

web:
	cd web && npm run dev

test:
	cd api && uv run pytest -q
