# truerate structure

Generated from git. Signatures only.

## Files
```
.env.example
.gitignore
Makefile
api/.python-version
api/pyproject.toml
api/scripts/seed_dev.py
api/tests/conftest.py
api/tests/test_app.py
api/tests/test_audience.py
api/tests/test_db.py
api/tests/test_instagram.py
api/tests/test_pipeline.py
api/tests/test_pricing.py
api/tests/test_signals.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/cli.py
api/truerate/config.py
api/truerate/db.py
api/truerate/instagram.py
api/truerate/llm.py
api/truerate/pipeline.py
api/truerate/pricing.py
api/truerate/signals.py
web/.gitignore
web/eslint.config.mjs
web/next.config.ts
web/package.json
web/scripts/first-screen.mjs
web/scripts/ui-check.sh
web/src/app/(app)/about/content.ts
web/src/app/(app)/about/page.tsx
web/src/app/(app)/analyses/[id]/analysis-view.tsx
web/src/app/(app)/analyses/[id]/page.tsx
web/src/app/(app)/analyses/[id]/print/page.tsx
web/src/app/(app)/analyses/[id]/print/print-view.tsx
web/src/app/(app)/batch/[id]/batch-view.tsx
web/src/app/(app)/batch/[id]/page.tsx
web/src/app/(app)/batch/page.tsx
web/src/app/(app)/layout.tsx
web/src/app/(app)/nav.tsx
web/src/app/(app)/page.tsx
web/src/app/(app)/rate-card/page.tsx
web/src/app/(app)/sign-out.tsx
web/src/app/favicon.ico
web/src/app/globals.css
web/src/app/layout.tsx
web/src/app/login/login-form.tsx
web/src/app/login/page.tsx
web/src/components/chips.tsx
web/src/components/report/audience.tsx
web/src/components/report/authenticity.tsx
web/src/components/report/decision.tsx
web/src/components/report/engagement.tsx
web/src/components/report/evidence.tsx
web/src/components/report/negotiation.tsx
web/src/components/report/placement.tsx
web/src/components/report/quote.tsx
web/src/components/report/report.tsx
web/src/components/report/waterfall.tsx
web/src/lib/api-types.ts
web/src/lib/api.ts
web/src/lib/format.ts
web/src/proxy.ts
web/tsconfig.json
api/tests/fixtures/*.json  (recorded HikerAPI responses, one per endpoint)
```

## Python (api/)
```
api/scripts/seed_dev.py:43:def snap_for(handle, seed):
api/scripts/seed_dev.py:61:def save(aid, handle, inputs, out, minutes):
api/tests/conftest.py:8:def db():
api/tests/test_app.py:7:def test_health():
api/tests/test_app.py:11:def test_settings_read_env(monkeypatch):
api/tests/test_app.py:25:def test_parse_handle_accepts_handles_and_links():
api/tests/test_app.py:33:def client(world, monkeypatch):
api/tests/test_app.py:40:def test_analysis_runs_and_reports(client):
api/tests/test_app.py:51:def test_bad_handle_is_rejected(client):
api/tests/test_app.py:55:def test_out_of_scope_and_failures_are_recorded(client, world, monkeypatch):
api/tests/test_app.py:62:    def broken(handle):
api/tests/test_app.py:70:def _with_collect(d, fn):
api/tests/test_app.py:75:def test_meta_lists_categories_and_coverage(client, tmp_path, monkeypatch):
api/tests/test_app.py:84:def test_quote_check_endpoint(client):
api/tests/test_app.py:92:def test_batch_runs_every_handle_and_ranks_by_cost(client):
api/tests/test_app.py:102:def test_batch_rejects_bad_or_too_many_handles(client):
api/tests/test_app.py:107:def test_rate_card_endpoint(client, tmp_path, monkeypatch):
api/tests/test_app.py:120:def test_batch_puts_avoid_after_everything_else(client, world, monkeypatch):
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
api/tests/test_pipeline.py:15:class TopicLLM:
api/tests/test_pipeline.py:21:    def json(self, prompt, schema, images=()):
api/tests/test_pipeline.py:29:def target_snapshot(handle="newcreator", seed=99):
api/tests/test_pipeline.py:41:def world(db):
api/tests/test_pipeline.py:52:def deps(db, snap, llm=None, face=True):
api/tests/test_pipeline.py:58:def test_a_genuine_creator_gets_go_with_a_full_report(world):
api/tests/test_pipeline.py:80:def test_bot_likers_stop_a_go_and_say_why(world):
api/tests/test_pipeline.py:88:def test_a_quote_above_the_range_means_negotiate(world):
api/tests/test_pipeline.py:94:def test_a_product_outside_the_creators_niche_means_avoid(world):
api/tests/test_pipeline.py:100:def test_private_and_faceless_pages_are_out_of_scope(world):
api/tests/test_pipeline.py:109:def test_quote_check_places_the_quote_and_counters(world):
api/tests/test_pricing.py:14:def synthetic_rows(n=90, seed=1):
api/tests/test_pricing.py:32:def test_bands_and_rounding():
api/tests/test_pricing.py:37:def test_collab_factor_shrinks_few_ads_toward_the_typical_drop():
api/tests/test_pricing.py:45:def test_baselines():
api/tests/test_pricing.py:53:def test_price_has_a_range_waterfall_comparables_and_delivery():
api/tests/test_pricing.py:67:def test_validate_beats_both_baselines_on_synthetic_deals():
api/tests/test_pricing.py:79:def test_range_covers_most_held_out_prices():
api/tests/test_pricing.py:85:def test_validate_command_saves_model_and_report(db, tmp_path, monkeypatch):
api/tests/test_pricing.py:98:def test_rate_card_per_category():
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
api/truerate/app.py:29:def submit(fn) -> None:
api/truerate/app.py:36:class Profile(BaseModel):
api/truerate/app.py:45:class Decision(BaseModel):
api/truerate/app.py:50:class WaterfallStep(BaseModel):
api/truerate/app.py:55:class Comparable(BaseModel):
api/truerate/app.py:64:class Delivery(BaseModel):
api/truerate/app.py:72:class Price(BaseModel):
api/truerate/app.py:84:class Flag(BaseModel):
api/truerate/app.py:92:class Language(BaseModel):
api/truerate/app.py:97:class Mix(BaseModel):
api/truerate/app.py:106:class Audience(BaseModel):
api/truerate/app.py:116:class Engagement(BaseModel):
api/truerate/app.py:123:class ReelPoint(BaseModel):
api/truerate/app.py:133:class FollowerPoint(BaseModel):
api/truerate/app.py:138:class Ratio(BaseModel):
api/truerate/app.py:143:class PaidRatio(Ratio):
api/truerate/app.py:147:class Ad(BaseModel):
api/truerate/app.py:155:class Placement(BaseModel):
api/truerate/app.py:167:class Niche(BaseModel):
api/truerate/app.py:175:class Competitor(BaseModel):
api/truerate/app.py:181:class Cheaper(BaseModel):
api/truerate/app.py:188:class Negotiation(BaseModel):
api/truerate/app.py:195:class Report(BaseModel):
api/truerate/app.py:215:class Inputs(BaseModel):
api/truerate/app.py:221:class AnalysisRequest(Inputs):
api/truerate/app.py:225:class Created(BaseModel):
api/truerate/app.py:229:class Analysis(BaseModel):
api/truerate/app.py:243:class AnalysisSummary(BaseModel):
api/truerate/app.py:253:class QuoteRequest(BaseModel):
api/truerate/app.py:257:class QuoteCheck(BaseModel):
api/truerate/app.py:265:class BatchRequest(Inputs):
api/truerate/app.py:269:class BatchRow(BaseModel):
api/truerate/app.py:283:class Batch(BaseModel):
api/truerate/app.py:292:class Per1k(BaseModel):
api/truerate/app.py:298:class CategoryRate(BaseModel):
api/truerate/app.py:306:class RateCard(BaseModel):
api/truerate/app.py:310:class Meta(BaseModel):
api/truerate/app.py:315:class ModelReport(BaseModel):
api/truerate/app.py:325:def parse_handle(text: str) -> str | None:
api/truerate/app.py:331:def _models() -> tuple:
api/truerate/app.py:335:def make_deps(db) -> Deps:
api/truerate/app.py:343:def _run(analysis_id: str, handle: str, inputs: dict) -> None:
api/truerate/app.py:346:    def step(i: int) -> None:
api/truerate/app.py:357:def _read_json(name: str) -> dict | None:
api/truerate/app.py:366:def health() -> dict:
api/truerate/app.py:371:def create_analysis(req: AnalysisRequest) -> Created:
api/truerate/app.py:380:def _start(db, handle: str, inputs: dict, batch_id: str | None = None) -> str:
api/truerate/app.py:389:def create_batch(req: BatchRequest) -> Created:
api/truerate/app.py:408:def get_batch(batch_id: str) -> Batch:
api/truerate/app.py:427:def get_rate_card() -> RateCard:
api/truerate/app.py:435:def list_analyses() -> list[AnalysisSummary]:
api/truerate/app.py:445:def get_analysis(analysis_id: str) -> Analysis:
api/truerate/app.py:453:def quote_check(analysis_id: str, req: QuoteRequest) -> QuoteCheck:
api/truerate/app.py:463:def meta() -> Meta:
api/truerate/app.py:469:def model_report() -> ModelReport:
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
api/truerate/config.py:14:class Settings(BaseSettings):
api/truerate/config.py:26:def get_settings() -> Settings:
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
api/truerate/pipeline.py:40:class Deps:
api/truerate/pipeline.py:51:def _flag_text(f: dict, s: dict) -> str:
api/truerate/pipeline.py:66:def _brand(reel: dict) -> str | None:
api/truerate/pipeline.py:71:def _days_ago(iso: str) -> int:
api/truerate/pipeline.py:75:def analyze(handle: str, inputs: dict, deps: Deps, step: Callable[[int], None] = lambda i: None) -> dict:
api/truerate/pipeline.py:116:    def kind(r):
api/truerate/pipeline.py:188:def _decide(v, flags, p, inputs, metrics, typical, fit, fit_share, competitor) -> dict:
api/truerate/pipeline.py:215:def _negotiation(p: dict, flags: list[dict], metrics: dict, category: str) -> dict:
api/truerate/pipeline.py:224:def check_quote(r: dict, quote: int) -> dict:
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
api/truerate/pricing.py:175:def rate_card(model: PriceModel) -> list[dict]:
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
web/src/app/(app)/about/content.ts:3:export const FLOW = [
web/src/app/(app)/about/content.ts:12:export const SIGNALS: [string, string, string][] = [
web/src/app/(app)/about/content.ts:31:export const FAKE_KINDS: Record<string, [string, string]> = {
web/src/app/(app)/about/content.ts:40:export const OTHER_PAGES: [string, string][] = [
web/src/app/(app)/about/content.ts:47:export const LIMITS = [
web/src/app/(app)/about/page.tsx:16:export default function AboutPage() {
web/src/app/(app)/analyses/[id]/analysis-view.tsx:11:export default function AnalysisView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/analyses/[id]/page.tsx:6:export default function AnalysisPage({ params }: PageProps<"/analyses/[id]">) {
web/src/app/(app)/analyses/[id]/print/page.tsx:5:export default function PrintPage({ params }: PageProps<"/analyses/[id]/print">) {
web/src/app/(app)/analyses/[id]/print/print-view.tsx:9:export default function PrintView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/batch/[id]/batch-view.tsx:16:export default function BatchView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/batch/[id]/page.tsx:5:export default function BatchResultPage({ params }: PageProps<"/batch/[id]">) {
web/src/app/(app)/batch/page.tsx:8:export default function BatchPage() {
web/src/app/(app)/layout.tsx:7:export default function AppLayout({ children }: LayoutProps<"/">) {
web/src/app/(app)/nav.tsx:18:export function NavLinks({ path }: { path: string | null }) {
web/src/app/(app)/nav.tsx:34:export default function Nav() {
web/src/app/(app)/page.tsx:11:export default function AnalyzePage() {
web/src/app/(app)/rate-card/page.tsx:8:export default function RateCardPage() {
web/src/app/(app)/sign-out.tsx:7:export default function SignOut() {
web/src/app/layout.tsx:12:export const metadata: Metadata = {
web/src/app/layout.tsx:17:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/login/login-form.tsx:8:export default function LoginForm() {
web/src/app/login/page.tsx:3:export default function LoginPage() {
web/src/components/chips.tsx:7:export function CallChip({ call, large = false }: { call: string; large?: boolean }) {
web/src/components/chips.tsx:15:export const VERDICTS = ["Real audience", "Some fake activity", "Mostly fake"] as const;
web/src/components/chips.tsx:16:export const VERDICT_COLOR: Record<string, string> = {
web/src/components/report/audience.tsx:4:export default function Audience({ r }: { r: Report }) {
web/src/components/report/authenticity.tsx:27:export default function Authenticity({ r }: { r: Report }) {
web/src/components/report/decision.tsx:7:export default function Decision({ r }: { r: Report }) {
web/src/components/report/engagement.tsx:6:export default function Engagement({ r }: { r: Report }) {
web/src/components/report/evidence.tsx:9:export default function Evidence({ r }: { r: Report }) {
web/src/components/report/negotiation.tsx:9:export default function Negotiation({ r }: { r: Report }) {
web/src/components/report/placement.tsx:16:export default function Placement({ r }: { r: Report }) {
web/src/components/report/quote.tsx:10:export default function QuoteChecker({ id, initial }: { id: string; initial: number | null }) {
web/src/components/report/report.tsx:17:export default function ReportView({ id, report: r, inputs }: { id: string; report: Report; inputs: Analysis["inputs"] }) {
web/src/components/report/waterfall.tsx:23:export default function Waterfall({ r }: { r: Report }) {
web/src/lib/api-types.ts:6:export interface paths {
web/src/lib/api-types.ts:162:export type webhooks = Record<string, never>;
web/src/lib/api-types.ts:163:export interface components {
web/src/lib/api-types.ts:686:export type $defs = Record<string, never>;
web/src/lib/api-types.ts:687:export interface operations {
web/src/lib/api.ts:4:export type Analysis = Schemas["Analysis"];
web/src/lib/api.ts:5:export type AnalysisRequest = Schemas["AnalysisRequest"];
web/src/lib/api.ts:6:export type AnalysisSummary = Schemas["AnalysisSummary"];
web/src/lib/api.ts:7:export type Report = Schemas["Report"];
web/src/lib/api.ts:8:export type Meta = Schemas["Meta"];
web/src/lib/api.ts:9:export type QuoteCheck = Schemas["QuoteCheck"];
web/src/lib/api.ts:10:export type Batch = Schemas["Batch"];
web/src/lib/api.ts:11:export type BatchRequest = Schemas["BatchRequest"];
web/src/lib/api.ts:12:export type RateCard = Schemas["RateCard"];
web/src/lib/api.ts:13:export type ModelReport = Schemas["ModelReport"];
web/src/lib/api.ts:26:export const api = {
web/src/lib/format.ts:3:export function inr(n: number): string {
web/src/lib/format.ts:11:export function compact(n: number): string {
web/src/lib/format.ts:18:export function pct(x: number, digits = 0): string {
web/src/lib/format.ts:22:export function daysAgo(iso: string): string {
web/src/lib/format.ts:28:export const SESSION_COOKIE = "truerate_session";
web/src/proxy.ts:4:export function proxy(request: NextRequest) {
web/src/proxy.ts:12:export const config = {
```

<!-- mapped: .@e5ad381 | paths: api/, web/src/ -->
