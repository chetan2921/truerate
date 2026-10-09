# truerate

TrueRate is an internal WLDD tool. Paste an Instagram face creator, optionally with a product category, a quoted price and a budget. It tells you what one reel is worth and whether to book them (Go, Negotiate, Avoid). One repo: `api/` (FastAPI, MongoDB, scikit-learn) prices and checks creators; `web/` (Next.js) shows the report. Built for the WLDD hackathon, Problem 02.

## Repos
| Repo | What it is | Mapped from | Context |
|------|-----------|-------------|---------|
| truerate (this folder, `.`) | api + web monorepo | `main` @ 39dc687 | `.claude/truerate/AGENTS.md`; subsystems `.claude/truerate/api/AGENTS.md`, `.claude/truerate/web/AGENTS.md` |

## Products
| Product | Repos | Plan |
|---------|-------|------|
| truerate | truerate (`api/`, `web/`) | `.claude/plan/truerate/` |

## Contracts
| Seam | What must agree | File |
|------|-----------------|------|
| api-surface | FastAPI routes and response models, and the web client plus its generated types | `.claude/contracts/api-surface.md` |

Facts that span repos live in the contract, not in a repo file. Read it before
changing either side, and update it when a side moves.

## Project rules
- The repo is public. Never commit `data/`, `.env`, keys, or anything that pairs a creator handle with a WLDD deal price.
- Deal prices are never sent to an LLM.
- UI work follows `DESIGN.md` and the ui-craft skill. A screen is done only when ui-craft's `audit.mjs` passes on it.
- Commits: `git commit -s`, no AI or Claude attribution anywhere. Push to `origin main` after each milestone, with the full suite green.

## Navigate
Working in a repo: `.claude/<repo>/AGENTS.md`, and for `api/` or `web/` their
own file under `.claude/truerate/`. Looking for a symbol or a file:
`.claude/<repo>/STRUCTURE.md`. Building a feature: that product's `SPEC.md` for
what it should do and `IMPLEMENTATION.md` for where the work stands. Building or
changing UI: `DESIGN.md`. Changing a seam: the contract. Wondering why something
is the way it is: `.claude/HISTORY.md`, newest lines last. Read what the task
needs, never the tree.

## Trust, then update
A context file is only true for the commit it was read from. Before relying on
one, check its footer stamp. In this workspace the repo is the workspace root,
so stamps name it `.`:

    git -C <repo> diff --stat <sha from the footer>..HEAD -- <paths from the footer>

Empty output means it still describes the code. Anything else names what to
re-read: re-read those files, rewrite the context file, and re-stamp it with the
current sha.

Sweep every stamp at once, from the workspace root, after a pull, a merge, or a
branch switch:

    grep -rl '<!-- mapped:' .claude --include='*.md' | while read -r f; do
      line=$(grep -o '<!-- mapped: .* -->' "$f" | head -1)
      repo=${line#<!-- mapped: }; repo=${repo%%@*}
      rest=${line#*@};            sha=${rest%% *}
      paths=${line#*paths: };     paths=${paths% -->}
      out=$(git -C "$repo" diff --stat "$sha"..HEAD -- $(echo "$paths" | tr ',' ' ') 2>&1)
      if [ -n "$out" ]; then printf '\n=== %s\n%s\n' "$f" "$out"; fi
    done

Every file it prints is a file to rewrite before trusting. The `tr` is not
decoration: zsh splits a command substitution into words but never a parameter
expansion, so the obvious `${paths//,/ }` passes one argument in zsh and reports
every file clean.

## Update as you go
When a session does the thing on the left, it updates the file on the right
before it ends. Not next session, not when someone notices.

| What happened | What to update |
|---------------|----------------|
| new folder, service, entry point, or dependency | `.claude/<repo>/AGENTS.md` |
| function added or removed, signature changed | `.claude/<repo>/STRUCTURE.md` |
| either side of a seam moved | the contract, and every side it names |
| a checklist step or milestone landed | the product's `IMPLEMENTATION.md` |
| a test added, or a testing lesson learned | the product's `TESTING.md` |
| a decision that contradicts the spec | `SPEC.md`, or the spec becomes fiction |
| a visual decision changed (tokens, type, layout rules) | `DESIGN.md` |
| a repo added, removed, or renamed | the Repos table, then map it |
| a new seam between repos appeared | a new file in `.claude/contracts/` |
| a folder grew into its own subsystem | give it its own `AGENTS.md` pair |

Re-stamp every mapped file you rewrite. A rewritten file with an old stamp is
worse than a stale file, because the sweep will now call it clean.

## Before the session ends
A session that changed anything: make the updates above, then add one line to
`.claude/HISTORY.md`. A session that only answered questions writes nothing.

## HISTORY.md
One line per session, newest last:

    - 2026-09-16 auth: swapped session cookies for JWT in api and app. Contract
      `auth-token` updated. Mobile clients below 2.3 now fail to log in.

A session that made a decision someone will question later adds a short
indented block under its line: what was chosen, what it was chosen over, and
why. That is rare. Most sessions are one line.

Past 120 lines, fold the oldest half into one paragraph at the top under
`## Before <date>`, keeping decisions and reasons, dropping routine detail.
Folded paragraphs are never re-folded or merged; summarising a summary loses
what the summary was for.

## Compression
The tree stays flat as the project grows. Only the work in flight is written out
in full.

- `IMPLEMENTATION.md`: one checklist, for the current item only. A finished item
  becomes one dated line under `## Done`.
- `HISTORY.md`: one line per session, folded as above.
- Repo files: one per repo. A nested folder file only for a real subsystem.
- Everything else: point at where the truth lives instead of restating it.

## Re-running
Re-run `/repo-setup` after a large merge, when a repo is added or removed, or
when the sweep prints more files than you want to fix by hand.

Tracking: committed to truerate (public GitHub repo chetan2921/truerate)
Layout: central
