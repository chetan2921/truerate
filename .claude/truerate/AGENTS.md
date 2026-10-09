# truerate repo

What one reel by an Instagram face creator is worth to WLDD, and whether to book them. Monorepo with two subsystems, each with its own runtime and its own context file.

Mapped from `main`.

## Subsystems
| Folder | What it is | Context |
|---|---|---|
| `api/` | FastAPI service on Python 3.12 (uv), MongoDB | `.claude/truerate/api/AGENTS.md` |
| `web/` | Next.js 16 front end | `.claude/truerate/web/AGENTS.md` |

## Run
- `cp .env.example .env` and fill `MONGODB_URI`, `HIKERAPI_KEY`, `LLM_API_KEY`.
- `make api`, `make web`, `make test` (targets in `Makefile`).

## Folder map
- `api/`, `web/`: the two subsystems above
- `DESIGN.md`: the visual source of truth for `web/`
- `data/` (git-ignored, repo root): `creators.csv`, the Kaggle CSV, trained model files
- `.claude/`: agent memory (this tree); the plan lives in `.claude/plan/truerate/`

## Sharp edges
- The repo is public. Never commit `data/`, `.env`, or any file pairing a creator handle with a WLDD price.
- Deal prices never go into an LLM prompt.
- Signatures for both subsystems are in `.claude/truerate/STRUCTURE.md`.

<!-- mapped: .@9585fbe | paths: Makefile, .env.example, .gitignore -->
