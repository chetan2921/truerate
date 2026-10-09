# truerate implementation

## Now
Milestone 1, data in. The scaffold is done (api health route, Next.js app). Next is the Mongo connection and the deals import. Waiting on Chetan for `MONGODB_URI` and `HIKERAPI_KEY` in `.env`.

### In flight: deals and Instagram data into Mongo
- [ ] add `pymongo` collections and indexes in `api/truerate/db.py`. Test (mongomock): the `cache` TTL index exists and handles are unique in `deals`
- [ ] test: importing a 33-row CSV gives 33 deals, 30 held out (10 per tier, seed 42), and re-running doesn't duplicate
- [ ] `truerate import-deals data/creators.csv` in `api/truerate/cli.py`
- [ ] record one real HikerAPI response per endpoint (profile, about, clips, comments, likers, followers, suggested) for a public account that is **not** in the deals CSV, into `api/tests/fixtures/`
- [ ] test: the parsers turn those fixtures into profile, reels (views, likes, comments, caption, taken_at, pinned, paid-partnership, sponsors, co-authors, tags, thumbnail), comments, likers and followers
- [ ] `api/truerate/instagram.py`: client (`x-access-key` header), 24 h Mongo cache, parsers
- [ ] `truerate collect <handle>` and `truerate collect-benchmark` (skips creators fetched in the last 24 h)
- [ ] live check on 2 creators: every reel has views, every comment has a time, likers and followers are non-empty
- [ ] full suite green, then stop here

## Next
- 2. Price v1: metrics (incl. consistency, paid vs own, collab vs own), Ridge+KNN, expected delivery, validation by band (holdout) and by category (leave-one-out) vs both baselines
- 3. Audience check: Kaggle fake-account model, comments and pods, Louvain, IsolationForest, MediaPipe, Gemini labels, commenter mix and languages, verdict in price, red-team with smart-fake rate reported
- 4. API + report: analyses endpoints with background jobs, login, analyze page, report page with all five sections (per `DESIGN.md`)
- 5. Extras: batch, rate card + calculator, quote check, competitor conflict, cheaper alternatives, print page, About in five parts
- 6. Pitch: deck of at most 12 slides answering judging 1–6 with real numbers, plus a 3-minute demo with a cached fallback

## Done
- 2026-10-10 Scaffold: FastAPI `api/` (Python 3.12, uv) with `/api/health`, Next.js 16 `web/`, `DESIGN.md` on Solo's palette, agent memory.
