# truerate implementation

## Now
Waiting on the paid HikerAPI key for the live steps, in order:
1. `uv run truerate collect-benchmark` for all 150 deal creators (about 3,000 requests).
2. `uv run truerate build-metrics`: about 150 Gemini labelling calls, plus niche calls for the 115 without a CSV niche.
3. `uv run truerate validate`. Milestone 2 is done when the holdout median error is below both baselines.
4. `uv run truerate redteam`. Milestone 3 is done when at least 80% are caught on flat views, bot likers, pod comments and bought followers, and the smart-fake rate is reported.

The free key has about 50 requests left, kept for checks.

Meanwhile milestone 4 is in flight. Until the 150 are in, the web is built against a dev database seeded with synthetic creators (`MONGODB_DB=truerate_dev`).

### In flight: API + report
- [ ] test, then `pipeline.analyze()`, recording each step as it goes:
  - collect, then the face check, then labels, metrics and category
  - the audience check (band norms, verdict, rings, warnings, commenter mix)
  - price with the genuine share, then the decision, reasons and negotiation lines
  - private accounts, fewer than 12 reels and faceless pages end as `out_of_scope`
- [ ] test, then the API: `POST` and `GET /api/analyses` (background thread pool), `GET /api/meta`, `GET /api/model-report`, with Pydantic response models. Generate `web/src/lib/api-types.ts`
- [ ] web: login (demo button plus the `@wldd.in` check, cookie, redirect), `/` with the analyze form and recent analyses, and `/analyses/[id]` polling the 4 steps
- [ ] web: the report, per `DESIGN.md`: decision block, waterfall with the 6 comparables, the five sections, negotiation lines
- [ ] ui-craft `audit.mjs` passes on `/` and the report
- [ ] live: a never-seen face creator end to end in under 2 minutes

## Next
- 5. Extras: batch, rate card + calculator, quote check, competitor conflict, cheaper alternatives, print page, About in five parts
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
