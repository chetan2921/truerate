# truerate implementation

## Now
Waiting on the paid HikerAPI key for the live steps, in order:
1. `uv run truerate collect-benchmark` for all 150 deal creators (about 3,000 requests).
2. `uv run truerate build-metrics`: about 150 Gemini labelling calls, plus niche calls for the 115 without a CSV niche.
3. `uv run truerate validate`. Milestone 2 is done when the holdout median error is below both baselines.
4. `uv run truerate redteam`. Milestone 3 is done when at least 80% are caught on flat views, bot likers, pod comments and bought followers, and the smart-fake rate is reported.
5. A never-seen face creator on `/`, end to end in under 2 minutes. That closes milestone 4.

The free key has about 50 requests left, kept for checks.

Meanwhile milestone 5 is in flight. Its screens are built against `MONGODB_DB=truerate_dev` and synthetic models until the 150 are in.

### In flight: extras
- [ ] dev seed: `MODELS_DIR` can point at `data/models_dev`, and a seed script writes synthetic analyses, a price model and both reports there
- [ ] test, then the quote check: `POST /api/analyses/{id}/quote` gives below, within or above the range, the difference, a counter-offer and 3 talking points, with no new scraping. The report gets a quote checker under the waterfall
- [ ] test, then batches: `POST /api/batches` (up to 50 handles, product, budget) and `GET /api/batches/{id}`, ranked by cost per 1,000 views. `/batch` and `/batch/[id]` with Export CSV
- [ ] test, then the rate card: `GET /api/rate-card` gives ₹ per 1,000 views and the typical reel price per category. `/rate-card` with the calculator (category and views wanted give a budget range)
- [ ] `/analyses/[id]/print`: the decision block, waterfall and red flags on A4, black on white; opens the print dialog. A Download-PDF button on the report
- [ ] `/about` in five parts: how it works, signals and why, accuracy (band, category, baselines, coverage), the fake-creator test, and other page types plus known limits. Reads `/api/model-report`
- [ ] header nav: Analyze, Batch, Rate card, About
- [ ] `web/scripts/ui-check.sh` passes on every new screen

## Next
- 6. Pitch: deck of at most 12 slides answering judging 1–6 with real numbers, plus a 3-minute demo with a cached fallback

## Done
- 2026-10-10 Scaffold: FastAPI `api/` (Python 3.12, uv) with `/api/health`, Next.js 16 `web/`, `DESIGN.md` on Solo's palette, agent memory.
- 2026-10-10 M1 code: 150 deals live in Mongo (30 held out). HikerAPI client with a 24 h Mongo cache, parsers tested on recorded fixtures, `collect` and `collect-benchmark`, and a live check on 2 creators. The benchmark run itself waits for the paid key.
- 2026-10-10 M2 code:
  - 7 categories and `reel_metrics` (own, paid and collab split; consistency; trend), plus the Gemini niche label (live on 2 creators)
  - `build-metrics`
  - `pricing.py`: Ridge plus the 6 same-category nearest deals, a leave-one-out blend and range, the collab factor, the waterfall and expected delivery
  - both baselines, and `validate`
  - On synthetic deals the model beats both baselines on 4 of 4 seeds, and the range covers 73% of 60 held-out deals.
- 2026-10-10 M3 code:
  - audience signals in 3 families (MiniLM generic and repeated comments, repeat commenters, fake likers and followers, evenness, ratios), band norms with box-plot fences and minimum gaps, the verdict and the genuine share
  - Gemini labels (hidden ads with covers, topics, account kinds, languages) and the commenter mix
  - MediaPipe face check, Louvain rings, and IsolationForest and renamed-page warnings
  - the red-team with 6 fake kinds
  - Live on 2 creators: 1 and 5 hidden ads found, plus the languages and commenter mixes.
- 2026-10-10 M4 code:
  - `pipeline.analyze()` (decision, reasons, competitor conflict, cheaper alternatives, negotiation lines)
  - the analyses API with background jobs and typed `Report` models, plus generated web types
  - login with proxy and `@wldd.in` check, analyze page, polling with 4 steps, and the full report
  - ui-check passes on `/`, `/login` and two reports (audit, report first screen, slop scan 0 of 12). The live run waits for the 150.
