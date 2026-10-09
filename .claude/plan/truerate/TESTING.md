# truerate testing

## Run
| Part | Command |
|------|---------|
| api | `make test` (runs `uv run pytest -q` in `api/`) |
| web | `cd web && npm run lint && npm run build` |
| UI | ui-craft `audit.mjs` and `slop-scan.mjs`, commands in `DESIGN.md` |

## Known-good examples
- FastAPI route test with `TestClient`, and settings read from env: `api/tests/test_app.py`
- Mongo in a test (the mongomock `db` fixture in `api/tests/conftest.py`), and a Typer command test with `CliRunner` and `get_db` monkeypatched: `api/tests/test_db.py`
- HikerAPI in a test: `fake_hiker(db)` in `api/tests/test_instagram.py` serves the recorded fixtures through `httpx.MockTransport`; it can also return an error status or a private profile
- A model trained on a tiny synthetic CSV, and a CLI that saves it: `api/tests/test_signals.py`

## Strategies that work here
- Typer turns a parameter with a default into an `--option`. Use `Annotated[Path, typer.Argument()] = default` for a positional argument with a default.
- Goal is prototype, so tests cover the parts being proven: parsers, pricing maths, the verdict rules. Not every branch.
- A test comes before the code it tests (repo-setup rule for planned products).
- Mongo in unit tests: `mongomock`, never the real cluster.
- Instagram in unit tests: recorded HikerAPI JSON in `api/tests/fixtures/`, from komalpandeyofficial (public, not a WLDD deal). The recordings were trimmed to the parsed fields and every other account renamed before committing; grep them against the deals CSV handles before any commit that touches them.
- Live HikerAPI runs: read `/sys/balance` (free) before and after, so the cost is measured. One creator is 20 requests.
- LLM in unit tests: a fake that returns a fixed reply. Never call Gemini from a test.

## Inventory
| Area | Unit | Integration | E2E | Notes |
|------|------|-------------|-----|-------|
| api health + settings | yes | no | no | |
| Mongo indexes, deals import, `import-deals` command | yes | no | no | mongomock; live run gave 150 deals, 30 held out |
| Kaggle fake-account model, `build-fake-model` | yes | no | no | real run: 88% on Kaggle's 120 test accounts |
| HikerAPI client, cache, parsers, `collect`, `collect-benchmark` | yes | no | no | live check on 2 deal creators passed: every reel has views, every comment a time, likers and followers non-empty |

## Model validation (judging 4 and 5)
These are reports, not pass/fail unit tests, and they arrive with milestones 2 and 3:
- `truerate validate`: 30 held-out creators by follower band, leave-one-out by category, both baselines, range coverage
- `truerate redteam`: catch rate per fake type (smart fake included) and the flagged share of unmodified creators

## Gaps
- `web/` has no tests yet; lint and build only.
