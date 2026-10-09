# api

The Python service: collects Instagram data, runs the audience checks, prices one reel, and serves the results to `web/`.

## Stack
- Python 3.12, pinned in `api/.python-version` and managed by uv. The machine's default Python is 3.14; never use it here.
- FastAPI, uvicorn, pymongo, pydantic-settings, httpx, typer (CLI). Tests: pytest, mongomock.
- Milestones 2–3 add scikit-learn, networkx, sentence-transformers, mediapipe and google-genai (spec, Stack table).

## Run
- `make api` from the repo root: http://localhost:8000, docs at `/docs`
- `make test`: `uv run pytest -q`
- CLI: `cd api && uv run truerate --help` (for example `uv run truerate import-deals`, which defaults to `data/creators.csv`)

## Entry points
- `truerate/app.py`: the FastAPI `app` and its routes
- `truerate/cli.py`: the `truerate` Typer command (data, model and validation jobs)
- `truerate/db.py`: `get_db()` from `MONGODB_URI`, `ensure_indexes()` (24 h TTL on `cache`, 30 d on `accounts`, unique `deals.handle`), `import_deals()`
- `truerate/config.py`: `Settings` loaded from the repo-root `.env`

## Folder map
- `truerate/`: the package. The one-file-per-job layout it grows into (`db.py`, `instagram.py`, `signals.py`, `pricing.py`, `pipeline.py`, `cli.py`) is in `.claude/plan/truerate/SPEC.md`, Architecture.
- `tests/`: pytest. Recorded HikerAPI JSON goes in `tests/fixtures/`.

## Sharp edges
- Unit tests never touch the real Mongo cluster (use mongomock), HikerAPI (use recorded fixtures) or Gemini (use a fake).
- Fixtures come from public accounts that aren't in WLDD's deals. The repo is public.
- Deal prices never go into an LLM prompt.
- Response models are part of the api-surface contract. Change one, then regenerate the web types.

<!-- mapped: .@4644762 | paths: api/ -->
