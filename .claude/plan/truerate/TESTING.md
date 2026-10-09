# truerate testing

## Run
| Part | Command |
|------|---------|
| api | `make test` (runs `uv run pytest -q` in `api/`) |
| web | `cd web && npm run lint && npm run build` |
| UI | ui-craft `audit.mjs` and `slop-scan.mjs`, commands in `DESIGN.md` |

## Known-good examples
- FastAPI route test with `TestClient`, and settings read from env: `api/tests/test_app.py`

## Strategies that work here
- Goal is prototype, so tests cover the parts being proven: parsers, pricing maths, the verdict rules. Not every branch.
- A test comes before the code it tests (repo-setup rule for planned products).
- Mongo in unit tests: `mongomock`, never the real cluster.
- Instagram in unit tests: recorded HikerAPI JSON in `api/tests/fixtures/`, taken from a public account that is not in WLDD's deals. The repo is public.
- LLM in unit tests: a fake that returns a fixed reply. Never call Gemini from a test.

## Inventory
| Area | Unit | Integration | E2E | Notes |
|------|------|-------------|-----|-------|
| api health + settings | yes | no | no | |

## Model validation (judging 4 and 5)
These are reports, not pass/fail unit tests, and they arrive with milestones 2 and 3:
- `truerate validate`: 30 held-out creators by follower band, leave-one-out by category, both baselines, range coverage
- `truerate redteam`: catch rate per fake type (smart fake included) and the flagged share of unmodified creators

## Gaps
- `web/` has no tests yet; lint and build only.
