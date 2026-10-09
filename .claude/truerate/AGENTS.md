# truerate repo

What one reel by an Instagram face creator is worth to WLDD, and whether to book them. Monorepo: a Python API that collects, analyses and prices, and a Next.js front end that shows the report.

Mapped from `main`.

## Stack
- `api/`: Python 3.12 (uv), FastAPI, pymongo, pydantic-settings, httpx. Later milestones add scikit-learn, networkx, sentence-transformers, mediapipe and google-genai (see the spec's stack table).
- `web/`: Next.js 16 App Router, React 19, TypeScript, Tailwind 4, ESLint.

## Run
- `cp .env.example .env` and fill `MONGODB_URI`, `HIKERAPI_KEY`, `LLM_API_KEY`.
- `make api`: http://localhost:8000 (docs at `/docs`)
- `make web`: http://localhost:3000
- `make test`: API unit tests

## Entry points
- `api/truerate/app.py`: the FastAPI `app` (routes live here)
- `api/truerate/config.py`: `Settings` from the repo-root `.env`
- `web/src/app/layout.tsx`, `web/src/app/page.tsx`: root layout and home page

## Folder map
- `api/truerate/`: the Python package. The planned one-file-per-job layout is in `.claude/plan/truerate/SPEC.md` (Architecture).
- `api/tests/`: pytest; fixtures go in `api/tests/fixtures/`.
- `web/src/app/`: routes (App Router).
- `web/public/`: static assets.
- `data/` (git-ignored, repo root): `creators.csv`, Kaggle CSV, trained model files.

## Sharp edges
- `web/AGENTS.md` is written by Next.js itself: this Next.js has breaking changes, so read `web/node_modules/next/dist/docs/` before writing web code.
- The system Python is 3.14. Always run Python through `uv run` (pinned to 3.12 in `api/.python-version`); mediapipe has no 3.14 wheels.
- The repo is public. Never commit `data/`, `.env`, or any file pairing a creator handle with a WLDD price. Test fixtures come from accounts that aren't in the deals CSV.
- Deal prices never go into an LLM prompt.

<!-- mapped: .@543bbb5 | paths: api/, web/src/, Makefile -->
