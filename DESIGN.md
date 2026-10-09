# TrueRate design

The visual source of truth for `web/`. Read it before building or changing any screen, together with the ui-craft skill.

## Where the look comes from

TrueRate is an internal WLDD tool, so it reuses WLDD's own app world instead of inventing one.

| Source | What we take |
|---|---|
| Solo app, `packages/solo_core/lib/src/constants/app_colors.dart` | The whole palette (hex values below) and the dark ground |
| Solo app, `apps/solo_app/pubspec.yaml` | Gilroy as the type intent. Gilroy is a paid font and can't ship in a public repo, so the web uses **Urbanist** (Google Fonts), the closest free geometric match |

ui-craft pipeline: step 1 (reference research) is skipped because this world is preserved. These sub-skills are not installed, so their steps don't run until someone installs them: `impeccable`, `shadcn`, `boneyard`, `design-motion-principles`, `refero-design`.

## The brief

- **Users:** the WLDD campaign team, on laptops. Design for 1280×720 to 1512×850 first. Those screens are short, not narrow.
- **The job:** the team pastes a creator and must read **what to pay** and **book or not** within a few seconds, mid-negotiation. Everything else is supporting evidence.
- **Content:** money in INR with Indian grouping (`₹56,500`, `₹1,80,000`), counts compact (`45K`, `1.8L`, `1.2Cr`), and many percentages. Every number shows its basis and a comparison (see the copy rules).

## Tokens

Dark only. Solo is dark, and there is no light mode in scope.

| Token | Value | Solo name | Use |
|---|---|---|---|
| `--bg` | `#131313` | black | page ground |
| `--surface` | `#202020` | lighterBlack | panels, table headers, inputs |
| `--text` | `#FBFBFB` | white | body and figures |
| `--text-muted` | `#FBFBFB` at 64% | — | labels, basis lines |
| `--accent` | `#96FF43` | primary / green | primary action, focus ring, the creator's own series in charts |
| `--go` | `#96FF43` | green | Go, Real audience, ok checks |
| `--negotiate` | `#FFF136` | yellow | Negotiate, Some fake activity, warn checks |
| `--avoid` | `#F5666E` | red | Avoid, Mostly fake, bad checks, red flags |
| `--info` | `#97BAFF` | lighterBlue | links, neutral highlights, peer series |
| `--strong-go` / `--strong-negotiate` / `--strong-avoid` | `#73F50E` / `#EDC500` / `#F44336` | darkGreen / yellowDark / brightRed | hover and pressed states only |

Pink (`#FF006B`, `#FF90E8`) and orange (`#F76B3E`) are Solo colors we don't use. Three state colors are enough, and a fourth would read as decoration.

**Type:** Urbanist 400 / 600 / 700. Every figure uses `font-variant-numeric: tabular-nums`. Check that Urbanist ships `tnum` on day one; if it doesn't, figures use IBM Plex Sans.
- Price headline: `clamp(2.75rem, min(6vw, 12vh), 5rem)`. The `vh` term keeps it on short laptops.
- Section titles: 1.125rem/600.
- Body: 0.9375rem/400. Basis lines: 0.8125rem, muted.

**Space:** 4px base. Tight inside a block (8–12px), loose between blocks (40–64px). Don't use one gap everywhere.

**Radius:** 8px for controls, 12px for panels. Nothing above 12px.

## Screens and what is loud

| Screen | Loud | Quiet |
|---|---|---|
| Analyze (`/`) | The handle input and its button, on the first screen at every size | Optional inputs (product category, quote, budget), recent analyses list |
| Report (`/analyses/[id]`) | One composed decision block: price range, recommended price, Go/Negotiate/Avoid chip, verdict scale, expected views, likes and comments | Waterfall with its 6 comparable deals, and the quote checker, next. Then the five evidence sections, each a different shape: authenticity checks as a dense table; engagement as one percentile bar; placement as one full-width reel chart with consistency, paid-vs-own and collab-vs-own as plain lines under it; audience as a mix bar plus languages plus one "worth reaching" sentence; comparables as a table |
| Batch (`/batch/[id]`) | The ranked table | Progress line |
| Rate card (`/rate-card`) | The calculator result | Categories as a table with an inline bar for ₹ per 1,000 views, not a grid of same-size cards |
| About (`/about`) | Predicted-vs-actual chart | Input → verdict → price diagram; signals-and-why table; error by band and by category; baselines; fake-creator test; other page types; known limits. The pitch deck reuses these, in the same tokens |
| Print (`/analyses/[id]/print`) | Same decision block, A4, black on white (print exception to dark-only) | — |

The decision block is earned by the brief: the price is the product's entire answer. Under it, show expected views and cost per 1,000 views as one sentence with its comparison, never as a row of three stat cards.

## Components and charts

- Primitives: shadcn/ui on Radix (Select, Tooltip, Tabs, Dialog), themed with the tokens above. Icons: Lucide.
- Charts: Recharts.
  - The creator is `--accent`, peers are `--info` at 60%, sponsored reels are marked with `--negotiate`.
  - Axes use compact numbers.
  - No gridlines except a faint baseline.
- Tables: right-aligned figures, tabular numerals, sticky header on long tables.

## States

- **Loading an analysis:** the four API steps as a list. The current step gets a moving bar; finished steps get a check. No spinner looping with nothing to say.
- **Empty:** one plain sentence and the input focused. Nothing else.
- **Error:** the API's message as a sentence, plus a Retry button. Out-of-scope (private or faceless) is not an error: say why, calmly.

## Motion

- Step progress and hover/focus transitions only: 120–180ms ease-out.
- Respect `prefers-reduced-motion`.
- No entrance animations on sections and nothing infinite.

## Browser surfaces

- `::selection`: `--accent` background, `--bg` text.
- `caret-color: var(--accent)`.
- Focus ring: 2px `--accent`, 2px offset.
- Dark scrollbars (`color-scheme: dark`).
- Link underline offset: 3px.

## Copy

- Sentence case. No eyebrow labels above headings. No headings ending in a full stop. No em dashes.
- **Verdict names:** Real audience, Some fake activity, Mostly fake. All three are always visible on the scale, with the current one lit.
- **Decision names:** Go, Negotiate, Avoid.
- **Every number states what it is based on and what it's compared with.** For example: "6% (12 of 200 likers checked) · similar creators 8%". Never a bare score like "90% genuine".
- Never write "transform", "seamless", "supercharge" or "all-in-one".

## Refuse in this project

- Glow, gradients or neon on the lime. It's a flat accent.
- Hero → three cards → CTA.
- A row of same-size KPI cards.
- Uppercase labels longer than three words.
- 24px+ radius.
- Decorative grid backgrounds.

## Verify before calling a screen done

Install ui-craft once (Node 18+, Chrome):

```
git clone https://github.com/XploY04/shaktiyan.git
cp -R shaktiyan/skills/ui-craft ~/.claude/skills/
cd ~/.claude/skills/ui-craft/scripts && npm install
```

With `make api` and `make web` running:

```
cd ~/.claude/skills/ui-craft/scripts
node audit.mjs     http://localhost:3000 / /batch /rate-card /about
node slop-scan.mjs http://localhost:3000
```

`audit.mjs` must pass. `slop-scan.mjs` is advisory: fix every hit you can't justify from this brief.
