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
api/tests/test_pricing.py
api/tests/test_signals.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/cli.py
api/truerate/config.py
api/truerate/db.py
api/truerate/instagram.py
api/truerate/llm.py
api/truerate/pricing.py
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
api/tests/test_pricing.py:14:def synthetic_rows(n=90, seed=1):
api/tests/test_pricing.py:32:def test_bands_and_rounding():
api/tests/test_pricing.py:37:def test_collab_factor_shrinks_few_ads_toward_the_typical_drop():
api/tests/test_pricing.py:45:def test_baselines():
api/tests/test_pricing.py:53:def test_price_has_a_range_waterfall_comparables_and_delivery():
api/tests/test_pricing.py:67:def test_validate_beats_both_baselines_on_synthetic_deals():
api/tests/test_pricing.py:77:def test_range_covers_most_held_out_prices():
api/tests/test_pricing.py:83:def test_validate_command_saves_model_and_report(db, tmp_path, monkeypatch):
api/tests/test_signals.py:12:def write_kaggle(path, n=20):
api/tests/test_signals.py:22:def test_account_features_follow_kaggle_definitions():
api/tests/test_signals.py:31:def test_load_kaggle_keeps_the_six_list_fields(tmp_path):
api/tests/test_signals.py:37:def test_fake_share_scores_accounts(tmp_path):
api/tests/test_signals.py:45:def test_build_fake_model_command(tmp_path):
api/tests/test_signals.py:59:def test_csv_genres_map_onto_7_categories():
api/tests/test_signals.py:67:def make_reel(day, views, paid=False, sponsors=(), coauthors=(), caption="", pinned=False):
api/tests/test_signals.py:72:def test_reel_metrics_on_the_last_30_unpinned_reels():
api/tests/test_signals.py:88:class FakeLLM:
api/tests/test_signals.py:92:    def json(self, prompt, schema):
api/tests/test_signals.py:97:def test_label_niche_sends_bio_and_12_captions_only():
api/tests/test_signals.py:105:def snapshot(handle, n_reels=15, followers=50_000):
api/tests/test_signals.py:110:def test_build_metrics_uses_wldd_niche_first_and_gemini_otherwise(db, monkeypatch):
api/truerate/app.py:9:def health() -> dict:
api/truerate/cli.py:21:def main() -> None:
api/truerate/cli.py:26:def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
api/truerate/cli.py:34:def build_fake_model_cmd(
api/truerate/cli.py:45:def make_hiker(db) -> Hiker:
api/truerate/cli.py:50:def collect_cmd(handle: str) -> None:
api/truerate/cli.py:68:def collect_benchmark_cmd() -> None:
api/truerate/cli.py:91:def make_llm() -> Gemini:
api/truerate/cli.py:97:def build_metrics_cmd() -> None:
api/truerate/cli.py:124:def validate_cmd(out_dir: Path = REPO_ROOT / "data" / "models") -> None:
api/truerate/config.py:9:class Settings(BaseSettings):
api/truerate/config.py:21:def get_settings() -> Settings:
api/truerate/db.py:19:def _client(uri: str) -> MongoClient:
api/truerate/db.py:23:def get_db() -> Database:
api/truerate/db.py:30:def ensure_indexes(db: Database) -> None:
api/truerate/db.py:39:def import_deals(db: Database, csv_path: Path) -> dict[str, int]:
api/truerate/db.py:65:def training_rows(db: Database) -> list[dict]:
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
api/truerate/llm.py:7:class Gemini:
api/truerate/llm.py:15:    def json(self, prompt: str, schema: dict) -> dict:
api/truerate/pricing.py:15:def band(followers: int) -> str:
api/truerate/pricing.py:19:def round500(x: float) -> int:
api/truerate/pricing.py:23:def features(m: dict) -> list[float]:
api/truerate/pricing.py:27:def per_1k(row: dict) -> float:
api/truerate/pricing.py:32:class Core:
api/truerate/pricing.py:41:    def fit(cls, rows: list[dict]) -> "Core":
api/truerate/pricing.py:48:    def predict_logs(self, m: dict) -> tuple[float, float, list[dict]]:
api/truerate/pricing.py:59:class PriceModel:
api/truerate/pricing.py:67:    def rows(self) -> list[dict]:
api/truerate/pricing.py:71:def fit(rows: list[dict], blend: tuple[float, float, float] | None = None) -> PriceModel:
api/truerate/pricing.py:83:def collab_factor(n: int, ratio: float | None, typical: float, prior: float | None = None) -> tuple[float, float]:
api/truerate/pricing.py:90:def price(model: PriceModel, m: dict, genuine_share: float = 1.0) -> dict:
api/truerate/pricing.py:124:def band_median_price(rows: list[dict], followers: int) -> float:
api/truerate/pricing.py:129:def modash_price(rows: list[dict], m: dict) -> float:
api/truerate/pricing.py:137:def _summary(errors: list[dict], method: str) -> dict:
api/truerate/pricing.py:142:def validate(rows: list[dict]) -> dict:
api/truerate/pricing.py:147:    def errors(r: dict, m: PriceModel, others: list[dict]) -> dict:
api/truerate/signals.py:13:def _digit_ratio(text: str) -> float:
api/truerate/signals.py:17:def account_features(acc: dict) -> list[float]:
api/truerate/signals.py:30:def load_kaggle(path: Path) -> tuple[list[list[float]], list[int]]:
api/truerate/signals.py:35:def train_fake_model(X: list[list[float]], y: list[int]) -> RandomForestClassifier:
api/truerate/signals.py:39:def fake_share(model: RandomForestClassifier, accounts: list[dict]) -> float | None:
api/truerate/signals.py:59:def category_from_niche(genres: list[str]) -> str | None:
api/truerate/signals.py:68:def is_paid(reel: dict) -> bool:
api/truerate/signals.py:72:def reel_metrics(snapshot: dict) -> dict:
api/truerate/signals.py:80:    def ratio(group):
api/truerate/signals.py:104:def label_niche(llm, bio: str, captions: list[str]) -> str:
```

## TypeScript (web/src/)
```
web/src/app/layout.tsx:15:export const metadata: Metadata = {
web/src/app/layout.tsx:20:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/page.tsx:3:export default function Home() {
```

<!-- mapped: .@2e55ffc | paths: api/, web/src/ -->
