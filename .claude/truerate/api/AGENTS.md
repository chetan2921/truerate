# api

The Python service: collects Instagram data, runs the audience checks, prices one reel, and serves the results to `web/`.

## Stack
- Python 3.12, pinned in `api/.python-version` and managed by uv. The machine's default Python is 3.14; never use it here.
- FastAPI, uvicorn, pymongo, pydantic-settings, httpx, typer (CLI). Tests: pytest, mongomock.
- Experiments only: TabPFN in the `experiments` dependency group (`uv run --group experiments ...`), pinned to the v2 weights, whose licence (Apache 2.0 with attribution) allows commercial use; the package's default weights don't. Local CPU only, never the cloud client, so WLDD's prices stay on this machine.
- Models: scikit-learn (Ridge, RandomForest, IsolationForest), numpy, joblib, networkx (Louvain), sentence-transformers (MiniLM), mediapipe + pillow (faces), google-genai (Gemini).

## Run
- `make api` from the repo root: http://localhost:8000, docs at `/docs`
- `make test`: `uv run pytest -q`
- CLI, from `api/`: `uv run truerate --help`. In pipeline order:
  - `import-deals`: `data/creators.csv` into `deals`, 30 held out
  - `build-fake-model`: trains on `data/external/instagram_fake/`, saves `data/models/fake_accounts.joblib`
  - `collect <handle>`: one snapshot, about 21 HikerAPI requests
  - `collect-benchmark --workers 12`: every deal creator not fetched in the last `--fresh-hours` (24); a failed creator is skipped, HTTP 402 (credit gone) stops the run. `--fresh-hours 0` re-snapshots everyone from the saved responses
  - `build-metrics --workers 4`: per deal creator, Gemini labels (in parallel), reel metrics, category, audience signals and commenter mix, then Louvain rings over all of them
  - `validate`: writes `data/models/model_report.json` (no handles or prices) and the served `data/models/price.joblib`
  - `redteam`: writes `data/models/redteam.json`
  - `experiment`: model v2 experiments, changing nothing served. Candidates are picked by repeated 5×10-fold CV on the 118 training deals only, then scored once on the 30 held out and on the fresh deals in `data/fresh_test_20.csv`, whose features are rebuilt from their stored analyses. Writes `data/models/experiments/`: `table.md`, `results.json` and the graphs. `--points today,ridge_v2` limits the candidates; TabPFN joins when the `experiments` group is installed. About 10 minutes without TabPFN and 50 with it; run TabPFN only with the servers stopped (8 GB Mac).
- Dev data for building screens before the 150 exist: `uv run python scripts/seed_dev.py` fills the `truerate_dev` database and `data/models_dev/` with synthetic analyses, a batch, a price model and both reports. Then run the API with `MONGODB_DB=truerate_dev MODELS_DIR=data/models_dev`.

## Entry points
- `truerate/app.py`: the FastAPI `app`, the routes (analyses, quote, batches, rate card, meta, model report), the Pydantic models (the api-surface contract), and the background job (`submit`, `_start`, `make_deps`, `_run`)
- `truerate/pipeline.py`: `analyze(handle, inputs, deps, step)`: one creator to report, with `Deps` for every outside service so tests swap them; `check_quote(report, quote)`
- `truerate/cli.py`: the `truerate` Typer command
- `truerate/db.py`: `get_db()`, `ensure_indexes()` (30 d TTL on `accounts`, unique `deals.handle`), `import_deals()`, `training_rows()`
- `truerate/instagram.py`: `Hiker` (HikerAPI client; every raw response saved once under `HIKER_DIR` and kept), the `parse_*` functions (including `parse_tagged` and each reel's `repost_of`), `mark_pinned()`, `collect()` (403 and 404 on list endpoints count as empty), `fetch_covers()`
- `truerate/signals.py`, in file order:
  - fake-account model (`account_features`, `train_fake_model`, `fake_share`)
  - `CATEGORIES`, `is_paid`, `recent_reels`, `reel_metrics`, `label_niche`
  - `band`, MiniLM `comment_signals`, `audience_signals`, `AUDIENCE_SIGNALS`, `band_norms`, `verdict`, `genuine_share`
  - `make_fake` and `redteam`
  - `ambiguous`, `label_creator` (Gemini), `commenter_mix`, `face_share`, `commenter_rings` (Louvain), `fit_anomaly` and `audience_warnings`
- `truerate/pricing.py`: `fit()` gives a `PriceModel`; `price()` gives the range, waterfall, comparables, delivery and an out-of-range `note`; `collab_factor` (bounded 0.5–1.0); `validate()` (with predicted-vs-actual points, no handles); the two baselines; `rate_card()` (3+ deals per category); `inr()` and `_group()` (Indian grouping)
- `truerate/experiment.py`: `extra_features` (account age, reel length, posting rate, YouTube link, contact email, verified), `deal_rows`, `fresh_rows` (rebuilds a stored analysis's exact metrics from its snapshot and listed paid reels), the candidates (`POINT_FNS`; signed split-conformal ranges at 80% and 50%, global or per follower band), `repeated_cv`, `pick`, `beats`, `run`, `learning_curve`, `importance` (exact linear SHAP) and `report_table`. `experiment_plots.py` draws the graphs (matplotlib, dark theme).
- `truerate/outputs.py`: `outputs(result, inputs)`, the plain verdicts (key, status good/warn/bad/info, title, detail), worked out on every read, so older analyses get them too.
- `truerate/webcheck.py`: `web_rate(llm, handle, full_name, followers, category)`, a Google-grounded Gemini search for a big creator's own stated rate; found only when readable, plausible and sourced.
- `truerate/llm.py`: `Gemini.json(prompt, schema, images)` and `Gemini.search(prompt)` (Google Search grounding, returns text and sources)
- `truerate/config.py`: `Settings` from the repo-root `.env`; `MODELS_DIR` (env `MODELS_DIR` overrides, relative to the repo root); `HIKER_DIR` (`data/hikerapi/`)

## Folder map
- `truerate/`: the package. The file-per-job layout is in `.claude/plan/truerate/SPEC.md`, Architecture.
- `scripts/seed_dev.py`: the dev seed above. It imports the tests' synthetic helpers.
- `scripts/make_deck.py`: the pitch deck from `model_report.json` and `redteam.json` (and `data/pitch/report.png` if present) into `data/pitch/TrueRate.pptx`. `--models-dir data/models_dev` for a draft.
- `tests/`: pytest. `conftest.py` has the mongomock `db` fixture. `tests/fixtures/` holds one recorded HikerAPI response per endpoint.

## Sharp edges
- Unit tests never touch the real Mongo cluster (mongomock), HikerAPI (`fake_hiker` in `tests/test_instagram.py`), Gemini (`FakeLLM`, `SchemaLLM`) or MiniLM (`fake_embed` in `tests/test_audience.py`).
- Fixtures come from public accounts that aren't in WLDD's deals, trimmed, with every other account renamed. The repo is public.
- Deal prices never go into an LLM prompt; the build-metrics test checks this.
- HikerAPI credit is limited. `GET /sys/balance` is free: check it before and after a live run. Free tier: 1 request per second.
- HikerAPI responses live on disk in `data/hikerapi/<endpoint>/<params>-<hash>.json.gz`: raw, gzipped (about 600 KB per creator), kept with no expiry, so each call is paid for once and a parser change needs no new request. Fresh data for a creator means deleting their files; a refresh option is for after the hackathon. Never in Mongo.
- Don't sort the whole `snapshots` collection: Atlas refuses an in-memory sort that large. Read per handle through the `(handle, fetched_at)` index.
- Views are `play_count`; `view_count` is always 0. Pinned reels have no flag; `mark_pinned` finds them by date order. Instagram shows only the 25 to 50 newest followers.
- First use downloads models: MiniLM (about 470 MB, Hugging Face cache) and BlazeFace (`data/models/blaze_face_short_range.tflite`).
- `build-metrics` reuses a creator's stored Gemini labels while the snapshot is the same (`labels_for`). A new snapshot means a new labelling call.
- Gemini: `gemini-2.5-flash` is closed to new keys; the default is `gemini-3.8-flash`. Keep the `genai.Client` on an object, or the SDK closes its connection mid-call.
- `PriceModel` is pickled into `data/models/price.joblib`; rerun `truerate validate` after changing its fields.
- Response models are part of the api-surface contract. Change one, then regenerate the web types.

<!-- mapped: .@8cab386 | paths: api/ -->
