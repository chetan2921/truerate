# TruRate handoff (2026-10-10, evening)

Read first: `AGENTS.md`, `.claude/plan/truerate/SPEC.md`, `IMPLEMENTATION.md`, `TESTING.md`, `DEMO.md`, `DESIGN.md`.
This file is safe to commit: no WLDD prices. Prices live only in git-ignored `data/`.

## Where things stand
- Product renamed **TruRate** (web, API messages, deck). Repo, package and CLI stay `truerate`.
- Run from `~/Documents/truerate`: `make api` (port 8000) and `make web` (port 3000). Then open http://localhost:3000 and click Demo login. Wait ~20 s after API start for models to load. Tests: `make test` (106 pass); web: `cd web && npm run lint && npm run build`; UI: `web/scripts/ui-check.sh /analyses/<id> /login`.
- **Uncommitted:** 36 files of today's work, plus 9 commits not pushed to `origin main`. Commit first, after the user says yes (`git commit -s`, no AI attribution; grep staged changes against `data/creators.csv` handles first, 0 hits).
- Done today, all verified:
  - fresh analysis 71 s → **34 s**, seen-before 23 s; same results:
    - overlapped Instagram requests;
    - parallel cover downloads;
    - Gemini `thinking_level="low"`, with labels as close to the default as two default runs are to each other;
    - retry on dropped Gemini connections.
  - face check: the short-range face model wrongly rejected 14 of WLDD's 148 face creators. It is now person (EfficientDet ≥0.6) **or** full-range face (≥0.8), and creators in WLDD's deals are never rejected. Result: 0 of 148 rejected; faceless food, travel and wildlife pages still out of scope.
  - the report headline is the **fair range** (no single big price); the single number shows only as "Middle of the fair range".
  - 42 specific product categories in 7 pricing groups. The rate card lists all 7: Fitness has 1 deal, shown as "not enough deals".
  - home: centred layout, top-10 recent list with show-all and × to hide (`DELETE /api/analyses/{id}` hides it).
  - batch input is numbered rows (Enter adds a row).
  - analyses left "running" by a stopped server are marked failed at startup.
  - Phyllo removed (`931e53e`). Older-reels experiment reverted (user decision: not worth the time).
- Explainer for organizers: https://claude.ai/artifact/QzWtvix98TwVhjqsPbAsMN (source in the old session's scratchpad; republish via `url`).
- Deck: `data/pitch/TruRate.pptx`, rebuilt by `cd api && uv run python scripts/make_deck.py`.

## Current accuracy (`data/models/model_report.json`, 30 held-out deals)
- Real price inside the 80% range: 83%.
- Median gap between the middle of the range and the price paid: 57%, against 65% for the band median and 73% for the Modash-style formula.
- The range is about **0.36× to 2.27× the middle** (≈6× wide). That width comes from the data: near-identical creators in WLDD's deals were paid a median 53% apart. Earlier repeated-CV trials of other models and features landed at 44-46%, no better.
- Above WLDD's largest deal, the range also widens 1.4× per doubling and its high end is lifted to the published market low (`pricing.price`). That is why mega creators show ranges like ₹18,500 to ₹6,00,000.
- Fake-creator test: 4 main fakes caught 99-100%, smart fake 72%, real creators flagged 9.5%.
- `data/fresh_test_20.csv` holds 20 creators with prices the user gave, none in the 150 deals. Ask whether they are real WLDD prices. A batch run on them was stopped after 3; rerun it as an unseen test set.

## The user's asks, consolidated
1. **A trained model that narrows the range** and beats a rival team's "trained model with graphs" in front of mentors, plus a before/after slide later.
2. **Brand-first page:** WLDD gets a brand call. Enter the brand (Instagram handle, website URL or name), budget and product. Get the top creators, why each is best, and a side-by-side comparison.
3. **Report in tabs** (like browser tabs) instead of one long cluttered page; less useful detail moves out of the way.
4. **More ideas** that stand out but stay in scope.

## Honest evaluation (say this to the user plainly)
- A bigger model alone won't narrow the range: with ~150 prices it memorises, and the 53% noise floor caps accuracy. The width can only shrink honestly in three ways:
  - (a) **More prices.** The 20 fresh ones, if real, are +13%. Any more WLDD deals are the biggest lever.
  - (b) **Features that explain price.** Candidates, all already fetched: paid-reel views for ad-heavy creators (a top-priced creator's ads get 16× their own views), own-voice share, reel length, ads per month, agency email, YouTube link, account age, comment language.
  - (c) **Per-creator ranges** (conformalized quantile regression, MAPIE CQR with quantile gradient boosting): narrow where similar deals agree, wide where they don't, still at 80% coverage.
- Also offer a **"most likely" 50% band** as the headline, about 2.7× wide instead of 6×, with the 80% range beside it. It is narrower and honest, because the confidence is stated.
- Mega-creator ranges: offer to show the WLDD-data range and the market reference separately instead of merging them. This is a product decision for the user.
- How to beat the rival honestly: rigorous validation (held-out set, baselines, interval coverage and width, the 20 fresh creators), SHAP feature-importance graphs, a learning curve showing error falling as deals grow, and the authenticity and ad detection his model lacks. Never claim an improvement the held-out numbers don't show.

## Plan (timebox; judging may be 2026-10-11)
Each step lists its proof of done.
1. **Commit today's work** (after the user agrees). Done when: `git status` is clean, the leak scan shows 0 hits, and the push happens only if the user says so.
2. **Model v2 experiments** (`api/truerate/pricing.py`, new `truerate experiment` CLI).
   - Same 30 holdout plus repeated 5×10-fold CV on the rest, never tuned on the holdout. Also score the 20 fresh creators.
   - Candidates: Ridge (current), ElasticNet, LightGBM/CatBoost (small, monotone, regularised), quantile regression forest; the new features above; CQR intervals.
   - Metrics: median gap, coverage, median high/low ratio, per band.
   - Adopt only if coverage stays near 80% and width or error improves. Done when: a before/after table and graphs (predicted vs actual, interval width, SHAP, learning curve) are saved in `data/models/experiments/`, and the served model changes only if it wins.
3. **Report tabs:** Summary (range, call, delivery, reasons, negotiation) · Price (steps, 6 deals, quote check, cheaper creators) · Audience (authenticity, engagement, niche) · Content (reel chart, consistency, paid/collab, ads) · Similar (Instagram suggestions). Use a `#tab` deep link, Summary by default, and leave the print one-pager as it is. Done when: lint, build, ui-check and layout check pass at desktop sizes (the user said desktop only).
4. **Brand match page** (`/brand`). This was removed in an earlier pivot; it now returns as its own page.
   - Brand profile: Instagram via HikerAPI (bio, captions, creators who tagged or co-authored with the brand) or website (httpx fetch, text only), summarised by Gemini into category, products, audience, tone and price tier.
   - Candidates: WLDD's creators (metrics stored), every analysed creator, creators who already worked with the brand or its rivals, and their Instagram suggestions.
   - Score: product fit, audience verdict, ₹ per 1,000 views at the fair range, low end within budget, rival ad in the last 60 days, consistency and engagement.
   - Output: top N with reasons, side-by-side comparison, and a budget plan picking the best set of creators within budget for expected views. Re-run stale top picks live.
   - Done when: tests for scoring and budget pick pass and a live brand run works.
5. **Stand-out extras** (pick with the user):
   - (a) **Audience overlap** in shortlists from shared commenters and likers, so WLDD doesn't pay twice for the same people. The data is already fetched.
   - (b) **Delivery tracker:** paste the live sponsored reel and compare views at 24 h and 7 days with the expected views. This builds WLDD's own labelled data, so the model improves after every campaign. It's the strongest answer to "static model" competitors.
   - (c) **Brand-safety scan** of captions and comments.
   - (d) **Lookalike finder** from one great creator.
6. **Notes and pitch:** update SPEC, IMPLEMENTATION, TESTING, HISTORY, DEMO and the explainer; build the before/after slide from step 2's table.

## Open decisions for the user
- Are the 20 prices in `data/fresh_test_20.csv` real WLDD deals? Use them as a test set, or add them to training (not both)?
- Should strong paid-reel views raise the price for ad-heavy creators? It is capped today because it hurt the held-out error before.
- 50% "most likely" band as the headline? Keep the market reference separate from the range?
- Which tabs, and which report parts are noise for the WLDD team?
- Brand page candidate pool: WLDD's creators only, or also creators found through the brand's tags and Instagram suggestions?

## Constraints that bite
- The repo is public: never commit `data/`, `.env`, or a creator handle next to a WLDD price, and never send deal prices to Gemini.
- Correctness over speed: no change that alters results without evidence (the user's rule).
- Don't restart the servers while the user is testing; it kills queued analyses. A restart marks them failed.
- The Mac has 8 GB RAM and is near full on swap; servers get killed under memory pressure. Disk was cleaned to ~22 GB free with mole (whitelist protects Desktop, Documents and the iOS runtime).
- Desktop web only for now. Use TDD where tests exist, `ui-craft` for UI, short plans.
