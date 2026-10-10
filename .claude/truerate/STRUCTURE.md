# truerate structure

Generated from git. Signatures only.

## Files
```
.env.example
.gitignore
Makefile
api/.python-version
api/pyproject.toml
api/scripts/make_deck.py
api/scripts/seed_dev.py
api/tests/conftest.py
api/tests/test_app.py
api/tests/test_audience.py
api/tests/test_audio.py
api/tests/test_db.py
api/tests/test_deck.py
api/tests/test_experiment.py
api/tests/test_instagram.py
api/tests/test_llm.py
api/tests/test_pipeline.py
api/tests/test_pricing.py
api/tests/test_signals.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/audio.py
api/truerate/cli.py
api/truerate/config.py
api/truerate/db.py
api/truerate/experiment.py
api/truerate/experiment_plots.py
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
web/scripts/report-shot.mjs
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
web/src/components/product-options.tsx
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
api/scripts/make_deck.py:40:def pct(x) -> str:
api/scripts/make_deck.py:44:class Deck:
api/scripts/make_deck.py:49:    def slide(self, title: str, note: str = ""):
api/scripts/make_deck.py:58:    def text(self, s, x, y, w, h, lines, gap=6):
api/scripts/make_deck.py:71:    def table(self, s, x, y, widths, rows, size=13, bold_row=None, colors=None):
api/scripts/make_deck.py:93:def _plain_style(tbl):
api/scripts/make_deck.py:101:def _bottom_rule(cell):
api/scripts/make_deck.py:109:def _log_axes(chart):
api/scripts/make_deck.py:120:def build_deck(report: dict, rt: dict, screenshot: Path | None, out: Path) -> None:
api/scripts/seed_dev.py:43:def snap_for(handle, seed):
api/scripts/seed_dev.py:61:def save(aid, handle, inputs, out, minutes):
api/tests/conftest.py:8:def db():
api/tests/test_app.py:7:def test_health():
api/tests/test_app.py:11:def test_settings_read_env(monkeypatch):
api/tests/test_app.py:25:def test_parse_handle_accepts_handles_and_links():
api/tests/test_app.py:33:def client(world, monkeypatch):
api/tests/test_app.py:40:def test_analysis_runs_and_reports(client):
api/tests/test_app.py:52:def test_bad_handle_is_rejected(client):
api/tests/test_app.py:56:def test_out_of_scope_and_failures_are_recorded(client, world, monkeypatch):
api/tests/test_app.py:63:    def broken(handle):
api/tests/test_app.py:71:def _with_collect(d, fn):
api/tests/test_app.py:76:def test_meta_lists_categories_and_coverage(client, tmp_path, monkeypatch):
api/tests/test_app.py:89:def test_quote_check_endpoint(client):
api/tests/test_app.py:97:def test_batch_runs_every_handle_and_ranks_by_cost(client):
api/tests/test_app.py:107:def test_batch_rejects_bad_or_too_many_handles(client):
api/tests/test_app.py:112:def test_rate_card_endpoint(client, tmp_path, monkeypatch):
api/tests/test_app.py:126:def test_batch_puts_avoid_after_everything_else(client, world, monkeypatch):
api/tests/test_app.py:137:def test_removing_an_analysis_hides_it_from_recent_but_keeps_its_report(client):
api/tests/test_app.py:146:def test_analyses_left_running_by_a_stopped_server_are_marked_failed(world):
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
api/tests/test_audio.py:12:def make_mp4(seconds: float, rate: int = 44_100) -> bytes:
api/tests/test_audio.py:30:def wav_info(data: bytes) -> tuple[int, int, float]:
api/tests/test_audio.py:35:def test_audio_from_video_gives_16khz_mono_wav():
api/tests/test_audio.py:40:def test_audio_from_video_keeps_at_most_90_seconds():
api/tests/test_audio.py:44:def test_spoken_candidates_are_the_newest_reels_the_rules_dont_already_call_ads():
api/tests/test_audio.py:49:def test_label_spoken_keeps_only_spoken_ads_with_brand_and_quote():
api/tests/test_db.py:9:def write_csv(path, per_tier=11):
api/tests/test_db.py:18:def test_indexes(db):
api/tests/test_db.py:25:def test_import_deals_holds_out_10_per_tier_and_is_idempotent(db, tmp_path):
api/tests/test_db.py:37:def test_import_deals_command(db, tmp_path, monkeypatch):
api/tests/test_deck.py:19:def test_deck_has_at_most_12_slides_with_the_real_numbers_and_no_handles(tmp_path):
api/tests/test_experiment.py:16:def test_extra_features_read_account_age_reel_length_posting_rate_and_contact():
api/tests/test_experiment.py:30:def test_ranges_hold_close_to_their_stated_share_of_unseen_prices():
api/tests/test_experiment.py:39:def test_ranges_by_follower_band_are_narrower_where_similar_deals_agree():
api/tests/test_experiment.py:49:def _sets(seed=7):
api/tests/test_experiment.py:55:def test_the_pick_never_looks_at_held_out_or_fresh_prices():
api/tests/test_experiment.py:69:def test_fresh_rows_rebuild_the_features_a_stored_analysis_was_priced_from(world):
api/tests/test_experiment.py:79:def test_learning_curve_and_importance_have_one_value_per_size_and_feature():
api/tests/test_experiment.py:87:def test_tabpfn_uses_the_v2_weights_whose_license_allows_commercial_use():
api/tests/test_experiment.py:96:def test_fresh_deals_are_scored_by_the_model_exactly_as_served():
api/tests/test_instagram.py:39:def fixture(name):
api/tests/test_instagram.py:43:def fake_hiker(store, calls=None, status=200, private=False, missing=(), disabled=()):
api/tests/test_instagram.py:44:    def handler(request):
api/tests/test_instagram.py:63:def test_parse_profile_and_about():
api/tests/test_instagram.py:71:def test_parse_reels_reads_counts_ads_and_collabs():
api/tests/test_instagram.py:83:def test_parse_reels_reads_tagged_accounts():
api/tests/test_instagram.py:88:def test_mark_pinned_flags_reels_older_than_a_later_one():
api/tests/test_instagram.py:94:def test_parse_comments_and_accounts():
api/tests/test_instagram.py:105:def test_hiker_saves_each_raw_response_once_on_disk(tmp_path):
api/tests/test_instagram.py:116:def test_hiker_raises_with_the_status_and_saves_nothing(tmp_path):
api/tests/test_instagram.py:123:def test_collect_builds_a_snapshot(tmp_path):
api/tests/test_instagram.py:134:def test_collect_stops_at_the_profile_for_a_private_account(tmp_path):
api/tests/test_instagram.py:140:def test_collect_benchmark_skips_creators_fetched_in_the_last_day(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:152:def test_collect_benchmark_stops_when_credit_runs_out(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:161:def test_collect_benchmark_runs_creators_in_parallel_and_survives_one_failure(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:184:def test_collect_treats_hidden_lists_as_empty(tmp_path):
api/tests/test_instagram.py:191:def test_collect_survives_a_missing_about(tmp_path):
api/tests/test_instagram.py:196:def test_collect_treats_disabled_comments_as_empty(tmp_path):
api/tests/test_instagram.py:201:def test_parse_reels_marks_reposts_with_the_original_author():
api/tests/test_instagram.py:207:def test_parse_tagged_posts_by_other_accounts():
api/tests/test_instagram.py:213:def test_collect_keeps_tagged_posts_by_others_only(tmp_path):
api/tests/test_instagram.py:218:def test_collect_benchmark_fresh_hours_zero_collects_again(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:227:def test_collect_fetches_the_per_reel_lists_in_parallel_with_the_same_result(tmp_path):
api/tests/test_instagram.py:233:def test_comments_start_while_older_reel_pages_are_still_loading(tmp_path):
api/tests/test_instagram.py:242:    def handler(request):
api/tests/test_llm.py:7:class Reply:
api/tests/test_llm.py:11:def flaky(failures):
api/tests/test_llm.py:15:    def generate_content(**kwargs):
api/tests/test_llm.py:24:def test_a_dropped_gemini_connection_is_retried(monkeypatch):
api/tests/test_llm.py:31:def test_gemini_gives_up_after_three_dropped_connections(monkeypatch):
api/tests/test_llm.py:40:def test_gemini_asks_for_low_thinking(monkeypatch):
api/tests/test_pipeline.py:17:class TopicLLM:
api/tests/test_pipeline.py:23:    def json(self, prompt, schema, images=(), audio=()):
api/tests/test_pipeline.py:37:def target_snapshot(handle="newcreator", seed=99):
api/tests/test_pipeline.py:49:def world(db):
api/tests/test_pipeline.py:60:def deps(db, snap, llm=None, face=True, audio=False):
api/tests/test_pipeline.py:66:def test_a_genuine_creator_gets_go_with_a_full_report(world):
api/tests/test_pipeline.py:88:def test_bot_likers_stop_a_go_and_say_why(world):
api/tests/test_pipeline.py:96:def test_a_quote_above_the_range_means_negotiate(world):
api/tests/test_pipeline.py:102:def test_a_product_outside_the_creators_niche_means_avoid(world):
api/tests/test_pipeline.py:108:def test_private_and_faceless_pages_are_out_of_scope(world):
api/tests/test_pipeline.py:117:def test_quote_check_places_the_quote_and_counters(world):
api/tests/test_pipeline.py:129:def test_a_brand_that_tagged_the_creator_recently_is_a_competitor(world):
api/tests/test_pipeline.py:140:def test_money_uses_indian_grouping_and_days_read_naturally():
api/tests/test_pipeline.py:145:def test_reasons_and_lines_use_indian_grouping(world):
api/tests/test_pipeline.py:152:def test_a_handle_instagram_doesnt_know_reads_as_a_plain_sentence(world):
api/tests/test_pipeline.py:153:    def missing(handle):
api/tests/test_pipeline.py:162:def test_a_spoken_ad_makes_the_reel_paid_and_shows_the_quote(world):
api/tests/test_pipeline.py:171:def test_the_creators_own_handle_is_never_the_brand(world):
api/tests/test_pipeline.py:180:def test_a_specific_product_is_matched_through_its_pricing_category(world):
api/tests/test_pipeline.py:188:def test_a_competitor_for_a_specific_product_is_named_by_the_category_it_was_matched_in(world):
api/tests/test_pipeline.py:198:def test_a_creator_wldd_has_booked_is_never_turned_away_by_the_cover_check(world):
api/tests/test_pricing.py:16:def synthetic_rows(n=90, seed=1):
api/tests/test_pricing.py:34:def test_bands_and_rounding():
api/tests/test_pricing.py:39:def test_collab_factor_shrinks_few_ads_toward_the_typical_drop():
api/tests/test_pricing.py:47:def test_collab_factor_never_raises_a_price_and_never_more_than_halves_it():
api/tests/test_pricing.py:54:def test_baselines():
api/tests/test_pricing.py:62:def test_price_has_a_range_waterfall_comparables_and_delivery():
api/tests/test_pricing.py:77:def test_validate_beats_both_baselines_on_synthetic_deals():
api/tests/test_pricing.py:89:def test_range_covers_most_held_out_prices():
api/tests/test_pricing.py:95:def test_validate_command_saves_model_and_report(db, tmp_path, monkeypatch):
api/tests/test_pricing.py:108:def test_rate_card_per_category():
api/tests/test_pricing.py:116:def test_a_creator_bigger_than_any_wldd_deal_gets_a_note():
api/tests/test_pricing.py:124:def test_rate_card_leaves_out_categories_with_fewer_than_3_deals():
api/tests/test_pricing.py:132:def test_every_price_carries_the_published_asking_range_for_its_size():
api/tests/test_pricing.py:139:def test_beyond_wldds_largest_creator_the_range_widens_and_reaches_the_market():
api/tests/test_pricing.py:152:def test_below_wldds_smallest_creator_only_the_bottom_widens():
api/tests/test_pricing.py:161:def test_the_range_comes_from_mapie_cross_conformal_at_80_percent():
api/tests/test_signals.py:13:def write_kaggle(path, n=20):
api/tests/test_signals.py:23:def test_account_features_follow_kaggle_definitions():
api/tests/test_signals.py:32:def test_load_kaggle_keeps_the_six_list_fields(tmp_path):
api/tests/test_signals.py:38:def test_fake_share_scores_accounts(tmp_path):
api/tests/test_signals.py:47:def test_build_fake_model_command(tmp_path):
api/tests/test_signals.py:61:def test_csv_genres_map_onto_7_categories():
api/tests/test_signals.py:69:def make_reel(day, views, paid=False, sponsors=(), coauthors=(), caption="", pinned=False, code=None, tags=(), repost_of=None):
api/tests/test_signals.py:74:def test_reel_metrics_on_the_last_30_unpinned_reels():
api/tests/test_signals.py:90:class FakeLLM:
api/tests/test_signals.py:94:    def json(self, prompt, schema, images=(), audio=()):
api/tests/test_signals.py:101:def test_label_niche_sends_bio_and_12_captions_only():
api/tests/test_signals.py:109:class SchemaLLM:
api/tests/test_signals.py:115:    def json(self, prompt, schema, images=(), audio=()):
api/tests/test_signals.py:123:def snapshot(handle, n_reels=15, followers=50_000):
api/tests/test_signals.py:131:def test_build_metrics_uses_wldd_niche_first_and_gemini_otherwise(db, monkeypatch):
api/tests/test_signals.py:163:def labelled_snapshot():
api/tests/test_signals.py:177:def test_ambiguous_reels_are_unlabelled_with_a_mention_tag_collab_or_promo_words():
api/tests/test_signals.py:185:def test_label_creator_sends_reels_accounts_and_comments_but_no_price():
api/tests/test_signals.py:201:def test_reel_metrics_count_hidden_ads_and_brand_co_authors_as_paid():
api/tests/test_signals.py:209:def test_build_metrics_skips_a_creator_whose_gemini_call_fails(db, monkeypatch):
api/tests/test_signals.py:230:def test_reel_metrics_falls_back_to_all_reels_when_none_are_own():
api/tests/test_signals.py:236:def test_build_metrics_keeps_gemini_labels_when_a_later_step_fails(db, monkeypatch):
api/tests/test_signals.py:242:    def flaky_metrics(snap, labels=None):
api/tests/test_signals.py:263:def test_label_creator_sends_only_the_8_newest_tagged_posts():
api/tests/test_signals.py:274:def test_hidden_like_counts_are_not_zero_likes():
api/truerate/app.py:25:async def lifespan(app: FastAPI):
api/truerate/app.py:38:def fail_interrupted(db) -> None:
api/truerate/app.py:43:def submit(fn) -> None:
api/truerate/app.py:50:class Profile(BaseModel):
api/truerate/app.py:59:class Decision(BaseModel):
api/truerate/app.py:64:class WaterfallStep(BaseModel):
api/truerate/app.py:69:class Comparable(BaseModel):
api/truerate/app.py:78:class Delivery(BaseModel):
api/truerate/app.py:86:class MarketReference(BaseModel):
api/truerate/app.py:93:class Price(BaseModel):
api/truerate/app.py:109:class Flag(BaseModel):
api/truerate/app.py:117:class Language(BaseModel):
api/truerate/app.py:122:class Mix(BaseModel):
api/truerate/app.py:131:class Audience(BaseModel):
api/truerate/app.py:141:class Engagement(BaseModel):
api/truerate/app.py:148:class ReelPoint(BaseModel):
api/truerate/app.py:158:class FollowerPoint(BaseModel):
api/truerate/app.py:163:class Ratio(BaseModel):
api/truerate/app.py:168:class PaidRatio(Ratio):
api/truerate/app.py:172:class Ad(BaseModel):
api/truerate/app.py:181:class BrandTag(BaseModel):
api/truerate/app.py:188:class Placement(BaseModel):
api/truerate/app.py:202:class Niche(BaseModel):
api/truerate/app.py:210:class Competitor(BaseModel):
api/truerate/app.py:217:class Cheaper(BaseModel):
api/truerate/app.py:224:class Negotiation(BaseModel):
api/truerate/app.py:231:class Report(BaseModel):
api/truerate/app.py:251:class Inputs(BaseModel):
api/truerate/app.py:257:class AnalysisRequest(Inputs):
api/truerate/app.py:261:class Created(BaseModel):
api/truerate/app.py:265:class Analysis(BaseModel):
api/truerate/app.py:279:class AnalysisSummary(BaseModel):
api/truerate/app.py:291:class QuoteRequest(BaseModel):
api/truerate/app.py:295:class QuoteCheck(BaseModel):
api/truerate/app.py:303:class BatchRequest(Inputs):
api/truerate/app.py:307:class BatchRow(BaseModel):
api/truerate/app.py:321:class Batch(BaseModel):
api/truerate/app.py:330:class Per1k(BaseModel):
api/truerate/app.py:336:class CategoryRate(BaseModel):
api/truerate/app.py:344:class ThinCategory(BaseModel):
api/truerate/app.py:349:class RateCard(BaseModel):
api/truerate/app.py:354:class Product(BaseModel):
api/truerate/app.py:359:class Meta(BaseModel):
api/truerate/app.py:365:class ModelReport(BaseModel):
api/truerate/app.py:375:def parse_handle(text: str) -> str | None:
api/truerate/app.py:381:def _models() -> tuple:
api/truerate/app.py:385:def _warm() -> None:
api/truerate/app.py:397:def make_deps(db) -> Deps:
api/truerate/app.py:405:def _run(analysis_id: str, handle: str, inputs: dict) -> None:
api/truerate/app.py:408:    def step(i: int) -> None:
api/truerate/app.py:419:def _read_json(name: str) -> dict | None:
api/truerate/app.py:428:def health() -> dict:
api/truerate/app.py:433:def create_analysis(req: AnalysisRequest) -> Created:
api/truerate/app.py:442:def _start(db, handle: str, inputs: dict, batch_id: str | None = None) -> str:
api/truerate/app.py:451:def create_batch(req: BatchRequest) -> Created:
api/truerate/app.py:470:def get_batch(batch_id: str) -> Batch:
api/truerate/app.py:489:def get_rate_card() -> RateCard:
api/truerate/app.py:498:def list_analyses() -> list[AnalysisSummary]:
api/truerate/app.py:508:def get_analysis(analysis_id: str) -> Analysis:
api/truerate/app.py:516:def hide_analysis(analysis_id: str) -> None:
api/truerate/app.py:523:def quote_check(analysis_id: str, req: QuoteRequest) -> QuoteCheck:
api/truerate/app.py:533:def meta() -> Meta:
api/truerate/app.py:539:def model_report() -> ModelReport:
api/truerate/audio.py:19:def audio_from_video(data: bytes) -> bytes:
api/truerate/audio.py:42:def fetch_audio(reels: list[dict]) -> dict[str, bytes]:
api/truerate/audio.py:45:    def one(reel):
api/truerate/cli.py:36:def main() -> None:
api/truerate/cli.py:41:def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
api/truerate/cli.py:49:def build_fake_model_cmd(
api/truerate/cli.py:60:def make_hiker() -> Hiker:
api/truerate/cli.py:65:def collect_cmd(handle: str) -> None:
api/truerate/cli.py:83:def collect_benchmark_cmd(workers: int = 1, fresh_hours: int = 24) -> None:
api/truerate/cli.py:117:def load_fake_model():
api/truerate/cli.py:121:def make_llm() -> Gemini:
api/truerate/cli.py:127:def build_metrics_cmd(workers: int = 1) -> None:
api/truerate/cli.py:142:    def label(item):
api/truerate/cli.py:156:    def safe_label(item):
api/truerate/cli.py:196:def validate_cmd(out_dir: Path = REPO_ROOT / "data" / "models") -> None:
api/truerate/cli.py:217:def experiment_cmd(out_dir: Path = REPO_ROOT / "data" / "models" / "experiments", fresh_csv: Path = REPO_ROOT / "data" / "fresh_test_20.csv",
api/truerate/cli.py:253:def redteam_cmd(out_dir: Path = MODELS_DIR) -> None:
api/truerate/config.py:16:class Settings(BaseSettings):
api/truerate/config.py:28:def get_settings() -> Settings:
api/truerate/db.py:18:def _client(uri: str) -> MongoClient:
api/truerate/db.py:22:def get_db() -> Database:
api/truerate/db.py:29:def ensure_indexes(db: Database) -> None:
api/truerate/db.py:37:def import_deals(db: Database, csv_path: Path) -> dict[str, int]:
api/truerate/db.py:63:def training_rows(db: Database) -> list[dict]:
api/truerate/experiment.py:37:def extra_features(snap: dict) -> dict:
api/truerate/experiment.py:59:def _utc(t: datetime) -> datetime:
api/truerate/experiment.py:63:def _with_extras(row: dict, snap: dict, mix: dict | None) -> dict:
api/truerate/experiment.py:69:def deal_rows(db) -> list[dict]:
api/truerate/experiment.py:74:def fresh_rows(db, prices: dict[str, float]) -> list[dict]:
api/truerate/experiment.py:93:def _num(x) -> float:
api/truerate/experiment.py:97:def _log(x) -> float:
api/truerate/experiment.py:101:def features_v2(m: dict) -> list[float]:
api/truerate/experiment.py:108:def _paid_typical(rows: list[dict]) -> float:
api/truerate/experiment.py:113:def _linear(regressor):
api/truerate/experiment.py:127:def _tabpfn():
api/truerate/experiment.py:137:def _sklearn_point(name: str, train: list[dict], test: list[dict]) -> np.ndarray:
api/truerate/experiment.py:147:def _today(train: list[dict]):
api/truerate/experiment.py:154:def _today_point(train: list[dict], test: list[dict], capped: bool = True) -> np.ndarray:
api/truerate/experiment.py:172:def _oof(rows: list[dict], point: str, folds: int = 10, seed: int = 0) -> np.ndarray:
api/truerate/experiment.py:179:def _offsets(resid: np.ndarray) -> dict:
api/truerate/experiment.py:189:def _band_offsets(rows: list[dict], resid: np.ndarray, by_band: bool) -> dict:
api/truerate/experiment.py:197:def conformal_offsets(rows: list[dict], point: str, by_band: bool = False, folds: int = 10, seed: int = 0) -> dict:
api/truerate/experiment.py:202:def _widen(rows: list[dict], m: dict) -> tuple[float, float]:
api/truerate/experiment.py:209:def _predict_both(point: str, train: list[dict], test: list[dict], folds: int = 10) -> dict[str, list[dict]]:
api/truerate/experiment.py:229:def predict(point: str, rng: str, train: list[dict], test: list[dict]) -> list[dict]:
api/truerate/experiment.py:233:def _served(train: list[dict], test: list[dict]) -> list[dict]:
api/truerate/experiment.py:239:def _all_preds(train: list[dict], test: list[dict], points, folds: int = 10) -> dict[str, list[dict]]:
api/truerate/experiment.py:249:def _summary(pairs: list[tuple[dict, dict]]) -> dict:
api/truerate/experiment.py:258:def score(test: list[dict], preds: list[dict]) -> dict:
api/truerate/experiment.py:265:def _mean(scores: list[dict]) -> dict:
api/truerate/experiment.py:270:def repeated_cv(train: list[dict], points=POINTS, repeats: int = 5, folds: int = 10) -> dict:
api/truerate/experiment.py:286:def pick(cv: dict, points=POINTS) -> dict:
api/truerate/experiment.py:297:def beats(after: dict, before: dict) -> bool:
api/truerate/experiment.py:303:def _bootstrap(test: list[dict], after: list[dict], before: list[dict], draws: int = 2000, seed: int = 0) -> dict:
api/truerate/experiment.py:307:    def arrays(ps):
api/truerate/experiment.py:317:def run(train: list[dict], holdout: list[dict], fresh: list[dict], repeats: int = 5, folds: int = 10, points=POINTS) -> dict:
api/truerate/experiment.py:344:def learning_curve(point: str, train: list[dict], test: list[dict], sizes, draws: int = 20, seed: int = 0) -> list[dict]:
api/truerate/experiment.py:357:def importance(point: str, rows: list[dict]) -> dict[str, float]:
api/truerate/experiment.py:378:def report_table(result: dict) -> str:
api/truerate/experiment.py:380:    def pct(x):
api/truerate/experiment.py:383:    def width(x):
api/truerate/experiment.py:386:    def cells(s):
api/truerate/experiment_plots.py:27:def _inr(x: float, _=None) -> str:
api/truerate/experiment_plots.py:32:def _log_axis(axis) -> None:
api/truerate/experiment_plots.py:38:def predicted_vs_actual(result: dict, names: tuple[str, str], path: Path) -> None:
api/truerate/experiment_plots.py:64:def ranges(result: dict, names: tuple[str, str], path: Path) -> None:
api/truerate/experiment_plots.py:91:def importance(values: dict[str, float], title: str, path: Path, top: int = 12) -> None:
api/truerate/experiment_plots.py:107:def learning(curves: dict[str, list[dict]], labels: dict[str, str], n_test: int, path: Path) -> None:
api/truerate/instagram.py:20:class HikerError(RuntimeError):
api/truerate/instagram.py:26:def _has_pic(url: str | None) -> bool:
api/truerate/instagram.py:30:def parse_profile(raw: dict) -> dict:
api/truerate/instagram.py:47:def parse_about(raw: dict) -> dict:
api/truerate/instagram.py:51:def parse_accounts(users: list[dict]) -> list[dict]:
api/truerate/instagram.py:65:def parse_reels(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:90:def parse_tagged(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:104:def mark_pinned(reels: list[dict]) -> list[dict]:
api/truerate/instagram.py:113:def parse_comments(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:120:class Hiker:
api/truerate/instagram.py:153:    def profile(self, username: str) -> dict:
api/truerate/instagram.py:156:    def about(self, pk: str) -> dict:
api/truerate/instagram.py:159:    def reels(self, pk: str, pages: int = 3, on_page=None) -> list[dict]:
api/truerate/instagram.py:173:    def comments(self, media_id: str) -> list[dict]:
api/truerate/instagram.py:176:    def likers(self, media_id: str, n: int = 200) -> list[dict]:
api/truerate/instagram.py:184:    def followers(self, pk: str) -> list[dict]:
api/truerate/instagram.py:187:    def tagged(self, pk: str) -> list[dict]:
api/truerate/instagram.py:190:    def suggested(self, pk: str) -> list[dict]:
api/truerate/instagram.py:194:def collect(hiker: Hiker, handle: str, comment_reels: int = 10, liker_reels: int = 3, workers: int = 1) -> dict:
api/truerate/instagram.py:235:def _or_empty(fetch, key: str, empty=None):
api/truerate/instagram.py:246:def fetch_covers(reels: list[dict], limit: int = 6) -> dict[str, bytes]:
api/truerate/instagram.py:248:    def one(http, r):
api/truerate/llm.py:10:class Gemini:
api/truerate/llm.py:18:    def json(self, prompt: str, schema: dict, images: list[bytes] = (), audio: list[bytes] = ()) -> dict:
api/truerate/pipeline.py:45:class Deps:
api/truerate/pipeline.py:57:def when(days: int) -> str:
api/truerate/pipeline.py:61:def _flag_text(f: dict, s: dict) -> str:
api/truerate/pipeline.py:76:def _brand(reel: dict, handle: str) -> str | None:
api/truerate/pipeline.py:82:def _days_ago(iso: str) -> int:
api/truerate/pipeline.py:86:def analyze(handle: str, inputs: dict, deps: Deps, step: Callable[[int], None] = lambda i: None) -> dict:
api/truerate/pipeline.py:139:    def kind(r):
api/truerate/pipeline.py:219:def _decide(v, flags, p, inputs, metrics, typical, fit, fit_share, competitor) -> dict:
api/truerate/pipeline.py:247:def _negotiation(p: dict, flags: list[dict], metrics: dict, category: str) -> dict:
api/truerate/pipeline.py:256:def check_quote(r: dict, quote: int) -> dict:
api/truerate/pricing.py:19:def _group(n: float) -> str:
api/truerate/pricing.py:28:def inr(n: float) -> str:
api/truerate/pricing.py:32:def round500(x: float) -> int:
api/truerate/pricing.py:36:def features(m: dict) -> list[float]:
api/truerate/pricing.py:40:def per_1k(row: dict) -> float:
api/truerate/pricing.py:45:class Core:
api/truerate/pricing.py:54:    def fit(cls, rows: list[dict]) -> "Core":
api/truerate/pricing.py:61:    def predict_logs(self, m: dict) -> tuple[float, float, list[dict]]:
api/truerate/pricing.py:72:class PriceModel:
api/truerate/pricing.py:81:    def rows(self) -> list[dict]:
api/truerate/pricing.py:85:def fit(rows: list[dict], blend: tuple[float, float, float] | None = None) -> PriceModel:
api/truerate/pricing.py:115:def market_reference(followers: int) -> dict:
api/truerate/pricing.py:120:def collab_factor(n: int, ratio: float | None, typical: float, prior: float | None = None) -> tuple[float, float]:
api/truerate/pricing.py:130:def price(model: PriceModel, m: dict, genuine_share: float = 1.0) -> dict:
api/truerate/pricing.py:190:def band_median_price(rows: list[dict], followers: int) -> float:
api/truerate/pricing.py:195:def modash_price(rows: list[dict], m: dict) -> float:
api/truerate/pricing.py:203:def _summary(errors: list[dict], method: str) -> dict:
api/truerate/pricing.py:208:def validate(rows: list[dict]) -> dict:
api/truerate/pricing.py:213:    def errors(r: dict, m: PriceModel, others: list[dict]) -> dict:
api/truerate/pricing.py:249:def rate_card(model: PriceModel) -> list[dict]:
api/truerate/pricing.py:262:def thin_categories(model: PriceModel) -> list[dict]:
api/truerate/signals.py:16:def _digit_ratio(text: str) -> float:
api/truerate/signals.py:20:def account_features(acc: dict) -> list[float]:
api/truerate/signals.py:33:def load_kaggle(path: Path) -> tuple[list[list[float]], list[int]]:
api/truerate/signals.py:38:def train_fake_model(X: list[list[float]], y: list[int]) -> RandomForestClassifier:
api/truerate/signals.py:42:def fake_share(model: RandomForestClassifier, accounts: list[dict]) -> float | None:
api/truerate/signals.py:75:def category_from_niche(genres: list[str]) -> str | None:
api/truerate/signals.py:84:def is_paid(reel: dict) -> bool:
api/truerate/signals.py:88:def recent_reels(snapshot: dict) -> list[dict]:
api/truerate/signals.py:93:def reel_metrics(snapshot: dict, labels: dict | None = None) -> dict:
api/truerate/signals.py:99:    def paid_reel(r):
api/truerate/signals.py:113:    def ratio(group):
api/truerate/signals.py:138:def label_niche(llm, bio: str, captions: list[str]) -> str:
api/truerate/signals.py:146:def band(followers: int) -> str:
api/truerate/signals.py:151:def _minilm():
api/truerate/signals.py:157:def minilm_embed(texts: list[str]) -> np.ndarray:
api/truerate/signals.py:169:def comment_signals(comments_by_reel: dict[str, list[dict]], embed) -> dict:
api/truerate/signals.py:191:def _cv(values: list[float]) -> float | None:
api/truerate/signals.py:196:def audience_signals(snapshot: dict, metrics: dict, fake_model, embed) -> dict:
api/truerate/signals.py:230:def _scale(value: float, log: bool) -> float:
api/truerate/signals.py:234:def band_norms(rows: list[dict]) -> dict:
api/truerate/signals.py:252:def verdict(signals: dict, norms: dict) -> dict:
api/truerate/signals.py:268:def genuine_share(signals: dict, norms: dict) -> float:
api/truerate/signals.py:285:def _bot(rng) -> dict:
api/truerate/signals.py:290:def make_fake(snapshot: dict, kind: str, rng) -> dict:
api/truerate/signals.py:326:def redteam(snapshots: list[dict], fake_model, embed, seed: int = 7) -> dict:
api/truerate/signals.py:331:    def signals(snap):
api/truerate/signals.py:352:def ambiguous(reel: dict) -> bool:
api/truerate/signals.py:357:def top_commenters(comments_by_reel: dict[str, list[dict]], n: int = 15) -> list[dict]:
api/truerate/signals.py:382:def label_creator(llm, snapshot: dict, images: dict[str, bytes]) -> dict:
api/truerate/signals.py:415:def commenter_mix(snapshot: dict, fake_model, labels: dict) -> dict:
api/truerate/signals.py:438:def _model(url: str):
api/truerate/signals.py:451:def _face_detector():
api/truerate/signals.py:459:def _person_detector():
api/truerate/signals.py:466:def has_face(image: bytes) -> bool:
api/truerate/signals.py:477:def face_share(covers: dict[str, bytes], detect=has_face) -> float | None:
api/truerate/signals.py:487:def commenter_rings(commenters_by_creator: dict[str, set[str]]) -> dict[str, int]:
api/truerate/signals.py:506:def _anomaly_row(signals: dict, typical: dict) -> list[float]:
api/truerate/signals.py:511:def fit_anomaly(rows: list[dict]):
api/truerate/signals.py:521:def audience_warnings(signals: dict, forest) -> list[str]:
api/truerate/signals.py:534:def spoken_candidates(reels: list[dict], n: int = SPOKEN_REELS) -> list[dict]:
api/truerate/signals.py:550:def label_spoken(llm, clips: dict[str, bytes]) -> dict[str, dict]:
```

## TypeScript (web/src/)
```
web/src/app/(app)/about/content.ts:3:export const FLOW = [
web/src/app/(app)/about/content.ts:12:export const SIGNALS: [string, string, string][] = [
web/src/app/(app)/about/content.ts:31:export const FAKE_KINDS: Record<string, [string, string]> = {
web/src/app/(app)/about/content.ts:40:export const OTHER_PAGES: [string, string][] = [
web/src/app/(app)/about/content.ts:47:export const LIMITS = [
web/src/app/(app)/about/page.tsx:16:export default function AboutPage() {
web/src/app/(app)/analyses/[id]/analysis-view.tsx:27:export default function AnalysisView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/analyses/[id]/page.tsx:6:export default function AnalysisPage({ params }: PageProps<"/analyses/[id]">) {
web/src/app/(app)/analyses/[id]/print/page.tsx:5:export default function PrintPage({ params }: PageProps<"/analyses/[id]/print">) {
web/src/app/(app)/analyses/[id]/print/print-view.tsx:9:export default function PrintView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/batch/[id]/batch-view.tsx:16:export default function BatchView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/batch/[id]/page.tsx:5:export default function BatchResultPage({ params }: PageProps<"/batch/[id]">) {
web/src/app/(app)/batch/page.tsx:14:export default function BatchPage() {
web/src/app/(app)/layout.tsx:7:export default function AppLayout({ children }: LayoutProps<"/">) {
web/src/app/(app)/nav.tsx:18:export function NavLinks({ path }: { path: string | null }) {
web/src/app/(app)/nav.tsx:34:export default function Nav() {
web/src/app/(app)/page.tsx:13:export default function AnalyzePage() {
web/src/app/(app)/rate-card/page.tsx:15:export default function RateCardPage() {
web/src/app/(app)/sign-out.tsx:7:export default function SignOut() {
web/src/app/layout.tsx:12:export const metadata: Metadata = {
web/src/app/layout.tsx:17:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/login/login-form.tsx:8:export default function LoginForm() {
web/src/app/login/page.tsx:3:export default function LoginPage() {
web/src/components/chips.tsx:7:export function CallChip({ call, large = false }: { call: string; large?: boolean }) {
web/src/components/chips.tsx:15:export const VERDICTS = ["Real audience", "Some fake activity", "Mostly fake"] as const;
web/src/components/chips.tsx:16:export const VERDICT_COLOR: Record<string, string> = {
web/src/components/product-options.tsx:4:export default function ProductOptions({ products, categories }: { products: Product[]; categories: string[] }) {
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
web/src/lib/api-types.ts:166:export type webhooks = Record<string, never>;
web/src/lib/api-types.ts:167:export interface components {
web/src/lib/api-types.ts:759:export type $defs = Record<string, never>;
web/src/lib/api-types.ts:760:export interface operations {
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
web/src/lib/api.ts:14:export type Product = Schemas["Product"];
web/src/lib/api.ts:30:export const api = {
web/src/lib/format.ts:3:export function inr(n: number): string {
web/src/lib/format.ts:11:export function compact(n: number): string {
web/src/lib/format.ts:18:export function pct(x: number, digits = 0): string {
web/src/lib/format.ts:22:export function daysAgo(iso: string): string {
web/src/lib/format.ts:28:export const SESSION_COOKIE = "truerate_session";
web/src/proxy.ts:4:export function proxy(request: NextRequest) {
web/src/proxy.ts:12:export const config = {
```

<!-- mapped: .@4c36c20 | paths: api/, web/src/ -->
