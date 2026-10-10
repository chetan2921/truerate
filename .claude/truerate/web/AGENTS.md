# web

The Next.js front end the WLDD team uses: login, analyze, report with a quote checker, client one-pager, batch shortlist, rate card and About.

## Stack
- Next.js 16 (App Router, `cacheComponents` on), React 19, TypeScript, Tailwind 4, ESLint. npm, not pnpm.
- Recharts (charts), Lucide (icons), `openapi-typescript` (types from the API), `playwright-core` (dev only, screenshots). `devIndicators` is off so screenshots stay clean.

## Run
- `make web` from the repo root: http://localhost:3000. The API base is `NEXT_PUBLIC_API_URL` (default http://localhost:8000).
- `cd web && npm run lint && npm run build` before calling anything done.
- `web/scripts/ui-check.sh /analyses/<id> /login`: ui-craft's audit and slop scan behind the demo login, plus the report's first-screen check (`DESIGN.md`, Verify).
- Before the 150 real creators exist, build screens against synthetic data: `cd api && uv run python scripts/seed_dev.py`, then run the API with `MONGODB_DB=truerate_dev MODELS_DIR=data/models_dev`. Never start a batch or analysis from the UI against the dev API: it calls HikerAPI for real.

## Entry points
- `src/proxy.ts`: sends any page without the `truerate_session` cookie to `/login` (Next 16 calls middleware "proxy")
- `src/app/login/`: demo login button and the `@wldd.in` check; sets the cookie in the browser
- `src/app/(app)/layout.tsx`: header with sign-out for every signed-in page
- `src/app/(app)/page.tsx`: `/`, the analyze form and recent analyses
- `src/app/(app)/analyses/[id]/`: `page.tsx` (Suspense around params) and `analysis-view.tsx` (polls every 1.5 s; running, out of scope, failed with Retry, done)
- `src/app/(app)/analyses/[id]/print/`: the A4 client one-pager, black on white; opens the print dialog
- `src/app/(app)/batch/`: paste form; `batch/[id]/` polls the ranked table and exports CSV
- `src/app/(app)/rate-card/`: calculator plus the category table
- `src/app/(app)/about/`: `page.tsx` (accuracy chart and tables, fake test, flow, signals, other pages, limits) and `content.ts` (static text, condensed from SPEC)
- `src/app/(app)/nav.tsx`: header nav; `layout.tsx` wraps it in Suspense because it reads the path
- `src/components/report/`: `report.tsx` lays the report out in five tabs through `tabs.tsx` (ARIA tabs, `#tab` deep links, sticky bar, each panel mounted on first open): Summary (`decision`, `negotiation`), Price (`waterfall` with the 6 comparables, `quote`, `CheaperCreators` from `evidence`), Audience (`authenticity`, `engagement`, `audience`), Content (`placement`, Recharts), Similar (`Suggestions` from `evidence`). A heading id must never equal a tab key, or the hash would scroll to it.
- `src/app/(app)/brand/`: the brand form with recent runs, and `[id]/brand-view.tsx` (polls the run); `src/components/brand/result.tsx` draws the result
- `src/components/chart-tip.tsx`: the hover/focus card every hand-drawn chart uses; `src/components/value-bars.tsx`: the ranked "What ₹10,000 buys" bars (batch and brand)
- `src/components/verdicts.tsx`: the plain verdict list and `StatusIcon` (icon plus word, never colour alone)
- `src/components/batch/compare.tsx`: the batch page's recommendation, scorecard and three CSS bar charts (price against budget, what ₹10,000 buys, expected views)
- `src/components/chips.tsx`: decision chip and verdict colours
- `src/lib/api.ts` (fetch calls), `src/lib/api-types.ts` (generated, `make types`), `src/lib/format.ts` (₹ with Indian grouping, K/L/Cr, percentages)

## Folder map
- `src/app/`: routes. Pages and flows are in `.claude/plan/truerate/SPEC.md`.
- `src/components/`: report sections and shared bits
- `scripts/`: `ui-check.sh` and `first-screen.mjs` (ui-craft behind the login), `report-shot.mjs` (the decision block as a PNG for the deck, through `playwright-core` and the installed Chrome)
- `AGENTS.md`, `CLAUDE.md` (in `web/`): written by Next.js itself and re-added by `next dev`. Keep them committed.

## Sharp edges
- This Next.js has breaking changes from older versions. Read the guide in `web/node_modules/next/dist/docs/` before writing a route, layout or data-fetching code.
- Next keeps visited pages alive (`<Activity>`): state survives navigation. Reset transient state (busy flags, submitted forms) in a `useLayoutEffect` cleanup; effects re-run when a page is shown again.
- `cacheComponents` is on: reading `params`, `searchParams` or `usePathname()` outside `<Suspense>` fails the build. Read params inside Suspense, and query strings in the browser.
- Section rhythm: put the gap on the `section` itself (padding), varied by weight. ui-craft's slop scan reads section padding, and one gap everywhere fires it.
- In the in-app browser, Next's live-reload socket fails, so reload by hand after an edit; a page can sit on "Loading…" while the dev server compiles a new route.
- Look and copy rules live in `DESIGN.md`. A screen is done when `web/scripts/ui-check.sh` passes on it.
- API calls go through `src/lib/api.ts` with generated types (`.claude/contracts/api-surface.md`). Never hand-write a response type.
- React's compiler lint forbids reassigning a variable during render: put running totals in a helper outside the component (see `waterfall.tsx`).
- The in-app preview tool can't read this repo, so run `make api` and `make web` from a terminal and open localhost.

<!-- mapped: .@8cab386 | paths: web/src/, web/package.json, web/next.config.ts, web/scripts/ -->
