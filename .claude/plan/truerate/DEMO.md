# TruRate demo (3 minutes)

## Before judging (the evening before, then 30 minutes before)
1. All six live steps in `IMPLEMENTATION.md` have run, so the deck and About show real numbers: `cd api && uv run python scripts/make_deck.py` writes `data/pitch/TruRate.pptx` (12 slides, numbers from `data/models/`).
2. Pick 2 face creators WLDD has never booked: one genuine, one suspicious (unusually even views, or a comment section full of emoji). Run both on `/` beforehand. Their analyses stay in Mongo and every HikerAPI response is kept on disk (`data/hikerapi/`), so a re-run spends no credit, takes seconds, and the old report opens by URL.
3. `make api` and `make web`, then log in with Demo login. Keep tabs open on `/`, both reports, `/about` and `/rate-card`.
4. Take the deck screenshot from a genuine creator's report: `cd web && node scripts/report-shot.mjs <analysis id>` (run it from `web/`, or it saves outside the repo). It captures only the decision block; the comparables table under it pairs WLDD creators with prices, which must never reach a slide.

## Real runs already in Mongo (2026-10-11)
Open them with the API on the real database:
| What | Path | Shows |
|---|---|---|
| vaibhavsisinty (21.7L followers) | `/analyses/068924023341` | Go. "Pay about ₹2,31,500" with the likely band: past WLDD's largest deal the price leans on the WLDD-discounted market rate, and the web check found his own listing (₹80,000 to ₹1,00,000, The Media Ant). The deck screenshot comes from this one |
| sejalkumar1195 | `/analyses/b254c99898a5` | Negotiate: a possible competitor (exclusivity check). Saved before today's pricing, so its numbers are the old ones |
| mostlysane | `/analyses/bee87c3f8952` | Negotiate: competitor, weak sponsored reach |
| foodtalkindia | `/analyses/a93e7df66811` | Out of scope: a food platform, only 1 of 10 covers shows someone on camera |
| riddhiii.vaishnav | `/analyses/512ada822e9d` | Some fake activity (likes too even), 3.4K followers. A private individual: use it on screen, never on a slide |
| A 3-creator batch | `/batch/b4488b3a59fc` | Who to book first and why, the cheapest-views alternative, "What ₹10,000 buys", the scorecard |
| boAt (@boat.nirvana) | `/brand/b546f14bfdc3` | Brand match: a ₹2,00,000 plan of 6 creators with about 23.4L views, best matches, the accounts seen with boAt |

A fresh unseen creator takes about 35 s live, one seen before about 25 s, and one bigger than any WLDD deal about 56 s (the web check). A brand run takes about 12 s.

## The three minutes
| Time | Show | Say |
|---|---|---|
| 0:00 | Deck slides 1 and 2 | Brands overpay for audiences that aren't there. TruRate says what one reel is worth and whether to book |
| 0:15 | `/`: paste a judge's creator (or a genuine one) with a product and a quote | Instagram data, ads and reels, audience check, price |
| 0:50 | The report, Summary tab | "Pay about", the likely band and the full range, then plain answers: real audience, good value, reliable, ads work, fit, rival ad. Hover a chart for its numbers. Price tab for the 6 WLDD deals behind it |
| 1:25 | The big creator's report | Past WLDD's deals the price leans on the market, discounted the way WLDD pays, and the web check found his own listed price |
| 1:45 | `/batch/b4488b3a59fc` and `/brand/b546f14bfdc3` | Who to book and why; for a brand, the set that brings the most views within budget |
| 2:20 | Deck slides 6 to 8 | 70% of held-out prices within 2× of what WLDD paid, beating both baselines on every score; six models tested on unseen deals, the simplest held up; why the range is wide, honestly |
| 2:50 | Close | Built to resist gaming (slide 9); every campaign can feed back into the model |

## Fallback
- Live analysis slower than about 60 seconds: open the same creator's pre-run report from Recent analyses and say so.
- HikerAPI or Gemini down: everything on the pre-run reports, About and the rate card comes from Mongo and `data/models`, so the demo runs offline after step 2.
- Out of scope (private or faceless): that is a feature. Read the reason out, then switch to the genuine creator.
