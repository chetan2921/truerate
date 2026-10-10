# truerate demo (3 minutes)

## Before judging (the evening before, then 30 minutes before)
1. All six live steps in `IMPLEMENTATION.md` have run, so the deck and About show real numbers: `uv run python scripts/make_deck.py` writes `data/pitch/TrueRate.pptx`.
2. Pick 2 face creators WLDD has never booked: one genuine, one suspicious (unusually even views, or a comment section full of emoji). Run both on `/` beforehand. Their analyses stay in Mongo and every HikerAPI response is kept on disk (`data/hikerapi/`), so a re-run spends no credit, takes seconds, and the old report opens by URL.
3. `make api` and `make web`, then log in with Demo login. Keep tabs open on `/`, both reports, `/about` and `/rate-card`.
4. Take the deck screenshot from the genuine creator's report: `node web/scripts/report-shot.mjs <analysis id>`. It captures only the decision block; the comparables table under it pairs WLDD creators with prices, which must never reach a slide.

## Real analyses already in Mongo (2026-10-10)
Open them at `/analyses/<id>` with the API on the real database:
| Creator | Id | Shows |
|---|---|---|
| sejalkumar1195 | `b254c99898a5` | Negotiate: a possible competitor (exclusivity check) and the note for a creator bigger than any WLDD deal. The deck screenshot comes from this one |
| mostlysane | `bee87c3f8952` | Negotiate: competitor, weak sponsored reach, out-of-range note |
| shresthvg | `b563b4ebfc74` | Out of scope: only 1 of 10 covers shows a face |
| riddhiii.vaishnav | `512ada822e9d` | Some fake activity (likes too even), 3.4K followers. A private individual: use it on screen, never on a slide |

A fresh unseen creator takes 90 to 111 s live. One whose Instagram data is already saved takes about 45 s.

## The three minutes
| Time | Show | Say |
|---|---|---|
| 0:00 | Deck slides 1 to 2 | Brands overpay for audiences that aren't there. TrueRate says what one reel is worth and whether to book |
| 0:20 | `/`: paste a judge's creator (or the genuine one) with a product and a quote | The four steps: Instagram data, ads and reels, audience check, price |
| 1:10 | The report | The price, the range and Go/Negotiate/Avoid come first. Then expected views at ₹ per 1,000 against the category, the waterfall with its 6 WLDD deals, and a quote check |
| 1:50 | The suspicious creator's report | The red flags with numbers and sample sizes, the verdict, and the fake-engagement step in the waterfall |
| 2:20 | `/about` | Held-out error against both baselines, the fake-creator test including the smart fake, and pages without a face |
| 2:50 | Close | Batch shortlist and rate card exist for the negotiation itself |

## Fallback
- Live analysis slower than about 60 seconds: open the same creator's pre-run report from Recent analyses and say so.
- HikerAPI or Gemini down: everything on the pre-run reports, About and the rate card comes from Mongo and `data/models`, so the demo runs offline after step 2.
- Out of scope (private or faceless): that is a feature. Read the reason out, then switch to the genuine creator.
