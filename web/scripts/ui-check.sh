#!/usr/bin/env bash
# ui-craft's audit and slop scan, run behind TrueRate's demo login. Needs ui-craft installed (DESIGN.md, Verify)
# and the API and web running. usage: web/scripts/ui-check.sh <report path> [more paths]
#   e.g. web/scripts/ui-check.sh /analyses/demo-fake /login
set -euo pipefail
SRC="$HOME/.claude/skills/ui-craft/scripts"
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="${BASE:-http://localhost:3000}"
TMP="$(mktemp -d)"
ln -s "$SRC/node_modules" "$TMP/node_modules"
cp "$SRC/package.json" "$HERE/first-screen.mjs" "$TMP/"
# Every page the scripts open gets the demo session cookie before it loads.
for f in audit.mjs slop-scan.mjs; do
  node -e '
    const fs = require("fs"); const [src, dst, base] = process.argv.slice(1);
    const line = "const browser = await chromium.launch({ channel: '"'"'chrome'"'"' });\n";
    const s = fs.readFileSync(src, "utf8");
    if (!s.includes(line)) throw new Error("ui-craft changed: no launch line in " + src);
    fs.writeFileSync(dst, s.replace(line, line + "const _np = browser.newPage.bind(browser); browser.newPage = async (o) => { const p = await _np(o); await p.context().addCookies([{ name: \"truerate_session\", value: \"demo\", url: \"" + base + "\" }]); return p; };\n"));
  ' "$SRC/$f" "$TMP/$f" "$BASE"
done
cd "$TMP"
# "/" first: the first-screen matrix runs on the first route, and "/" has the real primary action.
node audit.mjs "$BASE" / "$@"
node first-screen.mjs "$BASE" "$1"
for r in / "$@"; do node slop-scan.mjs "$BASE$r" | grep -vE '^\s+clear'; done
