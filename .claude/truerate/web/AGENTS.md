# web

The Next.js front end the WLDD team uses: login, analyze, report, and later batch, rate card, print page and About.

## Stack
- Next.js 16 (App Router, `cacheComponents` on), React 19, TypeScript, Tailwind 4, ESLint. npm, not pnpm.
- Recharts (reel chart), Lucide (icons), `openapi-typescript` (types from the API).

## Run
- `make web` from the repo root: http://localhost:3000. The API base is `NEXT_PUBLIC_API_URL` (default http://localhost:8000).
- `cd web && npm run lint && npm run build` before calling anything done.
- `web/scripts/ui-check.sh /analyses/<id> /login`: ui-craft's audit and slop scan behind the demo login, plus the report's first-screen check (`DESIGN.md`, Verify).
- Before the 150 real creators exist, build screens against synthetic analyses: run the API with `MONGODB_DB=truerate_dev` (seeded from the pipeline tests' synthetic world).

## Entry points
- `src/proxy.ts`: sends any page without the `truerate_session` cookie to `/login` (Next 16 calls middleware "proxy")
- `src/app/login/`: demo login button and the `@wldd.in` check; sets the cookie in the browser
- `src/app/(app)/layout.tsx`: header with sign-out for every signed-in page
- `src/app/(app)/page.tsx`: `/`, the analyze form and recent analyses
- `src/app/(app)/analyses/[id]/`: `page.tsx` (Suspense around params) and `analysis-view.tsx` (polls every 1.5 s; running, out of scope, failed with Retry, done)
- `src/components/report/`: `report.tsx` composes `decision`, `waterfall` (with the 6 comparables), `authenticity`, `engagement`, `placement` (Recharts), `audience`, `evidence`, `negotiation`
- `src/components/chips.tsx`: decision chip and verdict colours
- `src/lib/api.ts` (fetch calls), `src/lib/api-types.ts` (generated, `make types`), `src/lib/format.ts` (₹ with Indian grouping, K/L/Cr, percentages)

## Folder map
- `src/app/`: routes. Pages and flows are in `.claude/plan/truerate/SPEC.md`.
- `src/components/`: report sections and shared bits
- `scripts/`: `ui-check.sh` and `first-screen.mjs`
- `AGENTS.md`, `CLAUDE.md` (in `web/`): written by Next.js itself and re-added by `next dev`. Keep them committed.

## Sharp edges
- This Next.js has breaking changes from older versions. Read the guide in `web/node_modules/next/dist/docs/` before writing a route, layout or data-fetching code.
- `cacheComponents` is on: reading `params` or `searchParams` outside `<Suspense>` fails the build. Read params inside Suspense, and query strings in the browser.
- Look and copy rules live in `DESIGN.md`. A screen is done when `web/scripts/ui-check.sh` passes on it.
- API calls go through `src/lib/api.ts` with generated types (`.claude/contracts/api-surface.md`). Never hand-write a response type.
- React's compiler lint forbids reassigning a variable during render: put running totals in a helper outside the component (see `waterfall.tsx`).
- The in-app preview tool can't read this repo, so run `make api` and `make web` from a terminal and open localhost.

<!-- mapped: .@0d51f07 | paths: web/src/, web/package.json, web/next.config.ts, web/scripts/ -->
