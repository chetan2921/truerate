# truerate

Goal: prototype for the WLDD hackathon (Problem 02), built so WLDD can adopt it. Prototype rules: tests cover what is being proven (pricing maths, the fake-audience verdict, the parsers), and edge cases outside the demo path are skipped on purpose.

Repos: truerate (one monorepo: `api/`, `web/`)

## Who and what

The WLDD campaign team, when onboarding or discovering a creator. They paste an Instagram face creator, optionally with a product category, the creator's quoted price and a budget. TrueRate answers two questions:

1. What should WLDD pay for one reel? A fair price, a range, and the views it should buy.
2. Should WLDD book this creator for this product? Go, Negotiate or Avoid, with data-backed reasons.

Prices are learned from WLDD's own 150 past deals (handle, tier, niche, price paid; confidential, never committed).

## Flows

### Login
A one-click "Demo login" button, or an email that must end in `@wldd.in` (checked in the front end only). A cookie is set, and every other page redirects to `/login` without it.

### Analyze a creator (the main flow)
1. `/` shows a handle-or-link input. Product category, quoted price and budget are optional fields under it. Recent analyses are listed below.
2. Submit: `POST /api/analyses` returns an id, and the page moves to `/analyses/[id]`.
3. The page polls every 1.5 s and shows 4 steps: reading profile, reels and audience · spotting ads and measuring reels · checking audience quality · calculating fair price.
4. The report shows:
   - the decision block: price range, recommended price, Go/Negotiate/Avoid, verdict scale, expected views
   - the price waterfall
   - the quote checker
   - competitor-conflict warning, if any
   - evidence sections: audience checks, engagement vs similar creators, last 30 reels chart (views/likes/comments/followers toggle), audience and category, similar creators WLDD paid and cheaper alternatives
   - the negotiation lines
5. Failures:
   - A private account or faceless page gets status `out_of_scope` with the reason in one sentence.
   - An API error gets status `failed` with the message and a Retry button.

### Quote check
Type a quote on the report: `POST /api/analyses/{id}/quote` returns below/within/above range, the difference, a counter-offer and 3 talking points. No re-scraping.

### Batch shortlist
`/batch`: paste up to 50 handles plus product and budget. `/batch/[id]` polls a table ranked by cost per 1,000 views, with an Export CSV button.

### Rate card
`/rate-card`: ₹ per 1,000 views and typical reel price per category, from WLDD's deals, plus a calculator: category + views wanted → total budget range.

### Client one-pager
`/analyses/[id]/print` shows the decision block, waterfall and red flags on A4, then opens the browser print dialog.

### About (for judges)
`/about`: how it works, accuracy on 30 held-out creators vs two baselines, the fake-creator test results, and the strategy for other page types (static text).

## Milestones

1. **Data in.** Done when: 150 deals are in Mongo (30 held out, 10 per tier) and at least 140 creators have a stored snapshot with 12 or more reels.
2. **Price v1.** Done when: `truerate validate` prints a holdout median error lower than both baselines (band median, Modash-style formula).
3. **Audience check.** Done when: the verdict and genuine share feed the price, and `truerate redteam` catches at least 80% of the flat-views, bot-likers, pod-comments and bought-followers fakes.
4. **API + report.** Done when: entering a never-seen face creator on `/` shows the full report within 2 minutes, and `audit.mjs` passes on `/` and the report.
5. **Extras.** Done when: batch, rate card, quote check, competitor conflict, cheaper alternatives, print page and About all work on real data.

Not in scope: watchlist, post-campaign check, UGC pricing, brand-handle input, deployment, real auth, light mode.

## Stack

| Layer | Choice | Why |
|-------|--------|-----|
| front end | Next.js 16 (App Router, TS), Tailwind 4, shadcn/ui, Recharts | Chetan's choice; look and rules in `DESIGN.md` |
| back end | FastAPI, Python 3.12 via uv | Python has the ML libraries; mediapipe doesn't run on 3.14 |
| data | MongoDB (pymongo), URL in `.env`; model files in `data/models/` | Chetan's choice |
| Instagram data | HikerAPI, every call cached in Mongo for 24 h | WLDD already uses it |
| ML | scikit-learn (Ridge, KNN, RandomForest, IsolationForest), networkx Louvain, MiniLM (`paraphrase-multilingual-MiniLM-L12-v2`), MediaPipe face detection | Decided in planning; nothing optional |
| LLM | Gemini via `google-genai` on a free key | No Claude API; prices are never sent to it |
| auth | demo login + `@wldd.in` front-end check | Internal prototype |
| hosting | local only (`make api`, `make web`) | Not deployed |

## Architecture

**api/truerate/** (one file per job):

| File | Job |
|---|---|
| `config.py` | settings from `.env` |
| `db.py` | Mongo client, collections, indexes |
| `instagram.py` | HikerAPI client, cache, parse to plain dicts |
| `signals.py` | reel stats, ad labels, fake accounts, comments and pods, face check, verdict |
| `pricing.py` | training frame, Ridge+KNN, adjustments, range, quote, decision, rate card, comparables |
| `pipeline.py` | one creator → result |
| `app.py` | FastAPI routes and the background job thread pool |
| `cli.py` | import, collect, build, validate, redteam |

**Mongo collections:**

| Collection | Contents |
|---|---|
| `deals` | `{handle, tier, niche, price, holdout}` |
| `snapshots` | `{handle, fetched_at, followers, data}`. One per fetch, so follower history comes free |
| `metrics` | `{_id: handle, computed_at, ...}` |
| `analyses` | `{_id, handle, inputs, status, steps, result, error, batch_id, created_at, finished_at}` |
| `batches` | batch records |
| `cache` | HikerAPI responses, TTL index 24 h |
| `accounts` | looked-up brand and commenter accounts, TTL index 30 days |

**API:**

| Method | Path | Returns |
|---|---|---|
| GET | `/api/health` | `{ok}` |
| GET | `/api/meta` | categories, range coverage % |
| POST | `/api/analyses` | `{id}`, status 202 |
| GET | `/api/analyses` | recent analyses |
| GET | `/api/analyses/{id}` | status, steps, result |
| POST | `/api/analyses/{id}/quote` | quote check |
| POST | `/api/batches` | `{id}` |
| GET | `/api/batches/{id}` | ranked rows |
| GET | `/api/rate-card` | category rates |
| GET | `/api/model-report` | holdout + red-team results |

Response models are Pydantic. The web types are generated from `/openapi.json` (see `.claude/contracts/api-surface.md`).

**Pricing:**
- Market price is a blend in log space of Ridge on log(price) (log views, log followers, engagement, comments per 1K views, category) and KNN, where the 6 nearest past deals' ₹ per 1,000 views is multiplied by this creator's views. The blend weight is picked by leave-one-out.
- Fair price = market × collab factor × genuine share, rounded to ₹500.
- **Collab factor:**
  - Measure how many views this creator's sponsored reels keep, relative to their normal reels.
  - With a product category, use their ads in that category, pulled toward the population ratio for matching or non-matching ads.
  - Shrinkage: `(n·r + 3·prior)/(n + 3)`.
  - Divide by the typical ratio, because past prices already include the usual drop.
- **Range:** the 10th/90th percentile of leave-one-out residuals.
- **Decision:**
  - Avoid = mostly fake, weak product fit, or a competitor promoted in the last 60 days.
  - Negotiate = some fake activity, quote above range, or sponsored reels drop more than usual.
  - Otherwise Go.

**Audience check:**
- Checks are compared with WLDD creators in the same follower band:
  - fake-looking likers
  - fake-looking new followers
  - views per follower
  - likes per view
  - likes too even across reels
  - generic comments
  - repeated comment text
  - comment groups (repeat commenters, Louvain rings across creators)
  - former usernames
  - IsolationForest
- **Verdict:**
  - 0 failing families (likes, followers, comments) = Real audience
  - 1 = Some fake activity
  - 2 or more = Mostly fake
- **Genuine share** subtracts only the fake engagement above the band median.

**Ads:**
- Rules first: paid-partnership label, sponsor tags, ASCI hashtags, brand tag plus code or link.
- Then one Gemini call per creator labels ambiguous reels (with cover images), every reel's topic, and the comment languages.

**Deliberately not built:** real auth, deployment, follower history before our first snapshot (Instagram doesn't expose it).
