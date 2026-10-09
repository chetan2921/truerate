# web

The Next.js front end the WLDD team uses: login, analyze, report, batch, rate card, print page, About.

## Stack
- Next.js 16 (App Router), React 19, TypeScript, Tailwind 4, ESLint. npm, not pnpm.
- Planned: shadcn/ui, Recharts, Lucide, and types generated with `openapi-typescript`.

## Run
- `make web` from the repo root: http://localhost:3000
- `cd web && npm run lint && npm run build` before calling anything done

## Entry points
- `src/app/layout.tsx`: root layout, fonts, global styles
- `src/app/page.tsx`: `/` (becomes the Analyze page)
- `src/app/globals.css`: Tailwind entry; the design tokens from `DESIGN.md` go here

## Folder map
- `src/app/`: routes. Pages and flows are in `.claude/plan/truerate/SPEC.md`.
- `public/`: static assets
- `AGENTS.md`, `CLAUDE.md` (in `web/`): written by Next.js itself and re-added by `next dev`. Keep them committed.

## Sharp edges
- This Next.js has breaking changes from older versions. Read the guide in `web/node_modules/next/dist/docs/` before writing a route, layout or data-fetching code.
- Look and copy rules live in `DESIGN.md`. A screen is done when ui-craft's `audit.mjs` passes on it.
- API calls go through `src/lib/api.ts` with generated types (`.claude/contracts/api-surface.md`). Never hand-write a response type.

<!-- mapped: .@9585fbe | paths: web/src/, web/package.json, web/next.config.ts -->
