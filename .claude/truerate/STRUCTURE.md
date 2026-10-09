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
api/tests/test_db.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/cli.py
api/truerate/config.py
api/truerate/db.py
web/.gitignore
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
api/tests/test_db.py:10:def write_csv(path, per_tier=11):
api/tests/test_db.py:20:def db():
api/tests/test_db.py:26:def test_indexes(db):
api/tests/test_db.py:34:def test_import_deals_holds_out_10_per_tier_and_is_idempotent(db, tmp_path):
api/tests/test_db.py:46:def test_import_deals_command(db, tmp_path, monkeypatch):
api/truerate/app.py:9:def health() -> dict:
api/truerate/cli.py:13:def main() -> None:
api/truerate/cli.py:18:def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
api/truerate/config.py:9:class Settings(BaseSettings):
api/truerate/config.py:21:def get_settings() -> Settings:
api/truerate/db.py:19:def _client(uri: str) -> MongoClient:
api/truerate/db.py:23:def get_db() -> Database:
api/truerate/db.py:30:def ensure_indexes(db: Database) -> None:
api/truerate/db.py:39:def import_deals(db: Database, csv_path: Path) -> dict[str, int]:
```

## TypeScript (web/src/)
```
web/src/app/layout.tsx:20:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/page.tsx:3:export default function Home() {
```

<!-- mapped: .@4644762 | paths: api/, web/src/ -->
