# truerate testing

## Run
| Part | Command |
|------|---------|
| api | `make test` (runs `uv run pytest -q` in `api/`) |
| web | `cd web && npm run lint && npm run build` |
| UI | `web/scripts/ui-check.sh /analyses/<id> /login` with the API and web running (ui-craft behind the demo login; `DESIGN.md`, Verify) |

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
- HikerAPI storage in tests: `fake_hiker(tmp_path)` writes its files into pytest's temporary folder, never `data/hikerapi/`.
- `fake_hiker(..., missing={paths}, disabled={paths})` answers 404 or 403 on those endpoints, as HikerAPI does for hidden followers and comments turned off.
- LLM in unit tests: `FakeLLM` in `api/tests/test_signals.py` returns a fixed reply and records each prompt, so a test can check that no price went in. Never call Gemini from a test.
- Statistical properties (range coverage) are pooled over several synthetic seeds: 15 held-out deals swing too much by chance to test one seed.
- Pricing tests: `synthetic_rows(n, seed)` in `api/tests/test_pricing.py` makes deals whose true price is known.
- Audience tests: `genuine_band()` and `genuine_snapshot(i, rng)` in `api/tests/test_audience.py` make believable creators. `fake_embed` gives each distinct text its own random unit vector, so identical texts match and others don't.
- No real face images in the repo: test `face_share` with a stand-in detector, and run the real one live.
- Pipeline and API tests share one synthetic world: `world` and `deps()` in `api/tests/test_pipeline.py`; `test_app.py` imports them.
- ui-craft's `audit.mjs` takes the first `.btn` as the primary action. On the report that is a secondary button far down, so the report's first screen is checked with `web/scripts/first-screen.mjs`. A failing check is a hypothesis: confirm what it measured before changing the page.
- `slop-scan.mjs` can measure a loading state on a dev server that is still compiling the route (0 sections). Rerun once the route is warm.

## Inventory
| Area | Unit | Integration | E2E | Notes |
|------|------|-------------|-----|-------|
| api health + settings | yes | no | no | |
| Mongo indexes, deals import, `import-deals` command | yes | no | no | mongomock; live run gave 150 deals, 30 held out |
| Kaggle fake-account model, `build-fake-model` | yes | no | no | real run: 88% on Kaggle's 120 test accounts |
| HikerAPI client, cache, parsers, `collect`, `collect-benchmark` | yes | no | no | live check on 2 deal creators passed: every reel has views, every comment a time, likers and followers non-empty |
| Categories, `reel_metrics`, Gemini niche label, `build-metrics` | yes | no | no | fake LLM in tests; live on 2 creators (Food, Entertainment) |
| `pricing.py` and `validate` | yes | no | no | synthetic deals with a known ₹ per 1,000 views per category; live run waits for the 150 snapshots |
| Audience signals, band norms, verdict, genuine share, warnings | yes | no | no | synthetic genuine band; live signals on 2 creators |
| Gemini labels, hidden-ad split, commenter mix | yes | no | no | `FakeLLM` / `SchemaLLM`; live on 2 creators |
| Face check, Louvain rings | yes | no | no | stand-in detector in the unit test; real MediaPipe live on 2 creators' covers |
| Red-team (`make_fake`, `redteam`, command) | yes | no | no | synthetic creators; live run waits for the 150 |
| `pipeline.analyze` (Go, bot likers, quote, product fit, out of scope) | yes | no | no | synthetic WLDD world (`world` fixture in `test_pipeline.py`) |
| Analyses API, background job, meta, model report | yes | no | no | job runs inline (`submit` monkeypatched) |
| Quote check, batches (Avoid last), rate card | yes | no | no | `check_quote` and the endpoints, on the synthetic world |
| Pitch deck (`scripts/make_deck.py`) | yes | no | manual | at most 12 slides, numbers from the reports, no handles; slides rendered through Keynote (`osascript`, export as slide images) and looked at |
| Web: login, analyze, polling states, report, quote, print, batch, rate card, About | no | no | manual | lint + build; ui-check passes on every route; checked in the browser on the dev seed |

## Model validation (judging 4 and 5)
These are reports, not pass/fail unit tests, and they arrive with milestones 2 and 3:
- `truerate validate`: 30 held-out creators by follower band, leave-one-out by category, both baselines, range coverage
- `truerate redteam`: catch rate per fake type (smart fake included) and the flagged share of unmodified creators

## Gaps
- `web/` has no unit tests; lint, build, ui-check and a browser pass on the dev analyses.
