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
api/tests/test_audience.py
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
api/tests/test_audience.py:14:def fake_embed(texts):
api/tests/test_audience.py:26:def comment(user, text):
api/tests/test_audience.py:30:def test_comment_signals_find_generic_repeated_and_pod_comments():
api/tests/test_audience.py:45:def creator(**overrides):
api/tests/test_audience.py:51:def genuine_band(n=40, seed=3):
api/tests/test_audience.py:58:def test_verdict_counts_failing_families_against_the_band():
api/tests/test_audience.py:68:def test_a_small_gap_is_not_a_flag_even_outside_a_tight_band():
api/tests/test_audience.py:74:def test_genuine_share_removes_only_fake_engagement_above_the_band():
api/tests/test_audience.py:84:def test_every_signal_belongs_to_one_of_three_families():
api/tests/test_audience.py:88:def test_audience_signals_from_a_snapshot():
api/tests/test_audience.py:103:def genuine_snapshot(i, rng):
api/tests/test_audience.py:105:    def person(tag):
api/tests/test_audience.py:124:def test_redteam_catches_the_four_main_fakes_and_reports_the_smart_one():
api/tests/test_audience.py:137:def test_make_fake_leaves_the_original_alone():
api/tests/test_audience.py:144:def test_redteam_command_uses_the_latest_snapshot_of_each_creator_with_metrics(db, tmp_path, monkeypatch):
api/tests/test_audience.py:159:def test_commenter_mix_sorts_top_commenters_into_fake_brand_creator_and_person():
api/tests/test_audience.py:162:    def user(name, verified=False, bot=False):
api/tests/test_audience.py:174:def comment_by(user, text):
api/tests/test_audience.py:178:def test_face_share_is_the_share_of_covers_with_a_face():
api/tests/test_audience.py:184:def test_commenter_rings_group_creators_who_share_commenters():
api/tests/test_audience.py:190:def test_signals_without_norms_are_skipped():
api/tests/test_audience.py:196:def test_warnings_for_renamed_pages_and_unusual_patterns():
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
api/tests/test_signals.py:13:def write_kaggle(path, n=20):
api/tests/test_signals.py:23:def test_account_features_follow_kaggle_definitions():
api/tests/test_signals.py:32:def test_load_kaggle_keeps_the_six_list_fields(tmp_path):
api/tests/test_signals.py:38:def test_fake_share_scores_accounts(tmp_path):
api/tests/test_signals.py:47:def test_build_fake_model_command(tmp_path):
api/tests/test_signals.py:61:def test_csv_genres_map_onto_7_categories():
api/tests/test_signals.py:69:def make_reel(day, views, paid=False, sponsors=(), coauthors=(), caption="", pinned=False, code=None, tags=()):
api/tests/test_signals.py:74:def test_reel_metrics_on_the_last_30_unpinned_reels():
api/tests/test_signals.py:90:class FakeLLM:
api/tests/test_signals.py:94:    def json(self, prompt, schema, images=()):
api/tests/test_signals.py:100:def test_label_niche_sends_bio_and_12_captions_only():
api/tests/test_signals.py:108:class SchemaLLM:
api/tests/test_signals.py:114:    def json(self, prompt, schema, images=()):
api/tests/test_signals.py:122:def snapshot(handle, n_reels=15, followers=50_000):
api/tests/test_signals.py:130:def test_build_metrics_uses_wldd_niche_first_and_gemini_otherwise(db, monkeypatch):
api/tests/test_signals.py:162:def labelled_snapshot():
api/tests/test_signals.py:174:def test_ambiguous_reels_are_unlabelled_with_a_mention_tag_collab_or_promo_words():
api/tests/test_signals.py:182:def test_label_creator_sends_reels_accounts_and_comments_but_no_price():
api/tests/test_signals.py:197:def test_reel_metrics_count_hidden_ads_and_brand_co_authors_as_paid():
api/truerate/app.py:9:def health() -> dict:
api/truerate/cli.py:35:def main() -> None:
api/truerate/cli.py:40:def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
api/truerate/cli.py:48:def build_fake_model_cmd(
api/truerate/cli.py:59:def make_hiker(db) -> Hiker:
api/truerate/cli.py:64:def collect_cmd(handle: str) -> None:
api/truerate/cli.py:82:def collect_benchmark_cmd() -> None:
api/truerate/cli.py:105:def load_fake_model():
api/truerate/cli.py:109:def make_llm() -> Gemini:
api/truerate/cli.py:115:def build_metrics_cmd() -> None:
api/truerate/cli.py:155:def validate_cmd(out_dir: Path = REPO_ROOT / "data" / "models") -> None:
api/truerate/cli.py:176:def redteam_cmd(out_dir: Path = MODELS_DIR) -> None:
api/truerate/config.py:10:class Settings(BaseSettings):
api/truerate/config.py:22:def get_settings() -> Settings:
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
api/truerate/instagram.py:175:def fetch_covers(reels: list[dict], limit: int = 6) -> dict[str, bytes]:
api/truerate/llm.py:7:class Gemini:
api/truerate/llm.py:15:    def json(self, prompt: str, schema: dict, images: list[bytes] = ()) -> dict:
api/truerate/pricing.py:15:def round500(x: float) -> int:
api/truerate/pricing.py:19:def features(m: dict) -> list[float]:
api/truerate/pricing.py:23:def per_1k(row: dict) -> float:
api/truerate/pricing.py:28:class Core:
api/truerate/pricing.py:37:    def fit(cls, rows: list[dict]) -> "Core":
api/truerate/pricing.py:44:    def predict_logs(self, m: dict) -> tuple[float, float, list[dict]]:
api/truerate/pricing.py:55:class PriceModel:
api/truerate/pricing.py:63:    def rows(self) -> list[dict]:
api/truerate/pricing.py:67:def fit(rows: list[dict], blend: tuple[float, float, float] | None = None) -> PriceModel:
api/truerate/pricing.py:79:def collab_factor(n: int, ratio: float | None, typical: float, prior: float | None = None) -> tuple[float, float]:
api/truerate/pricing.py:86:def price(model: PriceModel, m: dict, genuine_share: float = 1.0) -> dict:
api/truerate/pricing.py:120:def band_median_price(rows: list[dict], followers: int) -> float:
api/truerate/pricing.py:125:def modash_price(rows: list[dict], m: dict) -> float:
api/truerate/pricing.py:133:def _summary(errors: list[dict], method: str) -> dict:
api/truerate/pricing.py:138:def validate(rows: list[dict]) -> dict:
api/truerate/pricing.py:143:    def errors(r: dict, m: PriceModel, others: list[dict]) -> dict:
api/truerate/signals.py:16:def _digit_ratio(text: str) -> float:
api/truerate/signals.py:20:def account_features(acc: dict) -> list[float]:
api/truerate/signals.py:33:def load_kaggle(path: Path) -> tuple[list[list[float]], list[int]]:
api/truerate/signals.py:38:def train_fake_model(X: list[list[float]], y: list[int]) -> RandomForestClassifier:
api/truerate/signals.py:42:def fake_share(model: RandomForestClassifier, accounts: list[dict]) -> float | None:
api/truerate/signals.py:62:def category_from_niche(genres: list[str]) -> str | None:
api/truerate/signals.py:71:def is_paid(reel: dict) -> bool:
api/truerate/signals.py:75:def recent_reels(snapshot: dict) -> list[dict]:
api/truerate/signals.py:80:def reel_metrics(snapshot: dict, labels: dict | None = None) -> dict:
api/truerate/signals.py:86:    def paid_reel(r):
api/truerate/signals.py:95:    def ratio(group):
api/truerate/signals.py:119:def label_niche(llm, bio: str, captions: list[str]) -> str:
api/truerate/signals.py:127:def band(followers: int) -> str:
api/truerate/signals.py:132:def _minilm():
api/truerate/signals.py:138:def minilm_embed(texts: list[str]) -> np.ndarray:
api/truerate/signals.py:150:def comment_signals(comments_by_reel: dict[str, list[dict]], embed) -> dict:
api/truerate/signals.py:172:def _cv(values: list[float]) -> float:
api/truerate/signals.py:176:def audience_signals(snapshot: dict, metrics: dict, fake_model, embed) -> dict:
api/truerate/signals.py:210:def _scale(value: float, log: bool) -> float:
api/truerate/signals.py:214:def band_norms(rows: list[dict]) -> dict:
api/truerate/signals.py:232:def verdict(signals: dict, norms: dict) -> dict:
api/truerate/signals.py:248:def genuine_share(signals: dict, norms: dict) -> float:
api/truerate/signals.py:265:def _bot(rng) -> dict:
api/truerate/signals.py:270:def make_fake(snapshot: dict, kind: str, rng) -> dict:
api/truerate/signals.py:306:def redteam(snapshots: list[dict], fake_model, embed, seed: int = 7) -> dict:
api/truerate/signals.py:311:    def signals(snap):
api/truerate/signals.py:332:def ambiguous(reel: dict) -> bool:
api/truerate/signals.py:337:def top_commenters(comments_by_reel: dict[str, list[dict]], n: int = 15) -> list[dict]:
api/truerate/signals.py:359:def label_creator(llm, snapshot: dict, images: dict[str, bytes]) -> dict:
api/truerate/signals.py:387:def commenter_mix(snapshot: dict, fake_model, labels: dict) -> dict:
api/truerate/signals.py:406:def _face_detector():
api/truerate/signals.py:419:def has_face(image: bytes) -> bool:
api/truerate/signals.py:429:def face_share(covers: dict[str, bytes], detect=has_face) -> float | None:
api/truerate/signals.py:439:def commenter_rings(commenters_by_creator: dict[str, set[str]]) -> dict[str, int]:
api/truerate/signals.py:458:def _anomaly_row(signals: dict) -> list[float]:
api/truerate/signals.py:462:def fit_anomaly(rows: list[dict]):
api/truerate/signals.py:469:def audience_warnings(signals: dict, forest) -> list[str]:
```

## TypeScript (web/src/)
```
web/src/app/layout.tsx:15:export const metadata: Metadata = {
web/src/app/layout.tsx:20:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/page.tsx:3:export default function Home() {
```

<!-- mapped: .@c8304e8 | paths: api/, web/src/ -->
