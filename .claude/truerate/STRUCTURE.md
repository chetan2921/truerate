# truerate structure

Generated from git. Signatures only.

## Files
```
.env.example
.gitignore
Makefile
api/.python-version
api/pyproject.toml
api/tests/test_app.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/config.py
web/.gitignore
web/AGENTS.md
web/CLAUDE.md
web/README.md
web/eslint.config.mjs
web/next.config.ts
web/package.json
web/src/app/favicon.ico
web/src/app/globals.css
web/src/app/layout.tsx
web/src/app/page.tsx
web/tsconfig.json
```

## Python (api/)
```
api/tests/test_app.py:7:def test_health():
api/tests/test_app.py:11:def test_settings_read_env(monkeypatch):
api/truerate/app.py:9:def health() -> dict:
api/truerate/config.py:9:class Settings(BaseSettings):
api/truerate/config.py:21:def get_settings() -> Settings:
```

## TypeScript (web/src/)
```
web/src/app/layout.tsx:20:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/page.tsx:3:export default function Home() {
```

<!-- mapped: .@543bbb5 | paths: api/, web/src/, Makefile -->
