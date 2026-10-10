# TruRate handoff (2026-10-11)

Read first: `AGENTS.md`, then `.claude/plan/truerate/` `SPEC.md`, `IMPLEMENTATION.md`, `TESTING.md`, `DEMO.md`, and `DESIGN.md`.
This file is safe to commit: no WLDD prices. Prices live only in git-ignored `data/`.

## Where things stand
- Everything is committed and pushed to `origin main`. Run: `make api` (8000) and `make web` (3000), Demo login. Tests: `cd api && uv run pytest -q` (all pass); web: `cd web && npm run lint && npm run build`; UI: `web/scripts/ui-check.sh /analyses/<id> /batch/<id> /brand/<id>`.
- **The app shows answers, not measurements** (the founders read outputs):
  - Report Summary: the full fair range, the call, and plain verdicts from `api/truerate/outputs.py` (✓/!/✗ with one sentence).
  - Evidence sits in tabs: Price, Audience (9 checks behind a disclosure), Content (ads grouped by brand) and Similar.
- **Batch** (`/batch/[id]`): who to book first and why, the cheapest-views alternative, "What ₹10,000 buys" ranked bars, a verdict scorecard, and price and reach charts. `/batch` lists recent batches.
- **Brand match** (`/brand`, `api/truerate/brand.py`):
  - Input: a brand's handle, site or name.
  - It works out what the brand sells and to whom.
  - It ranks WLDD's creators, past analyses and accounts seen with the brand, each labelled by source.
  - Output: a plan with the most views within budget (never a weak fit, fake audience or unreliable creator).
- **Big creators** (past WLDD's largest deal, 7L followers): the price leans on the published market rate × WLDD's measured discount (0.19 of the market middle at 1L–5L). A Gemini + Google Search web check shows the creator's own listed price as information only.
- **Charts**: every hand-drawn chart shows its numbers on hover or focus (`web/src/components/chart-tip.tsx`).
- **Bug fixed**: forms stuck on "Starting…" after navigating back (Next 16 keeps pages alive with `<Activity>`).
- Deck: `data/pitch/TruRate.pptx`, 12 slides, rebuilt by `cd api && uv run python scripts/make_deck.py`, numbers only from `data/models/`. Demo script and run IDs: `DEMO.md`.

## Model, honestly (`data/models/model_report.json`, `data/models/experiments*/`)
- 30 held-out deals: median error 57%, **70% within 2× of the price paid**, R² 0.15 on log price, rank order 0.57. Both baselines lose on every score (band median 65%, 50% within 2×; Modash-style 73%, 50%). The 80% range holds 83%.
- Six models tested (Ridge with new features, ElasticNet, monotone boosting, TabPFN v2, uncapped paid views, today's). They were picked on training deals only and scored on 30 held-out and 19 fresh deals. None beat today's on both test sets, so today's stays.
- Range width: a 2× range would hold 30% (held out) and 16% (fresh) of real prices. Per-band and per-creator ranges were no narrower. More deals, plus deal dates and deliverables, are the only honest levers.
- The audit found WLDD's data consistent; the user confirmed the 10 extreme deals are correct.

## Decisions (user)
- `data/fresh_test_20.csv`: real WLDD deals, one reel each, **test only**, never trained on; 19 usable.
- Answers over numbers; likely band plus full range; quote checker kept; stand-out extras dropped; HypeAuditor not used.
- Big creators: market rate discounted the way WLDD pays; their own listed price found online is **information only**.
- Batch "Rival ad" and brand "Worked with them" columns removed.
- 2026-10-11 late: nav reads Price a creator · Compare creators · Creators for a brand · Rate card · About. The **full range** is the headline everywhere (no "Pay about", no likely band on screen; the likely band still sets "on the high side" quotes). The published asking price shows only for 10L+ followers. Recent lists are tables with names beside handles, × to hide, and as many rows as fit the first screen. The brand result is in three tabs. Cross-platform strength (YouTube, X, LinkedIn) via Apify is researched, not built: see IMPLEMENTATION.

## Left
- Optional: the api and web AGENTS.md notes are stamped at an old commit; re-map them (`/repo-setup` or by hand) before trusting their details.
- Optional: the organisers' explainer (https://claude.ai/artifact/QzWtvix98TwVhjqsPbAsMN) predates today's changes.

## Constraints that bite
- The repo is public: never commit `data/`, `.env`, or a creator handle next to a WLDD price, and never send deal prices to Gemini. Leak-scan staged diffs against the handles in `data/creators.csv` and `data/fresh_test_20.csv`.
- Correctness over speed: no change that alters results without evidence.
- Don't restart the servers while the user is testing. `make api` reloads on code changes; an analysis running during a reload is marked failed.
- 8 GB Mac near full on swap: run TabPFN only with the servers stopped; nice long jobs.
- Desktop web only. TDD where tests exist, `ui-craft` for UI, short plans.
