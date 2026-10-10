# truerate implementation

## Now
All six milestones are done on real data (2026-10-10). What's left is judging day: the checklist and script in `.claude/plan/truerate/DEMO.md`.

Real-data results, for the pitch and the About page:
- Collection: 149 of 150 deal creators (one account deleted), 148 with 12+ reels.
- Price: holdout median error 56% against 65% (band median) and 62% (Modash-style); range covers 77%. By band: under 20K 29%, 20K to 100K 75%, 100K+ 63%.
- Fakes: flat views, flat views with noise, bot likers and pod comments caught 100%, bought followers 99%, smart fake 74%. 18% of WLDD's own creators are flagged, mostly for low likes per view.
- Live analysis of an unseen creator: 90 to 111 s with fresh Instagram data, about 45 s when it's already saved.

### In flight
Nothing. Ideas for after the hackathon: a refresh option for saved HikerAPI responses; reuse stored signals in the red-team (it takes about 30 minutes); a faster model for the labelling call.

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
- 2026-10-10 M1 to M6 on real data:
  - collection with `--workers 12`; build-metrics with labels saved per creator
  - validate passes after bounding the sponsored-performance factor; red-team passes
  - live analysis under 2 minutes (parallel fetches, warmed models, 8 tagged posts in the prompt)
  - the deck rebuilt from the real reports
  - Added on the way:
    - repost labels and brand tags
    - a note when a creator is bigger than any WLDD deal
    - a rate card that needs 3+ deals per category
    - Negotiate (not Avoid) for a possible competitor
    - plain sentences for unknown handles, and Indian grouping in all money text
