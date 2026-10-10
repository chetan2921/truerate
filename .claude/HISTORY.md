- 2026-10-10 setup: created the monorepo (FastAPI `api/`, Next.js 16 `web/`), agent memory with repo-setup, `DESIGN.md` with ui-craft on Solo's palette. Plan cut to 5 milestones.
  Decided: MongoDB instead of SQLite (Chetan's call). The repo is public, so the deals CSV, `.env` and anything pairing a creator with a WLDD price stay out of git.
- 2026-10-10 spec: closed 8 gaps against the problem statement (other-page-type strategy, pitch milestone 6, signals-and-why, per-category accuracy, consistency, collab vs own, who engages / worth reaching, smart-fake reporting) and added a PDF coverage table. `api/` and `web/` got their own context files.
- 2026-10-10 M1 start: ui-craft installed in `~/.claude/skills`. Mongo layer (indexes, TTL cache) and deals import with a fixed holdout, plus the `truerate import-deals` CLI, tested on mongomock. Blocked on `MONGODB_URI` and `HIKERAPI_KEY`.
  Decided with Chetan: commits are signed with `-s` and carry no AI attribution; the pitch is a `.pptx`; build runs straight through milestones and stops only when blocked.
- 2026-10-10 keys: Chetan filled `.env` (Mongo, HikerAPI, Gemini). Work moves to sessions opened in `~/Documents/truerate`. Kaggle fake-account `train.csv` and `test.csv` added to `data/external/instagram_fake/`.
- 2026-10-10 M1 code: live deals import; HikerAPI client, cache, parsers and `collect` commands, live-checked on 2 creators; Kaggle fake-account model (88%). The benchmark run waits for the paid HikerAPI key.
  Decided: the fake-account model uses only the 6 fields that come with likers and followers lists (88% vs 92% with all 11), because the full fields cost one request per account. Fixtures are trimmed and anonymised before committing. 7 categories group the CSV's 21 genres.
- 2026-10-10 M2 code: reel metrics, 7 categories, Gemini niche label, `build-metrics`, `pricing.py` and `validate`, all on synthetic tests. Live validation waits for the 150 snapshots. Gemini model moved to `gemini-3.8-flash` (2.5 is closed to new keys).
  Decided: comparables are the 6 nearest deals in the same category by views and followers, not nearest on every feature. Nearest on every feature mixed categories and narrowed the range (53% coverage on one seed). The served price model refits on all 150 after validation; the holdout numbers come from a model that never saw them.
- 2026-10-10 M3 code: audience signals, norms, verdict, genuine share, Gemini labels (hidden ads, topics, account kinds, languages), commenter mix, face check, Louvain rings, warnings and red-team. All tested on synthetic data; live checks on 2 creators. The 150-creator runs wait for the paid key.
  Decided:
  - A signal is bad only past the band's box-plot fence and a minimum gap, so a tight band doesn't flag tiny differences.
  - The genuine share counts flagged signals only, and pod comments don't discount the price because pods are real accounts.
  - The face check rejects only clearly faceless pages (under 2 of 10 covers): a real food creator showed 2 of 10.
- 2026-10-10 M4 code: pipeline, analyses API with typed `Report`, generated web types, login, analyze, polling and the full report. ui-check passes. The live run waits for the 150. A dev database (`truerate_dev`) holds synthetic analyses for building screens.
  Decided:
  - Native controls instead of shadcn (`DESIGN.md` updated).
  - The report's first screen is checked by `first-screen.mjs`, because ui-craft's primary-action heuristic picks a secondary button there.
  - Cheaper alternatives must be within half to double this creator's views.
- 2026-10-10 M5 code: quote check, client one-pager, batches, rate card with calculator, About in five parts, nav, dev seed (`truerate_dev`, `data/models_dev`). ui-check passes everywhere. M6 (pitch) in flight.
  Decided:
  - A batch ranks Avoid creators after the rest. Pure cost ranking put a Mostly fake creator first.
  - The deck goes to the git-ignored `data/pitch/`: its charts come from WLDD's prices.
- 2026-10-10 M6 code: pitch deck generator, decision-block screenshot and the demo script. All six milestones are code-complete; every remaining step is a live run that needs the paid HikerAPI key (IMPLEMENTATION, Now).
  Decided: the deck uses Arial, because a .pptx can't embed fonts. The deck screenshot is the decision block only, so no WLDD deal price next to a creator reaches a slide.
- 2026-10-10 storage: HikerAPI responses moved from the 24 h Mongo `cache` collection to files on disk (`data/hikerapi/`), raw and gzipped, kept with no expiry. Live check: two lookups cost 1 request.
  Decided with Chetan: keep each response once, with no expiry or refresh option until after the hackathon. Raw, not parsed, so parser fixes cost no credit. Snapshots stay in Mongo. The old cache documents expire on their own.
- 2026-10-10 M1 done: benchmark collected with the paid key (148 of 150 creators with 12+ reels; one deal creator's account no longer exists). `collect-benchmark` and `build-metrics` gained `--workers`. HikerAPI 403 and 404 on list endpoints now count as empty.
- 2026-10-10 M2 done on real data: build-metrics on 148 creators (tagged posts and repost labels added; labels saved per creator), validate holdout 56% vs 65% and 62% baselines, coverage 77%.
  Decided:
  - The sponsored-performance factor is bounded to 0.5–1.0, from systematic debugging. Ridge alone scored 57%; the unbounded factor reached 120× because viral reels were labelled as ads, giving 83%. Discount-only won on leave-one-out over the training creators (39%), not by peeking at the holdout.
  - Leave-one-out gives the 6-nearest-deals estimate zero weight, so the copy now says the market price is the regression.
- 2026-10-10 M3 done on real data: red-team caught 99 to 100% of the four main fakes and 74% of the smart fake. 18% of WLDD's own creators are flagged, mostly for low likes per view; thresholds left as they are, since there is no ground truth to tune them against.
- 2026-10-10 live: M4 to M6 done on real data.
  - Live analysis at 90 to 111 s, after parallel fetches, warmed models and capping tagged posts at 8 (that call went from 85 s to 32 s).
  - The real deck is built, and ui-check passes on the real report, batch, rate card and About.
  Decided with Chetan: a possible competitor is a Negotiate reason ("check exclusivity before booking"), not Avoid; all 6 live runs had come out Avoid.
  Also: a note when a creator is bigger than any WLDD deal; the rate card needs 3+ deals per category; an unknown handle gets a plain sentence.
- 2026-10-10 model v2: committed and pushed the day's work. Recorded the user's six decisions in HANDOFF. New `truerate experiment` (`experiment.py`, `experiment_plots.py`): candidates picked by repeated CV on the training deals only, scored on the 30 held out and 19 fresh deals. Served model unchanged. TabPFN v2 (`experiments` group) was run with the servers off: the CV pick, but worse on the held-out deals (62% against 57%), so not adopted.
  Kept today's model over ElasticNet with the new features: held out 55% against 57%, but fresh 56% against 55% with a range holding 58%, and a bootstrap error change of −9 to +9 points. The rule was written before any held-out number. Uncapped paid views (75% held out), per-band ranges (wider) and a 50% headline band (holds 32-33% on the test sets) were all rejected on the numbers.
  Later the same session: the report moved into five tabs (Summary, Price, Audience, Content, Similar) with `#tab` links. Beyond WLDD's largest deal the range is no longer lifted to the market low; the market price shows separately. Public price datasets and trained models were searched for: none has per-creator prices paid (only sponsorship labels, tier rate cards, or Collabstr's US asking prices), so WLDD's deals stay the training data. An audit found them consistent (sizes match today's snapshots), with 10 extreme deals the user confirmed are correct. Stand-out extras were dropped.
