# truerate implementation

## Now
Waiting on the paid HikerAPI key for three live steps, in order:
1. `uv run truerate collect-benchmark` for all 150 deal creators (about 3,000 requests, about 2.5 hours at 1 request a second).
2. `uv run truerate build-metrics`.
3. `uv run truerate validate`. Milestone 2 is done when the holdout median error is below both baselines.

The free key has about 50 requests left, kept for checks.

Meanwhile milestone 3 is in flight, built against synthetic tests and the 2 live snapshots. Its thresholds get set on the 150.

### In flight: audience check
- [ ] test, then the signals per creator:
  - likes family: fake-looking likers (`fake_share`), likes per view, how even likes are across reels
  - followers family: fake-looking newest followers, views per follower
  - comments family: generic and repeated comment text (MiniLM), commenters on 60% or more of reels
- [ ] test, then the verdict: each signal is compared with WLDD creators in the same follower band. 0, 1, or 2 or more failing families give Real audience, Some fake activity or Mostly fake. Former usernames and IsolationForest only warn
- [ ] test, then the genuine share (only fake engagement above the band median counts) feeding `price()`
- [ ] Louvain rings: commenters shared across WLDD creators, run on the stored snapshots
- [ ] Gemini, one call per creator: ambiguous reels labelled ad or not (with cover images), each reel's topic, comment languages. Prices are never in the prompt
- [ ] commenter mix: fake-looking accounts, creators and brands among top commenters, and languages
- [ ] MediaPipe face check on reel covers: a faceless page gets `out_of_scope`
- [ ] test, then `truerate redteam`: 6 fake types built from real snapshots, catch rate per type, and the flagged share of unmodified creators
- [ ] live, on the 150: at least 80% caught on flat views, bot likers, pod comments and bought followers; smart-fake rate reported

## Next
- 4. API + report: analyses endpoints with background jobs, login, analyze page, report page with all five sections (per `DESIGN.md`)
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
