# truerate

Goal: prototype for the WLDD hackathon (Problem 02), built so WLDD can adopt it. Prototype rules: tests cover what is being proven (parsers, pricing maths, the fake-audience verdict), and edge cases outside the demo path are skipped on purpose.

Repos: truerate (one monorepo: `api/`, `web/`)

## Who and what

The WLDD campaign team, when onboarding or discovering a creator. They paste an Instagram face creator's handle or profile link, optionally with a product category, the creator's quoted price and a budget. TrueRate answers two questions:

1. What is one reel on this page really worth? A fair price, a range, what it should deliver, and how the number was reached.
2. Should WLDD book this creator for this product? Go, Negotiate or Avoid, with data-backed reasons.

Prices are learned from WLDD's 150 past deals (handle, tier, niche where known, price paid in INR; confidential, never committed). Views and engagement are not in that data; we collect them from public Instagram data. Judges test on creators we have never seen, some built to fool the audience check.

## Flows

### Login
A one-click "Demo login" button, or an email that must end in `@wldd.in` (checked in the front end only). A cookie is set, and every other page redirects to `/login` without it.

### Analyze a creator (the main flow)
1. `/` shows a handle-or-link input. Product category, quoted price and budget are optional fields under it. Recent analyses are listed below.
2. Submit: `POST /api/analyses` returns an id, and the page moves to `/analyses/[id]`.
3. The page polls every 1.5 s and shows 4 steps: reading profile, reels and audience · spotting ads and measuring reels · checking audience quality · calculating fair price.
4. The report, top to bottom:
   - **Decision block.** Price range, recommended price, Go/Negotiate/Avoid with reasons, the verdict scale (Real audience · Some fake activity · Mostly fake), and expected delivery: views, likes and comments on the sponsored reel, plus cost per 1,000 views against the category average.
   - **How the price was reached.** A waterfall: market price from WLDD's past deals → sponsored-performance adjustment → fake-engagement adjustment → recommended price. Below it, the 6 past deals it compared against.
   - **Quote checker.** Competitor-conflict warning, if any.
   - **1. Authenticity.** Verdict plus every check, each with its value, sample size and the similar-creator median. Specific red flags with evidence.
   - **2. Engagement.** Rate, similar-creator median, and "better than X% of similar creators".
   - **3. Placement performance.**
     - last 30 reels chart (views, likes, comments, followers toggle; sponsored reels marked)
     - consistency (how many of the last 10 reels reached half the usual views, and a typical bad reel)
     - trend
     - paid reels vs own reels
     - collab posts with other creators vs own reels
     - list of detected ads, disclosed or not
   - **4. Audience and niche.**
     - niche
     - who engages (fake-looking commenters, creators and brands among top commenters, comment languages)
     - whether the audience is worth reaching: category value rank, product fit, and one plain sentence combining them
   - **5. Fair price evidence.** Similar creators WLDD paid, cheaper alternatives, Instagram-suggested accounts to analyse.
   - **Negotiation lines.** Copy and Download-PDF buttons.
5. Failures:
   - A private account or faceless page gets status `out_of_scope` with the reason in one sentence.
   - An API error gets status `failed` with the message and a Retry button.

### Quote check
Type a quote on the report: `POST /api/analyses/{id}/quote` returns below/within/above range, the difference, a counter-offer and 3 talking points. No re-scraping.

### Batch shortlist
`/batch`: paste up to 50 handles plus product and budget. `/batch/[id]` polls a table ranked by cost per 1,000 views, with an Export CSV button. Judges can run their unseen set here.

### Rate card
`/rate-card`: ₹ per 1,000 views and typical reel price per category, from WLDD's deals, plus a calculator: category + views wanted → total budget range.

### Client one-pager
`/analyses/[id]/print` shows the decision block, waterfall and red flags on A4, then opens the browser print dialog.

### About (for judges)
`/about` has five parts:
- how it works: input → verdict → price diagram
- signals and why (the table below)
- accuracy: held-out creators by follower band, leave-one-out by category, both baselines, range coverage
- the fake-creator test, including the smart fake
- strategy for other page types, plus known limits

The pitch deck uses the same content.

## Problem statement coverage

| PDF asks for | How TrueRate answers it | Milestone |
|---|---|---|
| The problem: bought followers, seeded views, engagement pods | Followers: newest-follower quality, views per follower. Seeded views: likes per view, likes too even. Pods: repeat commenters, Louvain rings | 3 |
| Put in any face creator's profile | Handle or profile-link input; face check on reel covers; private or faceless gets `out_of_scope` | 4 |
| Authenticity: clear verdict | 3-level verdict from 3 check families (likes, followers, comments) | 3 |
| Red flags: suspicious follower spikes | Share of fake-looking accounts among the 100 newest followers (a proxy; see Known limits) | 3 |
| Red flags: engagement that doesn't fit the page's reach | Views per follower and likes per view vs similar creators | 3 |
| Engagement rate and comparison with similar creators | Rate, band median, percentile | 2, 4 |
| Placement: how content actually performs | Last 30 reels chart, trend | 2, 4 |
| Placement: consistency across posts | Hit count of last 10 reels; typical bad reel (25th percentile views) | 2, 4 |
| Placement: collab or paid content vs own content | Paid (disclosed + hidden ads) vs own; collab posts vs own; shown separately | 2, 4 |
| Audience: what niche | Gemini on bio + captions; CSV niche where WLDD has it | 3 |
| Audience: who actually engages | Commenter mix, top commenters' type, comment languages | 3, 4 |
| Audience: worth reaching | Category value rank + product fit, stated in one sentence | 4 |
| Fair price: cost of one reel | Recommended price + range | 2 |
| Fair price: what it's likely to deliver | Expected views, likes, comments; cost per 1,000 views vs category | 2, 4 |
| Fair price: clear explanation | Waterfall + the 6 comparable past deals | 2, 4 |
| Uses past references and current analytics | Ridge + KNN on WLDD's deals, fed this creator's current metrics | 2 |
| Reflects authenticity | Genuine share multiplies the price; a waterfall step shows the amount | 3 |
| Usable in a negotiation | Range with start offer and walk-away, quote check, talking points, PDF | 5 |
| Small, medium, big accounts; any niche | Log-scale model; accuracy reported per band and per category | 2 |
| Strategy for faceless/meme, UGC, IPs, all | Section below; About page; pitch | 5, 6 |
| Judging 1: architecture, input to verdict and price | About diagram; pitch | 5, 6 |
| Judging 2: signals and why | Signals table below; About; pitch | 5, 6 |
| Judging 3: pricing logic across sizes and niches | Pricing section; per-band and per-category accuracy | 2, 6 |
| Judging 4: resistance to gaming | Red-team with 6 fake types incl. a smart fake built to look genuine | 3 |
| Judging 5: tested against known prices | 30 held-out creators vs 2 baselines; range coverage | 2 |
| Judging 6: strategy for other page types | Section below | 5, 6 |
| Unseen creators at judging | Live analysis of any handle; batch for many | 4, 5 |

## Signals and why

| Area | Signal | Why it is there |
|---|---|---|
| Authenticity | Fake-looking likers (Kaggle-trained classifier, ~200 likers on 3 reels). It uses only the 6 fields that come with the likers list: 88% on Kaggle's 120 test accounts, against 92% with all 11, which would cost one request per account | Bought likes come from empty accounts. Like counts are cheap to fake; account quality is not |
| Authenticity | Fake-looking newest followers (up to 100) | Bought followers arrive as a block of empty accounts, so the newest followers show a recent spike |
| Authenticity | Views per follower vs similar creators | Followers bought without reach show up as views far below the follower count |
| Authenticity | Likes per view vs similar creators | Seeded views have no real viewers behind them, so few of those views turn into likes |
| Authenticity | Likes too even across reels | Bot delivery is flat; real reach is spiky |
| Authenticity | Generic and repeated comment text | Bought and pod comments are emoji-only, templated, and reused across reels |
| Authenticity | Repeat commenters on ≥60% of reels, and Louvain rings across WLDD's creators | Pods use real accounts, so only the coordination gives them away |
| Authenticity | Former usernames; IsolationForest on the overall pattern | Renamed or bought pages; fakes shaped in ways we didn't predict |
| Engagement | (likes + comments) / views on own reels, percentile within the follower band | Attention per view, comparable across account sizes |
| Placement | Paid reels' median views vs own reels, shrunk toward the typical drop when there are few ads | A brand buys sponsored performance, not organic peaks |
| Placement | Hidden-ad detection (rules, then Gemini with cover images) | Many paid reels carry no #ad; missing them corrupts the paid-vs-own comparison |
| Placement | Collab posts vs own reels | Shared-audience posts behave differently from both |
| Placement | Consistency (last 10 reels) and trend (last 10 vs previous 10) | Brands pay for the floor, and for where the creator is heading |
| Audience | Niche from bio, captions and CSV | Sets the category rate and the comparison group |
| Audience | Commenter mix and comment languages | Shows whether real people, other creators or bots engage, and which market they are in |
| Audience | Category value rank and product fit | The same views are worth more in some categories, and off-topic ads underperform |

## Milestones

1. **Data in.** Done when: 150 deals are in Mongo (30 held out, 10 per tier) and at least 140 creators have a stored snapshot with 12 or more reels.
2. **Price v1.** Done when: `truerate validate` shows a holdout median error lower than both baselines (band median, Modash-style formula), with error per follower band (holdout) and per category (leave-one-out over all 150).
3. **Audience check.** Done when: the verdict and genuine share feed the price; `truerate redteam` catches at least 80% of the flat-views, bot-likers, pod-comments and bought-followers fakes; and the smart-fake catch rate is reported, whatever it is.
4. **API + report.** Done when: entering a never-seen face creator on `/` shows the full report (all five sections, including consistency, collab vs own, who engages and worth reaching) within 2 minutes, and `audit.mjs` passes on `/` and the report.
5. **Extras.** Done when: batch, rate card, quote check, competitor conflict, cheaper alternatives, print page and About (all five parts) work on real data.
6. **Pitch.** Done when: a deck of at most 12 slides answers judging criteria 1 to 6 with real numbers from `/api/model-report`, and a 3-minute live demo on an unseen creator runs end to end, with a cached fallback.

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
| pitch | PowerPoint `.pptx`, at most 12 slides, DESIGN.md colours | Works offline on any laptop at judging; content comes from the About page |

## Architecture

**api/truerate/** (one file per job):

| File | Job |
|---|---|
| `config.py` | settings from `.env` |
| `db.py` | Mongo client, collections, indexes |
| `instagram.py` | HikerAPI client, cache, parse to plain dicts |
| `signals.py` | reel stats, consistency, paid/collab vs own, ad labels, fake accounts, comments and pods, audience mix, face check, verdict |
| `pricing.py` | training frame, Ridge+KNN, adjustments, range, expected delivery, quote, decision, rate card, comparables, validation |
| `pipeline.py` | one creator → result |
| `app.py` | FastAPI routes and the background job thread pool |
| `cli.py` | import, collect, build, validate, redteam |

**Mongo collections:**

| Collection | Contents |
|---|---|
| `deals` | `{handle, tier, niche, price, holdout}` |
| `snapshots` | `{handle, fetched_at, followers, data}`. One per fetch, so follower history builds up |
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
| GET | `/api/model-report` | validation (band and category) + red-team results |

Response models are Pydantic. The web types are generated from `/openapi.json` (see `.claude/contracts/api-surface.md`).

**Pricing:**
- Market price is a blend in log space of Ridge on log(price) (log views, log followers, engagement, comments per 1K views, category) and KNN, where the 6 nearest past deals' ₹ per 1,000 views is multiplied by this creator's views. The blend weight is picked by leave-one-out.
- Fair price = market × collab factor × genuine share, rounded to ₹500.
- **Collab factor:**
  - Measure how many views this creator's paid reels keep, relative to their own reels.
  - With a product category, use their ads in that category, pulled toward the population ratio for matching or non-matching ads.
  - Shrinkage: `(n·r + 3·prior)/(n + 3)`.
  - Divide by the typical ratio, because past prices already include the usual drop.
- **Range:** the 10th/90th percentile of leave-one-out residuals.
- **Expected delivery:** own-reel views (25th/50th/75th percentile) × the adjusted ratio. Likes and comments are those views × the creator's likes and comments per view.
- **Decision:**
  - Avoid = mostly fake, weak product fit, or a competitor promoted in the last 60 days.
  - Negotiate = some fake activity, quote above range, or paid reels drop more than usual.
  - Otherwise Go.

**Audience check:**
- Each signal in the table above is compared with WLDD creators in the same follower band (small < 20K, medium 20K–99.9K, big ≥ 100K).
- **Verdict:**
  - 0 failing families (likes, followers, comments) = Real audience
  - 1 = Some fake activity
  - 2 or more = Mostly fake
  - Former usernames and IsolationForest only warn.
- **Genuine share** subtracts only the fake engagement above the band median.

**Ads:**
- Rules first: paid-partnership label, sponsor tags, ASCI hashtags, a brand tag plus a code or link.
- Then one Gemini call per creator labels ambiguous reels (with cover images), every reel's topic, and the comment languages.
- A post co-authored with another creator counts as a collab post. A post co-authored with a brand counts as paid.

**Validation:**
- Held out: 30 creators (10 per band, seed 42), never trained on. They give the headline error, error per band, and range coverage.
- Per category: leave-one-out across all 150, because 30 creators split 7 ways is too few.
- Baselines: the band's median price, and the Modash-style formula (views/1000 × CPM × engagement modifier ±25% × 2 at 1M+ followers).
- **Red-team:** fakes built from real creators:
  - flat views
  - flat views with noise
  - bot likers
  - pod comments
  - bought followers
  - a smart fake: all of the above, mild, with specific-sounding comments
  
  Plus the flagged share of unmodified creators.

## Strategy for other page types

**Faceless and meme pages.**
- **Value signal:** reach comes from the page, so the page's delivery record replaces creator trust: typical bad reel views, stability over 30–60 days, and reach beyond followers. Add audience fit and brand safety of past content.
- **Pricing:** CPM on expected views, offered as guaranteed views with a free repost if the page under-delivers.
- **Reposts:** detected by video and audio fingerprints. A page living on reposts gets a wider range, because its views follow the content, not a loyal audience.
- **Page networks run by one owner:** found through the same reel posted within hours on several pages, shared contacts or bio links, cross-tagging, and overlapping commenters. Cross-posting makes one reel look viral several times over, so its views are counted once when pages are bundled, and one fake page puts the whole network under review.
- **Ground truth:** WLDD's own meme pages' analytics.

**UGC creators.**
- **Production fee:** a rate card by format (talking head, skit, demo), revisions and turnaround, scored against their portfolio.
- **Distribution fee:** this model applied to their own reach × genuine share. Often near zero.
- **Usage-rights fee:** for running the content as ads, per month.
- **Separating the fees:** quote "content only" and "content + post on your page"; the difference is distribution. A regression on deals that have both confirms it.
- **The real value signal:** how their content performs when brands run it as ads.

**Instagram IPs (series).**
- **Value:** retention. Measure series lift (episode views vs page average), drop-off from episode to episode, and returning commenters. Here repeat commenters are loyal fans, told apart from pods by account quality and comments that reference earlier episodes.
- **Price:** base CPM × expected episode views × series lift × integration depth (woven into the episode > one-off post > end card). Offer season packages; price later episodes on the trend.

**Across all of them.**
- **Carries over:** pricing on expected delivered views, account-quality sampling, comment checks, comparables + regression, authenticity as a discount, the validation method.
- **Changes:** the weight of creator trust (zero for meme pages), what the paid-vs-own comparison means, what repeat commenters mean, the unit priced (reel, content, series package).
- **New data needed:** repost fingerprints, an ownership graph, portfolios, usage terms, episode labels, campaign results.
- **How we check new prices are right:**
  - backtest on WLDD's past deals for that page type;
  - after every campaign, compare predicted with delivered views and recalibrate monthly;
  - run shadow prices next to human buyers before trusting the model.

## Known limits

- **Follower spikes are a proxy.** Instagram doesn't expose follower history, so the spike signal is the share of fake-looking accounts among the newest followers. Real history builds from our first snapshot onward.
- **The 150 prices were negotiated at different past dates,** but we only see creators' current stats. That noise sets a floor on accuracy, and we report the error honestly.
- **Hidden-ad detection is probabilistic.** Reels it can't call are left out of the paid-vs-own comparison.

**Deliberately not built:** real auth, deployment, follower history before our first snapshot.
