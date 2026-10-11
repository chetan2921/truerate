# truerate implementation

## Now
All six milestones are done on real data (2026-10-10). What's left is judging day: the checklist and script in `.claude/plan/truerate/DEMO.md`.

Real-data results, for the pitch and the About page:
- Collection: 149 of 150 deal creators (one account deleted), 148 with 12+ reels.
- Price: holdout median error 56% against 65% (band median) and 62% (Modash-style); range covers 77%. By band: under 20K 29%, 20K to 100K 75%, 100K+ 63%.
- Fakes: flat views, flat views with noise, bot likers and pod comments caught 100%, bought followers 99%, smart fake 74%. 18% of WLDD's own creators are flagged, mostly for low likes per view.
- Live analysis of an unseen creator: 90 to 111 s with fresh Instagram data, about 45 s when it's already saved.

### In flight: model v2 experiments (handoff step 2)
Decision rule, fixed before any held-out number was computed:
- Challengers are picked by repeated 5×10-fold CV on the 118 training deals only. Price: the lowest CV median error among candidates whose CV 80% coverage is at least 75%. Range: the narrowest CV median width with CV coverage at least 77%.
- A challenger is served only if it beats today's model on both the 30 held out and the 19 fresh: lower error or narrower ranges, no worse on the other, and the 80% range still holding at least 75% (`experiment.beats`). The paired-bootstrap 90% interval of the difference is reported beside it. Otherwise the served model stays, and the table says so.
- The fresh deals are scored by models fitted on all 148, as served. The 30 held out are scored by models fitted on the 118. Genuine share is 1.0 for both, as in `validate`.

- [x] `truerate/experiment.py` with the new features and fresh rows rebuilt from stored analyses. Live: all 19 fresh deals re-price to their stored prices exactly.
- [x] Conformal ranges (80% and 50%; global or per band); synthetic coverage test.
- [x] Candidates. The harness reproduces `model_report.json` exactly (57%, 83%, every band), and today's served ranges for the fresh 19 exactly.
- [x] `truerate experiment` writes `data/models/experiments/`. The command is checked by the live run (no unit test); `run` and `report_table` have tests.
- [x] Adopt or not: **not adopted** (2026-10-10). The CV pick was ElasticNet with the new features (CV 39.5% against 40.0%). Held out: 55% against 57%, ranges 6.7× against 7.0×. Fresh: 56% against 55%, and its range holds 58% against 63%. Bootstrap over the 49: error change −9 to +9 points; width ×0.94 to ×0.97.
  - Uncapped paid factor: worse (held out 75%). The cap stays.
  - Per-band ranges: wider. The 50% band holds 33% (held out) and 32% (fresh) against its CV 52%, so it isn't fit to be the headline.
  - Fresh deals: WLDD paid a median 1.63× the prediction, mostly the big creators (1 of 6 inside the range). The held-out 30 were paid 0.72×. Learning curve: 59% at 30 deals, 56% at 118.
- [x] TabPFN v2 (local, v2 weights, `experiments` group), run with the servers off: **not adopted**. It became the CV pick (39.1% against 40.0%). Held out: 62% against 57% (worse). Fresh: 50% against 55%, with a range holding 58% against 63%. Bootstrap over the 49: −13 to +12 points. About 50 minutes with TabPFN.
- Dropped (user, 2026-10-10): the HypeAuditor hand check. The outside comparison stays the Modash-style baseline `validate` already scores.
- [x] Asked about the fresh deals (user, 2026-10-10): one reel each; when they were made is unknown. So the big-creator gap isn't explained by deal terms. It's either price drift over time or the noise floor.
- [x] Report tabs (2026-10-10): Summary · Price · Audience · Content · Similar, with `#tab` deep links and a sticky bar. Checked: lint, types, ui-check (audit, first screen at all 11 sizes, slop scan 0 of 12), cold deep links to all 5 tabs in Chrome, keyboard, a quote check surviving a tab switch, sticky bar, no console errors.
- [x] Market price shown separately (2026-10-10): beyond WLDD's largest deal the range stays WLDD's own (still widened 1.4× per doubling), and the note points to the separate market line. A real check on a creator with 7.8L followers: ₹10,500 to ₹74,500 instead of ₹10,500 to ₹2,00,000. Saved reports keep their old numbers. No held-out or fresh creator is beyond WLDD's deals, so the experiment numbers don't change.
- [x] Navigation fix (2026-10-11): forms reset when Next hides them, so no stuck "Starting…"; `/batch` lists recent batches with progress (`GET /api/batches`). Reproduced in Chrome with Playwright before the fix, passing after.
- [x] Answers instead of measurements (2026-10-11): `outputs.py` verdicts on every analysis and batch row; Summary leads with "Pay about", the likely band and the verdicts; evidence tabs trimmed (checks behind a disclosure, ads grouped by brand).
- [x] Batch comparison (2026-10-11): who to book and why, a verdict scorecard, and charts for price against budget, what ₹10,000 buys, and expected views.
- [x] Range question answered (2026-10-11): per-creator ranges were no narrower; coverage by width is in `data/models/experiments_local/table.md`.
- [x] Big creators (2026-10-11): price leans on the WLDD-discounted market rate past WLDD's largest deal; web check for their own listed price, shown as information. Live: a creator with 21.7L followers went from ₹58,000 to about ₹2.3L, and the web check found his own listing at ₹80,000 to ₹1,00,000 (confirmed on the source page).
- [x] Brand match (2026-10-11): `brand.py`, `POST/GET /api/brands`, `/brand` and `/brand/[id]`. Live: boAt from @boat.nirvana in 12 s (3 HikerAPI requests, 1 Gemini call), 180 creators considered, a ₹2,00,000 plan of 6 creators with about 23.4L views. The plan never books a creator with a weak fit, a fake audience or reels that mostly flop.
- [x] Charts (2026-10-11): ranked "What ₹10,000 buys" bars instead of the scatter; every hand-drawn chart shows its numbers on hover or focus (`ChartTip`); the empty "Rival ad" and "Worked with them" columns removed.
- [x] UI round (2026-10-11 late): nav labels say what each page does; full range everywhere; asking price only for 10L+; the reel chart's metric switch is back; `RecentTable` (names beside handles, × to hide via `DELETE /api/batches/{id}` and `/api/brands/{id}`, rows fit the first screen, then "Show all") on all three pages; the brand result in tabs (`components/tabs.tsx` now shared with the report). ui-check passes at all 11 sizes.
- [x] Retrained on 1,253 deals with payout dates (2026-10-11): 1,230 usable; 10% of each tier held out (124), none the earlier model trained on. Gradient boosting with global conformal ranges is served: 38% median error against 53% for the earlier model on the same creators, 74% within 2× (53%), range holds 86% (77%) at 6.7×. Payout-date stats tested, not adopted. 632 creators labelled offline (Gemini credit ran out). How it ran and how to repeat it: HANDOFF.
- [ ] Cross-platform strength (decided to explore, not built): Apify actors researched. YouTube via the free Data API v3 (3 quota units per creator); X via `apidojo/tweet-scraper` (~$0.40 per 1,000 tweets); LinkedIn via `harvestapi/linkedin-profile-scraper` and `harvestapi/linkedin-profile-posts`; link-in-bio discovery via `memo23/biolink-scraper`. About $10 of usage plus the $19 Starter plan for ~150 creators. Needs the user's Apify token and a YouTube API key. Match only through the creator's own bio links, never name search. X and LinkedIn scraping breaks their terms (LinkedIn sued hiQ): WLDD's call. Test it like every feature: adopt only if held-out error drops.
- [ ] Notes and pitch; demo prep; housekeeping; then the model work (judge-familiar metrics, anti-gaming chart, ensemble, model-card slides).

Ideas for after the hackathon: a refresh option for saved HikerAPI responses; reuse stored signals in the red-team (it takes about 30 minutes); a faster model for the labelling call.

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
