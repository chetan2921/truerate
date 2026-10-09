# truerate implementation

## Now
Milestone 1's code is done and live-checked on 2 deal creators: 20 requests and about a minute each. Left: `uv run truerate collect-benchmark` for all 150 (about 3,000 requests). It waits for the paid HikerAPI key; the free key has about 50 requests left, kept for checks.

Milestone 2 is in flight. Its code is built against synthetic tests now, then validated once the 150 snapshots are in.

### In flight: price v1
- [ ] the 7 categories (tech and gadgets; fashion and beauty; lifestyle and travel; entertainment; education, finance and news; food; fitness), with the CSV's 21 genres mapped onto them
- [ ] test, then `signals.reel_metrics(snapshot)`: last 30 unpinned reels split into own, paid (label, sponsor tag, ASCI hashtag) and collab (co-author, not paid). Returns followers, median own views, views per follower, engagement, comments per 1,000 views, consistency (last 10 reaching half the median), typical bad reel (25th percentile), trend, and paid and collab ratios with their counts
- [ ] test (fake LLM), then the Gemini niche label: bio and 12 captions give one category. WLDD's CSV niche wins where it exists
- [ ] `truerate build-metrics`: the latest snapshot of every deal goes into `metrics`
- [ ] test, then `pricing.py`: Ridge on log price, KNN on ₹ per 1,000 views, blend weight by leave-one-out, p10/p90 range, collab factor with shrinkage, expected delivery, and both baselines
- [ ] `truerate validate`: holdout error per band, leave-one-out per category, both baselines and range coverage, saved for `/api/model-report`
- [ ] live: on the 150 once snapshots exist, the holdout median error is below both baselines

## Next
- 3. Audience check: comments and pods, Louvain, IsolationForest, MediaPipe, Gemini ad labels, commenter mix and languages, the verdict in the price, and the red-team with the smart-fake rate reported. The fake-account model is already built (`truerate build-fake-model`, 88% on Kaggle's test set)
- 4. API + report: analyses endpoints with background jobs, login, analyze page, report page with all five sections (per `DESIGN.md`)
- 5. Extras: batch, rate card + calculator, quote check, competitor conflict, cheaper alternatives, print page, About in five parts
- 6. Pitch: deck of at most 12 slides answering judging 1–6 with real numbers, plus a 3-minute demo with a cached fallback

## Done
- 2026-10-10 Scaffold: FastAPI `api/` (Python 3.12, uv) with `/api/health`, Next.js 16 `web/`, `DESIGN.md` on Solo's palette, agent memory.
- 2026-10-10 M1 code: 150 deals live in Mongo (30 held out). HikerAPI client with a 24 h Mongo cache, parsers tested on recorded fixtures, `collect` and `collect-benchmark`, and a live check on 2 creators. The benchmark run itself waits for the paid key.
