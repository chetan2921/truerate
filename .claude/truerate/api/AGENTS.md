# api

The Python service: collects Instagram data, runs the audience checks, prices one reel, and serves the results to `web/`.

## Stack
- Python 3.12, pinned in `api/.python-version` and managed by uv. The machine's default Python is 3.14; never use it here.
- FastAPI, uvicorn, pymongo, pydantic-settings, httpx, typer (CLI), scikit-learn and joblib. Tests: pytest, mongomock.
- Later milestones add networkx, sentence-transformers, mediapipe and google-genai (spec, Stack table).

## Run
- `make api` from the repo root: http://localhost:8000, docs at `/docs`
- `make test`: `uv run pytest -q`
- CLI, from `api/`: `uv run truerate --help`
  - `import-deals`: `data/creators.csv` into `deals`, 30 held out
  - `build-fake-model`: trains on `data/external/instagram_fake/`, saves `data/models/fake_accounts.joblib`
  - `collect <handle>`: one snapshot, about 20 HikerAPI requests
  - `collect-benchmark`: every deal creator not fetched in the last 24 h; stops on HTTP 402 (credit gone)

## Entry points
- `truerate/app.py`: the FastAPI `app` and its routes
- `truerate/cli.py`: the `truerate` Typer command (data, model and validation jobs)
- `truerate/db.py`: `get_db()` from `MONGODB_URI`, `ensure_indexes()` (24 h TTL on `cache`, 30 d on `accounts`, unique `deals.handle`), `import_deals()`
- `truerate/instagram.py`: `Hiker` (HikerAPI client, parsed responses cached in `cache`), the `parse_*` functions, `mark_pinned()`, `collect()` (one snapshot)
- `truerate/signals.py`: the Kaggle fake-account model (`account_features`, `train_fake_model`, `fake_share`)
- `truerate/config.py`: `Settings` loaded from the repo-root `.env`

## Folder map
- `truerate/`: the package. The one-file-per-job layout it grows into is in `.claude/plan/truerate/SPEC.md`, Architecture.
- `tests/`: pytest. `conftest.py` has the mongomock `db` fixture. `tests/fixtures/` holds one recorded HikerAPI response per endpoint.

## Sharp edges
- Unit tests never touch the real Mongo cluster (use mongomock), HikerAPI (use `fake_hiker` in `tests/test_instagram.py`) or Gemini (use a fake).
- Fixtures come from public accounts that aren't in WLDD's deals, trimmed, with every other account renamed. The repo is public.
- Deal prices never go into an LLM prompt.
- HikerAPI credit is limited. `GET /sys/balance` is free: check it before and after a live run. Free tier: 1 request per second.
- `cache` stores parsed results, not raw JSON (a likers call is 1.4 MB raw). After changing a parser, clear `cache` or wait 24 h.
- Views are `play_count`; `view_count` is always 0. Pinned reels have no flag; `mark_pinned` finds them by date order. Instagram shows only the 25 to 50 newest followers.
- Response models are part of the api-surface contract. Change one, then regenerate the web types.

<!-- mapped: .@39dc687 | paths: api/ -->
