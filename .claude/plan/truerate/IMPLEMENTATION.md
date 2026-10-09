# truerate implementation

## Now
Waiting on the paid HikerAPI key for the live steps, in order:
1. `uv run truerate collect-benchmark` for all 150 deal creators (about 3,000 requests).
2. `uv run truerate build-metrics`: about 150 Gemini labelling calls, plus niche calls for the 115 without a CSV niche.
3. `uv run truerate validate`. Milestone 2 is done when the holdout median error is below both baselines.
4. `uv run truerate redteam`. Milestone 3 is done when at least 80% are caught on flat views, bot likers, pod comments and bought followers, and the smart-fake rate is reported.
5. A never-seen face creator on `/`, end to end in under 2 minutes. That closes milestone 4.
6. Batch, rate card, quote check, print and About on real data. That closes milestone 5.

The free key has about 50 requests left, kept for checks. Screens are built against `truerate_dev` and `data/models_dev` (`api/scripts/seed_dev.py`).

Milestone 6's code is done too. What is left needs the 150:
7. `uv run python scripts/make_deck.py` on the real reports, plus the report screenshot (`node web/scripts/report-shot.mjs <id>`).
8. The demo dry run in `.claude/plan/truerate/DEMO.md`, timed.

### In flight: live runs
Steps 1 to 8 above, in order, as soon as the paid HikerAPI key is in `.env`. Check `/sys/balance` first.

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
- 2026-10-10 M5 code:
  - quote check (API and report), the A4 client one-pager, and batches ranked by cost per 1,000 views with Avoid last and Export CSV
  - the rate card with its calculator, About in five parts with the predicted-vs-actual chart, and the header nav
  - the dev seed and the `MODELS_DIR` override
  - ui-check passes on all 14 routes checked. Real-data checks wait for the 150.
- 2026-10-10 M6 code:
  - `api/scripts/make_deck.py`: 12 slides answering judging 1 to 6, with native tables and a log-scale predicted-vs-actual chart. Arial, `DESIGN.md` colours. Writes the git-ignored `data/pitch/`; checked by rendering through Keynote
  - `web/scripts/report-shot.mjs`: captures the decision block only
  - `DEMO.md`: the 3-minute script and its fallback
