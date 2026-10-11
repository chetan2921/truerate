# TruRate handoff (2026-10-11, retrained on 1,253 deals)

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
- Judges' deck: `data/pitch/TruRate-judges.pptx` (and `.pdf`), 20 slides, built with pptxgenjs following Anthropic's pptx skill. Rebuild: `cd data/pitch/judges-deck && npm install pptxgenjs@3 && node build.js` (numbers from `data/models/`, cropped screenshots in `shots/`). Charts are drawn shapes: pptxgenjs charts don't render in Keynote.
- Leadership deck (the one to present): `data/pitch/TruRate-leadership.pptx` and `.pdf` (updated 2026-10-11 for the 1,253-deal model; slide 9 is the before/after and learning curve, read from `data/models/before_after.json`; the earlier version is `TruRate-leadership-v1`), 10 slides for the CTO and CXOs in DESIGN.md's look with Urbanist (installed in `~/Library/Fonts`; present from the PDF, which embeds it). Rebuild: `cd data/pitch/leadership-deck && npm install pptxgenjs@3 && node build2.js`. Per creator: about 45 s (median of 22 runs), about 25 HikerAPI requests (about 1.5¢ at $0.60 per 1,000), Gemini about 3¢ (rough estimate).

## Model, honestly (`data/models/model_report.json`, `data/models/before_after.json`, `data/models/experiments_1253_*/`)
- **Served since 2026-10-11: gradient boosting** (`pricing.Boosted`, monotone in views and followers, on `features_v2`) **with global split-conformal 80% ranges**, trained on 1,230 of WLDD's 1,253 deals (`data/creators2.csv`; 20 accounts no longer exist, 3 private or under 12 reels).
- Before/after on the same **124 held-out creators** (10% of each tier, none the earlier model trained on): median error **53% → 38%**, within 2× of the price paid **53% → 74%**, range holds **77% → 86%** at a median width **6.8× → 6.7×** (never over 7.5×), rank order 0.61 → 0.73, R² on log price 0.34 → 0.50. Baselines on the same 124: band median 46% (59% within 2×), Modash-style 56% (50%). The model beats both in every niche (leave-one-out).
- Learning curve (`experiments_1253_today/learning_curve.png`): boosting 54% at 30 deals, 41% at 500, 38% at 1,106; today's Ridge method 48% → 42%. More deals helped.
- The pre-registered rule picked boosting with "local" ranges; **global is served instead**: local held 87% at 6.3× but gave 8% of held-out creators ranges over 15× (one 144×). Global: 86%, 6.7×, max 7.5×. Old model files: `data/models/before_1253/`.
- Payout-date stats (views in the 90 days before each payout, `experiment --dated`): no better (CV 44% either way; held-out 40% vs 38%), so the model reads today's stats. Near-identical creators (same niche, followers and views within 25%) were still paid a median 1.87× apart (2,327 pairs; 1.80× on payout-date stats): what each deal included is the missing piece.
- **632 of the 1,230 creators are labelled offline** (Gemini credit ran out): niche by a MiniLM classifier (71% agreement with Gemini in 5-fold CV), ads by the rules alone (`labels_source: rules`). Relabel with Gemini when credit is back: delete those labels in the training DB, `build-metrics`, `validate --method boosting`.

### Earlier model (148 deals, until 2026-10-11)
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

## How the retraining ran (repeat it this way)
- Training data lives in a **local MongoDB**, never Atlas (the free 512 MB cluster filled up once and blocked the live app): `data/tools/mongodb/bin/mongod --dbpath data/mongo-train --bind_ip 127.0.0.1 --port 27018 --wiredTigerCacheSizeGB 0.25 --fork --logpath data/mongo-train.log`; stop it with `db.adminCommand({shutdown: 1})` (macOS has no `--shutdown`). Commands then run with `MONGODB_URI=mongodb://127.0.0.1:27018 MONGODB_DB=truerate_train`. It also holds `truerate_live_backup_20261011` (the live deals, metrics and labels before the swap).
- Steps: `import-deals ../data/creators2.csv --holdout-share 0.1 --exclude ../data/creators.csv` → `scripts/collect_deals.py` on the EC2 box and the Mac in parallel (paced at 4.4/s each: the HikerAPI account allows 9/s) → rsync `hikerapi/` back → `collect-benchmark --only done.txt` (offline) → `build-metrics --workers 32` (or `label-offline` without Gemini) → `experiment --no-fresh --workers 6 --live-model ../data/models/price.joblib` → `validate --method boosting --out-dir <staging>` → copy `price.joblib` and `model_report.json` into `data/models/` → copy `deals`, `metrics`, `labels` (about 6 MB) to Atlas `truerate`.
- Cost: about 40,000 HikerAPI requests (balance about $1,023 before), Gemini for 598 creators. EC2 box `ubuntu@3.110.217.14` (key `~/.ssh/digitalocean_reelpin`, passphrase in the Mac keychain) still has `~/truerate-collect/` (685 MB of raw responses and a `.env` with the HikerAPI key): delete when no longer needed.

## Left
- **Gemini credit is depleted**: every new live analysis and brand run needs Gemini, so they fail until the AI Studio prepay is topped up. Then relabel the 632 offline creators (above).
- The judges' deck (`TruRate-judges.pptx`) still predates the retraining (Ridge, 148 deals). The leadership deck is current.
- Optional: the api and web AGENTS.md notes are stamped at an old commit; re-map them (`/repo-setup` or by hand) before trusting their details.
- Optional: the organisers' explainer (https://claude.ai/artifact/QzWtvix98TwVhjqsPbAsMN) predates today's changes.

## Constraints that bite
- The repo is public: never commit `data/`, `.env`, or a creator handle next to a WLDD price, and never send deal prices to Gemini. Leak-scan staged diffs against the handles in `data/creators.csv`, `data/creators2.csv` and `data/fresh_test_20.csv`.
- Atlas is the free 512 MB tier and the live app writes there: keep bulky training data (snapshots with reel history) local.
- Correctness over speed: no change that alters results without evidence.
- Don't restart the servers while the user is testing. `make api` reloads on code changes; an analysis running during a reload is marked failed.
- 8 GB Mac near full on swap: run TabPFN only with the servers stopped; nice long jobs.
- Desktop web only. TDD where tests exist, `ui-craft` for UI, short plans.
