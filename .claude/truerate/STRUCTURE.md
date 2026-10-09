# truerate structure

Generated from git. Signatures only.

## Files
```
.env.example
.gitignore
Makefile
api/.python-version
api/pyproject.toml
api/tests/conftest.py
api/tests/test_app.py
api/tests/test_db.py
api/tests/test_instagram.py
api/tests/test_signals.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/cli.py
api/truerate/config.py
api/truerate/db.py
api/truerate/instagram.py
api/truerate/signals.py
web/.gitignore
web/eslint.config.mjs
web/next.config.ts
web/package.json
web/src/app/favicon.ico
web/src/app/globals.css
web/src/app/layout.tsx
web/src/app/page.tsx
web/tsconfig.json
api/tests/fixtures/*.json  (recorded HikerAPI responses, one per endpoint)
```

## Python (api/)
```
api/tests/conftest.py:8:def db():
api/tests/test_app.py:7:def test_health():
api/tests/test_app.py:11:def test_settings_read_env(monkeypatch):
api/tests/test_db.py:9:def write_csv(path, per_tier=11):
api/tests/test_db.py:18:def test_indexes(db):
api/tests/test_db.py:26:def test_import_deals_holds_out_10_per_tier_and_is_idempotent(db, tmp_path):
api/tests/test_db.py:38:def test_import_deals_command(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:36:def fixture(name):
api/tests/test_instagram.py:40:def fake_hiker(db, calls=None, status=200, private=False):
api/tests/test_instagram.py:41:    def handler(request):
api/tests/test_instagram.py:56:def test_parse_profile_and_about():
api/tests/test_instagram.py:64:def test_parse_reels_reads_counts_ads_and_collabs():
api/tests/test_instagram.py:76:def test_parse_reels_reads_tagged_accounts():
api/tests/test_instagram.py:81:def test_mark_pinned_flags_reels_older_than_a_later_one():
api/tests/test_instagram.py:87:def test_parse_comments_and_accounts():
api/tests/test_instagram.py:98:def test_hiker_caches_each_call_in_mongo(db):
api/tests/test_instagram.py:107:def test_hiker_raises_with_the_status(db):
api/tests/test_instagram.py:113:def test_collect_builds_a_snapshot(db):
api/tests/test_instagram.py:124:def test_collect_stops_at_the_profile_for_a_private_account(db):
api/tests/test_instagram.py:130:def test_collect_benchmark_skips_creators_fetched_in_the_last_day(db, monkeypatch):
api/tests/test_instagram.py:142:def test_collect_benchmark_stops_when_credit_runs_out(db, monkeypatch):
api/tests/test_signals.py:10:def write_kaggle(path, n=20):
api/tests/test_signals.py:20:def test_account_features_follow_kaggle_definitions():
api/tests/test_signals.py:29:def test_load_kaggle_keeps_the_six_list_fields(tmp_path):
api/tests/test_signals.py:35:def test_fake_share_scores_accounts(tmp_path):
api/tests/test_signals.py:43:def test_build_fake_model_command(tmp_path):
api/truerate/app.py:9:def health() -> dict:
api/truerate/cli.py:17:def main() -> None:
api/truerate/cli.py:22:def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
api/truerate/cli.py:30:def build_fake_model_cmd(
api/truerate/cli.py:41:def make_hiker(db) -> Hiker:
api/truerate/cli.py:46:def collect_cmd(handle: str) -> None:
api/truerate/cli.py:64:def collect_benchmark_cmd() -> None:
api/truerate/config.py:9:class Settings(BaseSettings):
api/truerate/config.py:21:def get_settings() -> Settings:
api/truerate/db.py:19:def _client(uri: str) -> MongoClient:
api/truerate/db.py:23:def get_db() -> Database:
api/truerate/db.py:30:def ensure_indexes(db: Database) -> None:
api/truerate/db.py:39:def import_deals(db: Database, csv_path: Path) -> dict[str, int]:
api/truerate/instagram.py:14:class HikerError(RuntimeError):
api/truerate/instagram.py:20:def _has_pic(url: str | None) -> bool:
api/truerate/instagram.py:24:def parse_profile(raw: dict) -> dict:
api/truerate/instagram.py:41:def parse_about(raw: dict) -> dict:
api/truerate/instagram.py:45:def parse_accounts(users: list[dict]) -> list[dict]:
api/truerate/instagram.py:59:def parse_reels(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:81:def mark_pinned(reels: list[dict]) -> list[dict]:
api/truerate/instagram.py:90:def parse_comments(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:97:class Hiker:
api/truerate/instagram.py:119:    def profile(self, username: str) -> dict:
api/truerate/instagram.py:122:    def about(self, pk: str) -> dict:
api/truerate/instagram.py:125:    def reels(self, pk: str, pages: int = 3) -> list[dict]:
api/truerate/instagram.py:136:    def comments(self, media_id: str) -> list[dict]:
api/truerate/instagram.py:139:    def likers(self, media_id: str, n: int = 200) -> list[dict]:
api/truerate/instagram.py:147:    def followers(self, pk: str) -> list[dict]:
api/truerate/instagram.py:150:    def suggested(self, pk: str) -> list[dict]:
api/truerate/instagram.py:154:def collect(hiker: Hiker, handle: str, comment_reels: int = 10, liker_reels: int = 3) -> dict:
api/truerate/signals.py:10:def _digit_ratio(text: str) -> float:
api/truerate/signals.py:14:def account_features(acc: dict) -> list[float]:
api/truerate/signals.py:27:def load_kaggle(path: Path) -> tuple[list[list[float]], list[int]]:
api/truerate/signals.py:32:def train_fake_model(X: list[list[float]], y: list[int]) -> RandomForestClassifier:
api/truerate/signals.py:36:def fake_share(model: RandomForestClassifier, accounts: list[dict]) -> float | None:
```

## TypeScript (web/src/)
```
web/src/app/layout.tsx:15:export const metadata: Metadata = {
web/src/app/layout.tsx:20:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/page.tsx:3:export default function Home() {
```

<!-- mapped: .@39dc687 | paths: api/, web/src/ -->
