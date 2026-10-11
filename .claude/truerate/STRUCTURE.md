# truerate structure

Generated from git. Signatures only.

## Files
```
.env.example
.gitignore
Makefile
api/.python-version
api/pyproject.toml
api/scripts/collect_deals.py
api/scripts/make_deck.py
api/scripts/seed_dev.py
api/tests/conftest.py
api/tests/test_app.py
api/tests/test_audience.py
api/tests/test_audio.py
api/tests/test_brand.py
api/tests/test_collect_deals.py
api/tests/test_db.py
api/tests/test_deck.py
api/tests/test_experiment.py
api/tests/test_instagram.py
api/tests/test_llm.py
api/tests/test_outputs.py
api/tests/test_pipeline.py
api/tests/test_pricing.py
api/tests/test_signals.py
api/tests/test_webcheck.py
api/truerate/__init__.py
api/truerate/app.py
api/truerate/audio.py
api/truerate/brand.py
api/truerate/cli.py
api/truerate/config.py
api/truerate/db.py
api/truerate/experiment.py
api/truerate/experiment_plots.py
api/truerate/instagram.py
api/truerate/llm.py
api/truerate/outputs.py
api/truerate/pipeline.py
api/truerate/pricing.py
api/truerate/signals.py
api/truerate/webcheck.py
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
web/src/app/(app)/brand/[id]/brand-view.tsx
web/src/app/(app)/brand/[id]/page.tsx
web/src/app/(app)/brand/page.tsx
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
web/src/components/batch/compare.tsx
web/src/components/brand/result.tsx
web/src/components/chart-tip.tsx
web/src/components/chips.tsx
web/src/components/product-options.tsx
web/src/components/recent-table.tsx
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
web/src/components/tabs.tsx
web/src/components/value-bars.tsx
web/src/components/verdicts.tsx
web/src/lib/api-types.ts
web/src/lib/api.ts
web/src/lib/format.ts
web/src/proxy.ts
web/tsconfig.json
api/tests/fixtures/*.json  (recorded HikerAPI responses, one per endpoint)
```

## Python (api/)
```
api/scripts/collect_deals.py:32:class Paced(httpx.BaseTransport):
api/scripts/collect_deals.py:49:    def handle_request(self, request: httpx.Request) -> httpx.Response:
api/scripts/collect_deals.py:64:    def close(self) -> None:
api/scripts/collect_deals.py:68:def plan(rows: list[dict], done: set[str]) -> list[tuple[str, datetime]]:
api/scripts/collect_deals.py:78:def run(hiker, todo: list[tuple[str, datetime]], workers: int, log: Path, collect=collect, store: Path | None = None) -> dict:
api/scripts/collect_deals.py:113:def main() -> None:
api/scripts/make_deck.py:40:def pct(x) -> str:
api/scripts/make_deck.py:44:class Deck:
api/scripts/make_deck.py:49:    def slide(self, title: str, note: str = ""):
api/scripts/make_deck.py:58:    def text(self, s, x, y, w, h, lines, gap=6):
api/scripts/make_deck.py:71:    def table(self, s, x, y, widths, rows, size=13, bold_row=None, colors=None):
api/scripts/make_deck.py:93:def _plain_style(tbl):
api/scripts/make_deck.py:101:def _bottom_rule(cell):
api/scripts/make_deck.py:109:def _log_axes(chart):
api/scripts/make_deck.py:130:def build_deck(report: dict, rt: dict, screenshot: Path | None, out: Path, experiments: dict | None = None, widths: dict | None = None) -> None:
api/scripts/make_deck.py:229:    def scores(m):
api/scripts/seed_dev.py:43:def snap_for(handle, seed):
api/scripts/seed_dev.py:61:def save(aid, handle, inputs, out, minutes):
api/tests/conftest.py:8:def db():
api/tests/test_app.py:7:def test_health():
api/tests/test_app.py:11:def test_settings_read_env(monkeypatch):
api/tests/test_app.py:26:def test_parse_handle_accepts_handles_and_links():
api/tests/test_app.py:34:def client(world, monkeypatch):
api/tests/test_app.py:41:def test_analysis_runs_and_reports(client):
api/tests/test_app.py:53:def test_bad_handle_is_rejected(client):
api/tests/test_app.py:57:def test_out_of_scope_and_failures_are_recorded(client, world, monkeypatch):
api/tests/test_app.py:64:    def broken(handle):
api/tests/test_app.py:72:def _with_collect(d, fn):
api/tests/test_app.py:77:def test_meta_lists_categories_and_coverage(client, tmp_path, monkeypatch):
api/tests/test_app.py:90:def test_quote_check_endpoint(client):
api/tests/test_app.py:98:def test_batch_runs_every_handle_and_ranks_by_cost(client):
api/tests/test_app.py:108:def test_batch_rejects_bad_or_too_many_handles(client):
api/tests/test_app.py:113:def test_rate_card_endpoint(client, tmp_path, monkeypatch):
api/tests/test_app.py:127:def test_batch_puts_avoid_after_everything_else(client, world, monkeypatch):
api/tests/test_app.py:138:def test_removing_an_analysis_hides_it_from_recent_but_keeps_its_report(client):
api/tests/test_app.py:147:def test_analyses_left_running_by_a_stopped_server_are_marked_failed(world):
api/tests/test_app.py:156:def test_recent_batches_are_listed_newest_first_with_progress(client):
api/tests/test_app.py:164:def test_finished_analyses_and_batch_rows_carry_plain_verdicts(client):
api/tests/test_app.py:174:def test_reports_saved_before_the_likely_band_get_it_when_read(client, world):
api/tests/test_app.py:186:def test_a_brand_run_is_started_polled_and_listed(client, monkeypatch):
api/tests/test_app.py:194:    def brand_deps(fetch):
api/tests/test_app.py:206:    def missing(handle):
api/tests/test_app.py:214:def test_recent_lists_carry_names_and_batches_and_brand_runs_can_be_hidden(client, monkeypatch):
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
api/tests/test_brand.py:20:class BrandLLM(TopicLLM):
api/tests/test_brand.py:23:    def json(self, prompt, schema, images=(), audio=()):
api/tests/test_brand.py:30:def test_parse_brand_tells_handles_websites_and_names_apart():
api/tests/test_brand.py:39:def test_site_text_keeps_the_words_and_drops_the_code():
api/tests/test_brand.py:48:def test_the_brand_profile_comes_from_the_brands_own_words():
api/tests/test_brand.py:54:def test_partners_are_the_creators_seen_with_the_brand_but_never_the_brand_itself():
api/tests/test_brand.py:58:def creator(**changes) -> dict:
api/tests/test_brand.py:64:def test_scoring_puts_a_fitting_real_good_value_creator_first_and_says_why():
api/tests/test_brand.py:76:def test_budget_plan_picks_the_most_views_that_fit_the_budget():
api/tests/test_brand.py:83:def test_the_pool_labels_where_each_creator_came_from(world):
api/tests/test_brand.py:96:def test_a_brand_run_profiles_ranks_plans_and_lists_who_to_price_next(world):
api/tests/test_brand.py:113:def test_a_brand_on_instagram_costs_three_requests(tmp_path):
api/tests/test_brand.py:124:def test_the_plan_never_books_a_creator_with_a_clear_problem():
api/tests/test_collect_deals.py:12:def test_plan_reaches_back_before_each_payout_and_skips_creators_done():
api/tests/test_collect_deals.py:19:def test_run_keeps_going_past_failures_and_queues_rate_limits_for_another_pass(tmp_path):
api/tests/test_collect_deals.py:22:    def fake_collect(hiker, handle, workers, back_to):
api/tests/test_collect_deals.py:37:def test_run_stops_when_credit_runs_out(tmp_path):
api/tests/test_collect_deals.py:38:    def broke(hiker, handle, workers, back_to):
api/tests/test_collect_deals.py:46:def test_paced_transport_waits_out_rate_limits_and_slows_down():
api/tests/test_collect_deals.py:51:    def inner(request):
api/tests/test_collect_deals.py:61:def test_paced_transport_speeds_back_up_on_success():
api/tests/test_db.py:9:def write_csv(path, per_tier=11):
api/tests/test_db.py:18:def test_indexes(db):
api/tests/test_db.py:25:def test_import_deals_holds_out_10_per_tier_and_is_idempotent(db, tmp_path):
api/tests/test_db.py:37:def test_import_deals_command(db, tmp_path, monkeypatch):
api/tests/test_db.py:44:def write_dated_csv(path, counts=(("small", 20), ("medium", 12), ("big", 8))):
api/tests/test_db.py:53:def test_import_deals_holds_out_a_share_of_each_tier_from_creators_not_excluded(db, tmp_path):
api/tests/test_db.py:70:def test_import_deals_command_with_a_holdout_share(db, tmp_path, monkeypatch):
api/tests/test_deck.py:19:def test_deck_has_at_most_12_slides_with_the_real_numbers_and_no_handles(tmp_path):
api/tests/test_experiment.py:16:def test_extra_features_read_account_age_reel_length_posting_rate_and_contact():
api/tests/test_experiment.py:30:def test_ranges_hold_close_to_their_stated_share_of_unseen_prices():
api/tests/test_experiment.py:39:def test_ranges_by_follower_band_are_narrower_where_similar_deals_agree():
api/tests/test_experiment.py:49:def _sets(seed=7):
api/tests/test_experiment.py:55:def test_the_pick_never_looks_at_held_out_or_fresh_prices():
api/tests/test_experiment.py:70:def test_fresh_rows_rebuild_the_features_a_stored_analysis_was_priced_from(world):
api/tests/test_experiment.py:80:def test_learning_curve_and_importance_have_one_value_per_size_and_feature():
api/tests/test_experiment.py:88:def test_tabpfn_uses_the_v2_weights_whose_license_allows_commercial_use():
api/tests/test_experiment.py:97:def test_fresh_deals_are_scored_by_the_model_exactly_as_served():
api/tests/test_experiment.py:106:def test_per_creator_ranges_are_narrow_where_similar_deals_agree_and_still_hold_their_level():
api/tests/test_experiment.py:107:    def noisy(n, seed):
api/tests/test_experiment.py:125:def test_coverage_by_width_counts_prices_inside_a_range_of_each_width_around_the_middle():
api/tests/test_experiment.py:132:def test_the_ensemble_averages_its_members_in_log_price():
api/tests/test_experiment.py:135:    def with_extras(rows, seed):  # boosting needs the new features to have values, as WLDD's deals do
api/tests/test_experiment.py:146:def test_dated_rows_use_the_stats_around_the_payout_where_there_are_any():
api/tests/test_experiment.py:158:def test_run_scores_one_held_out_set_when_there_are_no_fresh_deals():
api/tests/test_experiment.py:172:def test_live_model_is_scored_on_the_held_out_deals_exactly_as_the_app_prices_them():
api/tests/test_experiment.py:183:def test_repeated_cv_gives_the_same_scores_on_several_cores():
api/tests/test_experiment.py:192:def test_charts_draw_a_run_without_fresh_deals(tmp_path):
api/tests/test_experiment.py:202:def test_experiment_plots_redraws_from_saved_results(tmp_path):
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
api/tests/test_instagram.py:260:def _paged_hiker(store, pages: int, step_days: int = 30, calls=None):
api/tests/test_instagram.py:264:    def page(k):
api/tests/test_instagram.py:270:    def handler(request):
api/tests/test_instagram.py:282:def test_reels_page_back_past_a_date(tmp_path):
api/tests/test_instagram.py:293:def test_reels_without_a_date_keep_the_page_limit(tmp_path):
api/tests/test_instagram.py:300:def test_reels_back_to_a_date_stop_at_the_page_cap(tmp_path):
api/tests/test_instagram.py:309:def test_collect_passes_the_date_to_the_reel_pages(tmp_path):
api/tests/test_instagram.py:317:def test_collect_benchmark_reaches_back_before_each_deals_payout(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:321:    def fake_collect(hiker, handle, back_to=None):
api/tests/test_instagram.py:333:def test_collect_benchmark_can_be_limited_to_a_list_of_creators(db, tmp_path, monkeypatch):
api/tests/test_instagram.py:337:    def fake_collect(hiker, handle, back_to=None):
api/tests/test_llm.py:7:class Reply:
api/tests/test_llm.py:11:def flaky(failures):
api/tests/test_llm.py:15:    def generate_content(**kwargs):
api/tests/test_llm.py:24:def test_a_dropped_gemini_connection_is_retried(monkeypatch):
api/tests/test_llm.py:31:def test_gemini_gives_up_after_three_dropped_connections(monkeypatch):
api/tests/test_llm.py:40:def test_gemini_asks_for_low_thinking(monkeypatch):
api/tests/test_outputs.py:7:def result(**changes) -> dict:
api/tests/test_outputs.py:29:def by_key(r: dict, inputs: dict | None = None) -> dict:
api/tests/test_outputs.py:33:def test_a_genuine_good_value_creator_reads_as_plain_answers():
api/tests/test_outputs.py:41:def test_a_quote_is_judged_against_the_likely_band_first():
api/tests/test_outputs.py:51:def test_the_budget_says_whether_the_creator_fits():
api/tests/test_outputs.py:58:def test_fake_activity_is_named_in_plain_words_not_numbers():
api/tests/test_outputs.py:65:def test_value_reliability_and_ads_have_three_grades():
api/tests/test_outputs.py:75:def test_product_fit_and_a_rival_ad_are_answers_too():
api/tests/test_outputs.py:81:def test_every_finished_analysis_gets_verdicts(world):
api/tests/test_outputs.py:87:def test_the_web_check_reads_as_a_plain_answer():
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
api/tests/test_pipeline.py:133:def test_a_brand_that_tagged_the_creator_recently_is_a_competitor(world):
api/tests/test_pipeline.py:144:def test_money_uses_indian_grouping_and_days_read_naturally():
api/tests/test_pipeline.py:149:def test_reasons_and_lines_use_indian_grouping(world):
api/tests/test_pipeline.py:156:def test_a_handle_instagram_doesnt_know_reads_as_a_plain_sentence(world):
api/tests/test_pipeline.py:157:    def missing(handle):
api/tests/test_pipeline.py:166:def test_a_spoken_ad_makes_the_reel_paid_and_shows_the_quote(world):
api/tests/test_pipeline.py:175:def test_the_creators_own_handle_is_never_the_brand(world):
api/tests/test_pipeline.py:184:def test_a_specific_product_is_matched_through_its_pricing_category(world):
api/tests/test_pipeline.py:192:def test_a_competitor_for_a_specific_product_is_named_by_the_category_it_was_matched_in(world):
api/tests/test_pipeline.py:202:def test_a_creator_wldd_has_booked_is_never_turned_away_by_the_cover_check(world):
api/tests/test_pipeline.py:209:def test_a_quote_above_where_most_deals_land_means_negotiate():
api/tests/test_pipeline.py:213:    def call(quote):
api/tests/test_pipeline.py:222:def test_the_price_model_gets_the_extra_features_boosting_reads(world, monkeypatch):
api/tests/test_pipeline.py:228:    def spy(model, m, genuine_share=1.0):
api/tests/test_pricing.py:17:def synthetic_rows(n=90, seed=1):
api/tests/test_pricing.py:35:def test_bands_and_rounding():
api/tests/test_pricing.py:40:def test_collab_factor_shrinks_few_ads_toward_the_typical_drop():
api/tests/test_pricing.py:48:def test_collab_factor_never_raises_a_price_and_never_more_than_halves_it():
api/tests/test_pricing.py:55:def test_baselines():
api/tests/test_pricing.py:63:def test_price_has_a_range_waterfall_comparables_and_delivery():
api/tests/test_pricing.py:78:def test_validate_beats_both_baselines_on_synthetic_deals():
api/tests/test_pricing.py:95:def test_range_covers_most_held_out_prices():
api/tests/test_pricing.py:101:def test_validate_command_saves_model_and_report(db, tmp_path, monkeypatch):
api/tests/test_pricing.py:114:def test_rate_card_per_category():
api/tests/test_pricing.py:122:def test_a_creator_bigger_than_any_wldd_deal_gets_a_note():
api/tests/test_pricing.py:130:def test_rate_card_leaves_out_categories_with_fewer_than_3_deals():
api/tests/test_pricing.py:138:def test_every_price_carries_the_published_asking_range_for_its_size():
api/tests/test_pricing.py:145:def test_beyond_wldds_largest_creator_the_price_leans_on_the_market_discounted_the_way_wldd_pays():
api/tests/test_pricing.py:168:def test_below_wldds_smallest_creator_only_the_bottom_widens():
api/tests/test_pricing.py:177:def test_the_range_comes_from_mapie_cross_conformal_at_80_percent():
api/tests/test_pricing.py:194:def test_the_likely_band_is_about_3x_wide_around_the_middle_and_inside_the_full_range():
api/tests/test_pricing.py:206:def test_validate_dated_trains_the_served_model_on_the_stats_around_each_payout(db, tmp_path, monkeypatch):
api/tests/test_pricing.py:219:def with_extras(rows, seed):
api/tests/test_pricing.py:228:def test_boosted_model_serves_exactly_what_the_experiment_scored(ranges):
api/tests/test_pricing.py:241:def test_boosted_model_still_discounts_fake_engagement_and_weak_sponsored_reach():
api/tests/test_pricing.py:249:def test_validate_can_serve_the_boosted_model(db, tmp_path, monkeypatch):
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
api/tests/test_signals.py:283:def test_deal_window_metrics_use_own_reels_in_the_90_days_before_the_payout():
api/tests/test_signals.py:294:def test_deal_window_metrics_need_three_own_reels():
api/tests/test_signals.py:302:def test_build_metrics_adds_the_stats_around_the_payout_date(db, monkeypatch):
api/tests/test_signals.py:316:def test_build_metrics_reuses_labels_for_a_rebuilt_snapshot_of_the_same_reels(db, monkeypatch):
api/tests/test_signals.py:341:def test_label_offline_reads_niche_from_captions_and_never_asks_gemini(db, monkeypatch):
api/tests/test_signals.py:342:    def snap_with(handle, word):
api/tests/test_signals.py:356:    def embed(texts):
api/tests/test_signals.py:384:def test_build_metrics_stores_the_extra_features_the_boosted_model_reads(db, monkeypatch):
api/tests/test_webcheck.py:9:class SearchLLM(TopicLLM):
api/tests/test_webcheck.py:16:    def search(self, prompt):
api/tests/test_webcheck.py:24:def test_a_stated_rate_is_read_with_its_sources():
api/tests/test_webcheck.py:30:def test_nothing_found_or_a_garbled_reply_says_so_instead_of_inventing_a_price():
api/tests/test_webcheck.py:39:def test_only_creators_bigger_than_wldds_largest_get_a_web_check_and_it_never_sees_a_deal_price(world):
api/tests/test_webcheck.py:52:def test_a_failed_web_check_never_fails_the_analysis(world):
api/truerate/app.py:29:async def lifespan(app: FastAPI):
api/truerate/app.py:42:def fail_interrupted(db) -> None:
api/truerate/app.py:47:def submit(fn) -> None:
api/truerate/app.py:54:class Profile(BaseModel):
api/truerate/app.py:63:class Decision(BaseModel):
api/truerate/app.py:68:class WaterfallStep(BaseModel):
api/truerate/app.py:73:class Comparable(BaseModel):
api/truerate/app.py:82:class Delivery(BaseModel):
api/truerate/app.py:90:class MarketReference(BaseModel):
api/truerate/app.py:97:class Price(BaseModel):
api/truerate/app.py:115:class Flag(BaseModel):
api/truerate/app.py:123:class Language(BaseModel):
api/truerate/app.py:128:class Mix(BaseModel):
api/truerate/app.py:137:class Audience(BaseModel):
api/truerate/app.py:147:class Engagement(BaseModel):
api/truerate/app.py:154:class ReelPoint(BaseModel):
api/truerate/app.py:164:class FollowerPoint(BaseModel):
api/truerate/app.py:169:class Ratio(BaseModel):
api/truerate/app.py:174:class PaidRatio(Ratio):
api/truerate/app.py:178:class Ad(BaseModel):
api/truerate/app.py:187:class BrandTag(BaseModel):
api/truerate/app.py:194:class Placement(BaseModel):
api/truerate/app.py:208:class Niche(BaseModel):
api/truerate/app.py:216:class Competitor(BaseModel):
api/truerate/app.py:223:class Cheaper(BaseModel):
api/truerate/app.py:230:class Negotiation(BaseModel):
api/truerate/app.py:237:class Source(BaseModel):
api/truerate/app.py:242:class WebRate(BaseModel):
api/truerate/app.py:251:class Report(BaseModel):
api/truerate/app.py:272:class Inputs(BaseModel):
api/truerate/app.py:278:class AnalysisRequest(Inputs):
api/truerate/app.py:282:class Created(BaseModel):
api/truerate/app.py:286:class Output(BaseModel):
api/truerate/app.py:293:class Analysis(BaseModel):
api/truerate/app.py:308:class AnalysisSummary(BaseModel):
api/truerate/app.py:321:class QuoteRequest(BaseModel):
api/truerate/app.py:325:class QuoteCheck(BaseModel):
api/truerate/app.py:333:class BatchRequest(Inputs):
api/truerate/app.py:337:class BatchRow(BaseModel):
api/truerate/app.py:359:class Batch(BaseModel):
api/truerate/app.py:368:class Creator(BaseModel):
api/truerate/app.py:373:class BatchSummary(BaseModel):
api/truerate/app.py:382:class BrandRequest(BaseModel):
api/truerate/app.py:389:class BrandAnswer(BaseModel):
api/truerate/app.py:395:class BrandPick(BaseModel):
api/truerate/app.py:415:class BrandProfile(BaseModel):
api/truerate/app.py:428:class BrandPlan(BaseModel):
api/truerate/app.py:434:class BrandResult(BaseModel):
api/truerate/app.py:442:class BrandRun(BaseModel):
api/truerate/app.py:453:class BrandSummary(BaseModel):
api/truerate/app.py:461:class Per1k(BaseModel):
api/truerate/app.py:467:class CategoryRate(BaseModel):
api/truerate/app.py:475:class ThinCategory(BaseModel):
api/truerate/app.py:480:class RateCard(BaseModel):
api/truerate/app.py:485:class Product(BaseModel):
api/truerate/app.py:490:class Meta(BaseModel):
api/truerate/app.py:496:class ModelReport(BaseModel):
api/truerate/app.py:506:def parse_handle(text: str) -> str | None:
api/truerate/app.py:512:def _models() -> tuple:
api/truerate/app.py:516:def _with_likely(result: dict | None) -> dict | None:
api/truerate/app.py:524:def _warm() -> None:
api/truerate/app.py:536:def make_deps(db) -> Deps:
api/truerate/app.py:544:def make_brand_deps(db) -> BrandDeps:
api/truerate/app.py:552:def _run_brand(run_id: str, req: dict) -> None:
api/truerate/app.py:555:    def step(i: int) -> None:
api/truerate/app.py:569:def _run(analysis_id: str, handle: str, inputs: dict) -> None:
api/truerate/app.py:572:    def step(i: int) -> None:
api/truerate/app.py:583:def _read_json(name: str) -> dict | None:
api/truerate/app.py:592:def health() -> dict:
api/truerate/app.py:597:def create_analysis(req: AnalysisRequest) -> Created:
api/truerate/app.py:606:def _start(db, handle: str, inputs: dict, batch_id: str | None = None) -> str:
api/truerate/app.py:615:def create_brand_run(req: BrandRequest) -> Created:
api/truerate/app.py:626:def list_brand_runs() -> list[BrandSummary]:
api/truerate/app.py:632:def hide_brand_run(run_id: str) -> None:
api/truerate/app.py:639:def get_brand_run(run_id: str) -> BrandRun:
api/truerate/app.py:647:def create_batch(req: BatchRequest) -> Created:
api/truerate/app.py:666:def list_batches() -> list[BatchSummary]:
api/truerate/app.py:679:def hide_batch(batch_id: str) -> None:
api/truerate/app.py:686:def get_batch(batch_id: str) -> Batch:
api/truerate/app.py:710:def get_rate_card() -> RateCard:
api/truerate/app.py:719:def list_analyses() -> list[AnalysisSummary]:
api/truerate/app.py:729:def get_analysis(analysis_id: str) -> Analysis:
api/truerate/app.py:739:def hide_analysis(analysis_id: str) -> None:
api/truerate/app.py:746:def quote_check(analysis_id: str, req: QuoteRequest) -> QuoteCheck:
api/truerate/app.py:756:def meta() -> Meta:
api/truerate/app.py:762:def model_report() -> ModelReport:
api/truerate/audio.py:19:def audio_from_video(data: bytes) -> bytes:
api/truerate/audio.py:42:def fetch_audio(reels: list[dict]) -> dict[str, bytes]:
api/truerate/audio.py:45:    def one(reel):
api/truerate/brand.py:22:def parse_brand(text: str) -> dict:
api/truerate/brand.py:38:def site_text(http, url: str, limit: int = 3000) -> str:
api/truerate/brand.py:65:def profile_brand(llm, text: str) -> dict:
api/truerate/brand.py:72:def instagram_brand(hiker, handle: str) -> dict:
api/truerate/brand.py:80:def brand_partners(data: dict) -> list[str]:
api/truerate/brand.py:92:def candidates(db, model: PriceModel, brand_handle: str | None, partners: list[str]) -> list[dict]:
api/truerate/brand.py:97:    def add(handle: str, source: str, data: dict | None = None) -> None:
api/truerate/brand.py:131:def score(c: dict, brand: dict, budget: int | None) -> dict:
api/truerate/brand.py:136:    def add(key: str, status: str, title: str, points: float) -> None:
api/truerate/brand.py:197:def bookable(picks: list[dict]) -> list[dict]:
api/truerate/brand.py:202:def budget_plan(cands: list[dict], budget: int, unit: int = 500) -> dict:
api/truerate/brand.py:218:class BrandDeps:
api/truerate/brand.py:226:def run_brand(deps: BrandDeps, req: dict, step: Callable[[int], None] = lambda i: None) -> dict:
api/truerate/cli.py:44:def main() -> None:
api/truerate/cli.py:49:def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv",
api/truerate/cli.py:60:def build_fake_model_cmd(
api/truerate/cli.py:71:def make_hiker() -> Hiker:
api/truerate/cli.py:76:def collect_cmd(handle: str) -> None:
api/truerate/cli.py:94:def collect_benchmark_cmd(workers: int = 1, fresh_hours: int = 24, only: Path | None = None) -> None:
api/truerate/cli.py:133:def load_fake_model():
api/truerate/cli.py:137:def make_llm() -> Gemini:
api/truerate/cli.py:143:def build_metrics_cmd(workers: int = 1) -> None:
api/truerate/cli.py:158:    def label(item):
api/truerate/cli.py:174:    def safe_label(item):
api/truerate/cli.py:218:def label_offline_cmd() -> None:
api/truerate/cli.py:226:    def latest(handle):
api/truerate/cli.py:249:def validate_cmd(out_dir: Path = REPO_ROOT / "data" / "models", dated: bool = False, method: str = "ridge") -> None:
api/truerate/cli.py:275:def experiment_cmd(out_dir: Path = REPO_ROOT / "data" / "models" / "experiments", fresh_csv: Path = REPO_ROOT / "data" / "fresh_test_20.csv",
api/truerate/cli.py:317:def _draw_experiment(result: dict, out_dir: Path) -> None:
api/truerate/cli.py:333:def experiment_plots_cmd(out_dir: Path) -> None:
api/truerate/cli.py:340:def redteam_cmd(out_dir: Path = MODELS_DIR) -> None:
api/truerate/config.py:16:class Settings(BaseSettings):
api/truerate/config.py:28:def get_settings() -> Settings:
api/truerate/db.py:19:def _client(uri: str) -> MongoClient:
api/truerate/db.py:23:def get_db() -> Database:
api/truerate/db.py:30:def ensure_indexes(db: Database) -> None:
api/truerate/db.py:38:def import_deals(db: Database, csv_path: Path, holdout_share: float | None = None, exclude: set[str] | None = None) -> dict[str, int]:
api/truerate/db.py:75:def training_rows(db: Database) -> list[dict]:
api/truerate/experiment.py:33:def _utc(t: datetime) -> datetime:
api/truerate/experiment.py:37:def _with_extras(row: dict, snap: dict, mix: dict | None) -> dict:
api/truerate/experiment.py:41:def deal_rows(db) -> list[dict]:
api/truerate/experiment.py:46:def fresh_rows(db, prices: dict[str, float]) -> list[dict]:
api/truerate/experiment.py:68:def dated(rows: list[dict]) -> list[dict]:
api/truerate/experiment.py:84:def _paid_typical(rows: list[dict]) -> float:
api/truerate/experiment.py:89:def _linear(regressor):
api/truerate/experiment.py:102:def _tabpfn():
api/truerate/experiment.py:112:def _sklearn_point(name: str, train: list[dict], test: list[dict]) -> np.ndarray:
api/truerate/experiment.py:122:def _today(train: list[dict]):
api/truerate/experiment.py:129:def _today_point(train: list[dict], test: list[dict], capped: bool = True) -> np.ndarray:
api/truerate/experiment.py:152:def _oof(rows: list[dict], point: str, folds: int = 10, seed: int = 0) -> np.ndarray:
api/truerate/experiment.py:159:def _offsets(resid: np.ndarray) -> dict:
api/truerate/experiment.py:163:def _band_offsets(rows: list[dict], resid: np.ndarray, by_band: bool) -> dict:
api/truerate/experiment.py:171:def conformal_offsets(rows: list[dict], point: str, by_band: bool = False, folds: int = 10, seed: int = 0) -> dict:
api/truerate/experiment.py:176:def _local_spread(train: list[dict], resid: np.ndarray, targets: list[dict], leave_out_self: bool = False) -> np.ndarray:
api/truerate/experiment.py:178:    def pos(rows):
api/truerate/experiment.py:184:def _widen(rows: list[dict], m: dict) -> tuple[float, float]:
api/truerate/experiment.py:191:def _predict_both(point: str, train: list[dict], test: list[dict], folds: int = 10) -> dict[str, list[dict]]:
api/truerate/experiment.py:216:def predict(point: str, rng: str, train: list[dict], test: list[dict]) -> list[dict]:
api/truerate/experiment.py:220:def _served(train: list[dict], test: list[dict]) -> list[dict]:
api/truerate/experiment.py:226:def live_scores(model, test: list[dict]) -> dict:
api/truerate/experiment.py:231:def _all_preds(train: list[dict], test: list[dict], points, folds: int = 10) -> dict[str, list[dict]]:
api/truerate/experiment.py:241:def _summary(pairs: list[tuple[dict, dict]]) -> dict:
api/truerate/experiment.py:250:def score(test: list[dict], preds: list[dict]) -> dict:
api/truerate/experiment.py:260:def coverage_by_width(test: list[dict], preds: list[dict], widths=WIDTHS) -> dict:
api/truerate/experiment.py:267:def _mean(scores: list[dict]) -> dict:
api/truerate/experiment.py:275:def _cv_init(train: list[dict]) -> None:
api/truerate/experiment.py:280:def _cv_fold(job: tuple) -> tuple:
api/truerate/experiment.py:285:def repeated_cv(train: list[dict], points=POINTS, repeats: int = 5, folds: int = 10, workers: int = 1) -> dict:
api/truerate/experiment.py:313:def pick(cv: dict, points=POINTS) -> dict:
api/truerate/experiment.py:324:def beats(after: dict, before: dict) -> bool:
api/truerate/experiment.py:330:def _bootstrap(test: list[dict], after: list[dict], before: list[dict], draws: int = 2000, seed: int = 0) -> dict:
api/truerate/experiment.py:334:    def arrays(ps):
api/truerate/experiment.py:344:def run(train: list[dict], holdout: list[dict], fresh: list[dict], repeats: int = 5, folds: int = 10, points=POINTS, workers: int = 1) -> dict:
api/truerate/experiment.py:373:def learning_curve(point: str, train: list[dict], test: list[dict], sizes, draws: int = 20, seed: int = 0) -> list[dict]:
api/truerate/experiment.py:386:def importance(point: str, rows: list[dict]) -> dict[str, float]:
api/truerate/experiment.py:407:def report_table(result: dict) -> str:
api/truerate/experiment.py:409:    def pct(x):
api/truerate/experiment.py:412:    def width(x):
api/truerate/experiment.py:415:    def cells(s):
api/truerate/experiment_plots.py:27:def _inr(x: float, _=None) -> str:
api/truerate/experiment_plots.py:32:def _log_axis(axis) -> None:
api/truerate/experiment_plots.py:38:def predicted_vs_actual(result: dict, names: tuple[str, str], path: Path) -> None:
api/truerate/experiment_plots.py:64:def ranges(result: dict, names: tuple[str, str], path: Path) -> None:
api/truerate/experiment_plots.py:81:    def holds(x: dict, k: str) -> str:
api/truerate/experiment_plots.py:94:def importance(values: dict[str, float], title: str, path: Path, permutation: bool = False, top: int = 12) -> None:
api/truerate/experiment_plots.py:113:def learning(curves: dict[str, list[dict]], labels: dict[str, str], n_test: int, path: Path) -> None:
api/truerate/instagram.py:20:class HikerError(RuntimeError):
api/truerate/instagram.py:26:def _has_pic(url: str | None) -> bool:
api/truerate/instagram.py:30:def parse_profile(raw: dict) -> dict:
api/truerate/instagram.py:47:def parse_about(raw: dict) -> dict:
api/truerate/instagram.py:51:def parse_accounts(users: list[dict]) -> list[dict]:
api/truerate/instagram.py:65:def parse_reels(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:90:def parse_tagged(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:104:def mark_pinned(reels: list[dict]) -> list[dict]:
api/truerate/instagram.py:113:def parse_comments(items: list[dict]) -> list[dict]:
api/truerate/instagram.py:123:def _when(taken_at: str) -> datetime:
api/truerate/instagram.py:127:class Hiker:
api/truerate/instagram.py:160:    def profile(self, username: str) -> dict:
api/truerate/instagram.py:163:    def about(self, pk: str) -> dict:
api/truerate/instagram.py:166:    def reels(self, pk: str, pages: int = 3, on_page=None, back_to: datetime | None = None) -> list[dict]:
api/truerate/instagram.py:184:    def comments(self, media_id: str) -> list[dict]:
api/truerate/instagram.py:187:    def likers(self, media_id: str, n: int = 200) -> list[dict]:
api/truerate/instagram.py:195:    def followers(self, pk: str) -> list[dict]:
api/truerate/instagram.py:198:    def tagged(self, pk: str) -> list[dict]:
api/truerate/instagram.py:201:    def suggested(self, pk: str) -> list[dict]:
api/truerate/instagram.py:205:def collect(hiker: Hiker, handle: str, comment_reels: int = 10, liker_reels: int = 3, workers: int = 1, back_to: datetime | None = None) -> dict:
api/truerate/instagram.py:246:def _or_empty(fetch, key: str, empty=None):
api/truerate/instagram.py:257:def fetch_covers(reels: list[dict], limit: int = 6) -> dict[str, bytes]:
api/truerate/instagram.py:259:    def one(http, r):
api/truerate/llm.py:10:class Gemini:
api/truerate/llm.py:18:    def json(self, prompt: str, schema: dict, images: list[bytes] = (), audio: list[bytes] = ()) -> dict:
api/truerate/llm.py:33:    def search(self, prompt: str) -> dict:
api/truerate/outputs.py:21:def _views(n: float) -> str:
api/truerate/outputs.py:29:def _sentence(parts: list[str]) -> str:
api/truerate/outputs.py:34:def outputs(r: dict, inputs: dict) -> list[dict]:
api/truerate/outputs.py:40:    def add(key: str, status: str, title: str, detail: str = "") -> None:
api/truerate/pipeline.py:48:class Deps:
api/truerate/pipeline.py:60:def when(days: int) -> str:
api/truerate/pipeline.py:64:def _flag_text(f: dict, s: dict) -> str:
api/truerate/pipeline.py:79:def _brand(reel: dict, handle: str) -> str | None:
api/truerate/pipeline.py:85:def _days_ago(iso: str) -> int:
api/truerate/pipeline.py:89:def _safe_web_rate(llm, handle: str, full_name: str, followers: int, category: str) -> dict | None:
api/truerate/pipeline.py:97:def analyze(handle: str, inputs: dict, deps: Deps, step: Callable[[int], None] = lambda i: None) -> dict:
api/truerate/pipeline.py:156:    def kind(r):
api/truerate/pipeline.py:237:def _decide(v, flags, p, inputs, metrics, typical, fit, fit_share, competitor) -> dict:
api/truerate/pipeline.py:267:def _negotiation(p: dict, flags: list[dict], metrics: dict, category: str) -> dict:
api/truerate/pipeline.py:276:def check_quote(r: dict, quote: int) -> dict:
api/truerate/pricing.py:21:def _group(n: float) -> str:
api/truerate/pricing.py:30:def inr(n: float) -> str:
api/truerate/pricing.py:34:def round500(x: float) -> int:
api/truerate/pricing.py:38:def features(m: dict) -> list[float]:
api/truerate/pricing.py:47:def _num(x) -> float:
api/truerate/pricing.py:51:def _log(x) -> float:
api/truerate/pricing.py:55:def features_v2(m: dict) -> list[float]:
api/truerate/pricing.py:69:def likely_band(fair: float, low: float, high: float) -> tuple[int, int]:
api/truerate/pricing.py:75:def per_1k(row: dict) -> float:
api/truerate/pricing.py:80:class Core:
api/truerate/pricing.py:89:    def fit(cls, rows: list[dict]) -> "Core":
api/truerate/pricing.py:96:    def predict_logs(self, m: dict) -> tuple[float, float, list[dict]]:
api/truerate/pricing.py:109:def boosting_regressor():
api/truerate/pricing.py:117:def paid_typical_of(rows: list[dict]) -> float:
api/truerate/pricing.py:122:def boosted_logs(train: list[dict], test: list[dict]) -> np.ndarray:
api/truerate/pricing.py:129:def split_offsets(resid: np.ndarray, level: float) -> tuple[float, float]:
api/truerate/pricing.py:135:def _positions(rows: list[dict]) -> np.ndarray:
api/truerate/pricing.py:139:def local_spread(train_pos: np.ndarray, abs_resid: np.ndarray, target_pos: np.ndarray, leave_out_self: bool = False) -> np.ndarray:
api/truerate/pricing.py:151:class Boosted:
api/truerate/pricing.py:165:    def fit(cls, rows: list[dict], ranges: bool = True, local: bool = False) -> "Boosted":
api/truerate/pricing.py:178:    def log_price(self, m: dict) -> float:
api/truerate/pricing.py:181:    def spread(self, m: dict) -> float:
api/truerate/pricing.py:186:class PriceModel:
api/truerate/pricing.py:196:    def rows(self) -> list[dict]:
api/truerate/pricing.py:200:def fit(rows: list[dict], blend: tuple[float, float, float] | None = None, method: str = "ridge", ranges: bool = True,
api/truerate/pricing.py:238:def market_discount(rows: list[dict]) -> float:
api/truerate/pricing.py:250:def market_reference(followers: int) -> dict:
api/truerate/pricing.py:255:def collab_factor(n: int, ratio: float | None, typical: float, prior: float | None = None) -> tuple[float, float]:
api/truerate/pricing.py:265:def price(model: PriceModel, m: dict, genuine_share: float = 1.0) -> dict:
api/truerate/pricing.py:340:def band_median_price(rows: list[dict], followers: int) -> float:
api/truerate/pricing.py:345:def modash_price(rows: list[dict], m: dict) -> float:
api/truerate/pricing.py:353:def _summary(errors: list[dict], method: str) -> dict:
api/truerate/pricing.py:368:def validate(rows: list[dict], method: str = "ridge") -> dict:
api/truerate/pricing.py:373:    def errors(r: dict, m: PriceModel, others: list[dict]) -> dict:
api/truerate/pricing.py:412:def rate_card(model: PriceModel) -> list[dict]:
api/truerate/pricing.py:425:def thin_categories(model: PriceModel) -> list[dict]:
api/truerate/signals.py:17:def _digit_ratio(text: str) -> float:
api/truerate/signals.py:21:def account_features(acc: dict) -> list[float]:
api/truerate/signals.py:34:def load_kaggle(path: Path) -> tuple[list[list[float]], list[int]]:
api/truerate/signals.py:39:def train_fake_model(X: list[list[float]], y: list[int]) -> RandomForestClassifier:
api/truerate/signals.py:43:def fake_share(model: RandomForestClassifier, accounts: list[dict]) -> float | None:
api/truerate/signals.py:76:def category_from_niche(genres: list[str]) -> str | None:
api/truerate/signals.py:85:def is_paid(reel: dict) -> bool:
api/truerate/signals.py:89:def recent_reels(snapshot: dict) -> list[dict]:
api/truerate/signals.py:94:def reel_metrics(snapshot: dict, labels: dict | None = None) -> dict:
api/truerate/signals.py:100:    def paid_reel(r):
api/truerate/signals.py:114:    def ratio(group):
api/truerate/signals.py:142:def niche_vector(snapshot: dict, embed) -> np.ndarray:
api/truerate/signals.py:150:def fit_niche_model(X: np.ndarray, y: list[str]):
api/truerate/signals.py:161:def extra_features(snap: dict) -> dict:
api/truerate/signals.py:184:def english_share(mix: dict | None) -> float | None:
api/truerate/signals.py:194:def deal_window_metrics(snapshot: dict, paid_on: datetime) -> dict:
api/truerate/signals.py:216:def label_niche(llm, bio: str, captions: list[str]) -> str:
api/truerate/signals.py:224:def band(followers: int) -> str:
api/truerate/signals.py:229:def _minilm():
api/truerate/signals.py:235:def minilm_embed(texts: list[str]) -> np.ndarray:
api/truerate/signals.py:247:def comment_signals(comments_by_reel: dict[str, list[dict]], embed) -> dict:
api/truerate/signals.py:269:def _cv(values: list[float]) -> float | None:
api/truerate/signals.py:274:def audience_signals(snapshot: dict, metrics: dict, fake_model, embed) -> dict:
api/truerate/signals.py:308:def _scale(value: float, log: bool) -> float:
api/truerate/signals.py:312:def band_norms(rows: list[dict]) -> dict:
api/truerate/signals.py:330:def verdict(signals: dict, norms: dict) -> dict:
api/truerate/signals.py:346:def genuine_share(signals: dict, norms: dict) -> float:
api/truerate/signals.py:363:def _bot(rng) -> dict:
api/truerate/signals.py:368:def make_fake(snapshot: dict, kind: str, rng) -> dict:
api/truerate/signals.py:404:def redteam(snapshots: list[dict], fake_model, embed, seed: int = 7) -> dict:
api/truerate/signals.py:409:    def signals(snap):
api/truerate/signals.py:430:def ambiguous(reel: dict) -> bool:
api/truerate/signals.py:435:def top_commenters(comments_by_reel: dict[str, list[dict]], n: int = 15) -> list[dict]:
api/truerate/signals.py:460:def label_creator(llm, snapshot: dict, images: dict[str, bytes]) -> dict:
api/truerate/signals.py:493:def commenter_mix(snapshot: dict, fake_model, labels: dict) -> dict:
api/truerate/signals.py:516:def _model(url: str):
api/truerate/signals.py:529:def _face_detector():
api/truerate/signals.py:537:def _person_detector():
api/truerate/signals.py:544:def has_face(image: bytes) -> bool:
api/truerate/signals.py:555:def face_share(covers: dict[str, bytes], detect=has_face) -> float | None:
api/truerate/signals.py:565:def commenter_rings(commenters_by_creator: dict[str, set[str]]) -> dict[str, int]:
api/truerate/signals.py:584:def _anomaly_row(signals: dict, typical: dict) -> list[float]:
api/truerate/signals.py:589:def fit_anomaly(rows: list[dict]):
api/truerate/signals.py:599:def audience_warnings(signals: dict, forest) -> list[str]:
api/truerate/signals.py:612:def spoken_candidates(reels: list[dict], n: int = SPOKEN_REELS) -> list[dict]:
api/truerate/signals.py:628:def label_spoken(llm, clips: dict[str, bytes]) -> dict[str, dict]:
api/truerate/webcheck.py:15:def _field(text: str, name: str) -> str:
api/truerate/webcheck.py:20:def _rupees(value: str) -> int | None:
api/truerate/webcheck.py:25:def web_rate(llm, handle: str, full_name: str, followers: int, category: str) -> dict:
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
web/src/app/(app)/batch/page.tsx:16:export default function BatchPage() {
web/src/app/(app)/brand/[id]/brand-view.tsx:10:export default function BrandView({ params }: { params: Promise<{ id: string }> }) {
web/src/app/(app)/brand/[id]/page.tsx:6:export default function BrandResultPage({ params }: PageProps<"/brand/[id]">) {
web/src/app/(app)/brand/page.tsx:11:export default function BrandPage() {
web/src/app/(app)/layout.tsx:7:export default function AppLayout({ children }: LayoutProps<"/">) {
web/src/app/(app)/nav.tsx:19:export function NavLinks({ path }: { path: string | null }) {
web/src/app/(app)/nav.tsx:35:export default function Nav() {
web/src/app/(app)/page.tsx:12:export default function AnalyzePage() {
web/src/app/(app)/rate-card/page.tsx:16:export default function RateCardPage() {
web/src/app/(app)/sign-out.tsx:7:export default function SignOut() {
web/src/app/layout.tsx:12:export const metadata: Metadata = {
web/src/app/layout.tsx:17:export default function RootLayout({ children }: LayoutProps<"/">) {
web/src/app/login/login-form.tsx:8:export default function LoginForm() {
web/src/app/login/page.tsx:3:export default function LoginPage() {
web/src/components/batch/compare.tsx:48:export function Recommendation({ rows }: { rows: Row[] }) {
web/src/components/batch/compare.tsx:98:export function Scorecard({ rows }: { rows: Row[] }) {
web/src/components/batch/compare.tsx:156:export function PriceChart({ rows, budget }: { rows: Row[]; budget: number | null | undefined }) {
web/src/components/batch/compare.tsx:198:export function ReachChart({ rows }: { rows: Row[] }) {
web/src/components/brand/result.tsx:48:export default function BrandResult({ run }: { run: BrandRun }) {
web/src/components/chart-tip.tsx:5:export default function ChartTip({ lines, children, className = "" }: { lines: React.ReactNode[]; children: React.ReactNode; className?: string }) {
web/src/components/chips.tsx:7:export function CallChip({ call, large = false }: { call: string; large?: boolean }) {
web/src/components/chips.tsx:15:export const VERDICTS = ["Real audience", "Some fake activity", "Mostly fake"] as const;
web/src/components/chips.tsx:16:export const VERDICT_COLOR: Record<string, string> = {
web/src/components/product-options.tsx:4:export default function ProductOptions({ products, categories }: { products: Product[]; categories: string[] }) {
web/src/components/recent-table.tsx:8:export type Column<T> = { label: string; cell: (item: T) => React.ReactNode; className?: string };
web/src/components/recent-table.tsx:11:export function NameHandle({ name, handle }: { name?: string | null; handle: string }) {
web/src/components/recent-table.tsx:24:export default function RecentTable<T extends { id: string }>({ title, items, href, columns, onRemove, removeLabel, empty, className = "" }: {
web/src/components/report/audience.tsx:5:export default function Audience({ r }: { r: Report }) {
web/src/components/report/authenticity.tsx:28:export default function Authenticity({ r }: { r: Report }) {
web/src/components/report/decision.tsx:6:export default function Decision({ r, outputs }: { r: Report; outputs: Output[] }) {
web/src/components/report/engagement.tsx:7:export default function Engagement({ r }: { r: Report }) {
web/src/components/report/evidence.tsx:9:export function CheaperCreators({ r }: { r: Report }) {
web/src/components/report/evidence.tsx:44:export function Suggestions({ r }: { r: Report }) {
web/src/components/report/negotiation.tsx:9:export default function Negotiation({ r }: { r: Report }) {
web/src/components/report/placement.tsx:40:export default function Placement({ r }: { r: Report }) {
web/src/components/report/quote.tsx:11:export default function QuoteChecker({ id, initial }: { id: string; initial: number | null }) {
web/src/components/report/report.tsx:18:export default function ReportView({ id, report: r, inputs, outputs }: { id: string; report: Report; inputs: Analysis["inputs"]; outputs: Output[] }) {
web/src/components/report/waterfall.tsx:24:export default function Waterfall({ r }: { r: Report }) {
web/src/components/tabs.tsx:5:export type Tab = { key: string; label: string; panel: React.ReactNode };
web/src/components/tabs.tsx:15:export default function Tabs({ tabs, label }: { tabs: Tab[]; label: string }) {
web/src/components/value-bars.tsx:4:export type ValueRow = { handle: string; fair: number; views: number; highlight?: boolean; usualPerK?: number | null };
web/src/components/value-bars.tsx:8:export default function ValueBars({ rows, caption }: { rows: ValueRow[]; caption: string }) {
web/src/components/verdicts.tsx:6:export const STATUS = {
web/src/components/verdicts.tsx:13:export function StatusIcon({ status, size = 20 }: { status: Output["status"]; size?: number }) {
web/src/components/verdicts.tsx:19:export default function Verdicts({ outputs }: { outputs: Output[] }) {
web/src/lib/api-types.ts:6:export interface paths {
web/src/lib/api-types.ts:213:export type webhooks = Record<string, never>;
web/src/lib/api-types.ts:214:export interface components {
web/src/lib/api-types.ts:1050:export type $defs = Record<string, never>;
web/src/lib/api-types.ts:1051:export interface operations {
web/src/lib/api.ts:4:export type Analysis = Schemas["Analysis"];
web/src/lib/api.ts:5:export type AnalysisRequest = Schemas["AnalysisRequest"];
web/src/lib/api.ts:6:export type AnalysisSummary = Schemas["AnalysisSummary"];
web/src/lib/api.ts:7:export type Report = Schemas["Report"];
web/src/lib/api.ts:8:export type Meta = Schemas["Meta"];
web/src/lib/api.ts:9:export type QuoteCheck = Schemas["QuoteCheck"];
web/src/lib/api.ts:10:export type Batch = Schemas["Batch"];
web/src/lib/api.ts:11:export type BatchSummary = Schemas["BatchSummary"];
web/src/lib/api.ts:12:export type BatchRequest = Schemas["BatchRequest"];
web/src/lib/api.ts:13:export type RateCard = Schemas["RateCard"];
web/src/lib/api.ts:14:export type ModelReport = Schemas["ModelReport"];
web/src/lib/api.ts:15:export type Product = Schemas["Product"];
web/src/lib/api.ts:16:export type Output = Schemas["Output"];
web/src/lib/api.ts:17:export type BrandRun = Schemas["BrandRun"];
web/src/lib/api.ts:18:export type BrandSummary = Schemas["BrandSummary"];
web/src/lib/api.ts:19:export type BrandRequest = Schemas["BrandRequest"];
web/src/lib/api.ts:35:export const api = {
web/src/lib/format.ts:3:export function inr(n: number): string {
web/src/lib/format.ts:8:export function inrRange(low: number, high: number): string {
web/src/lib/format.ts:16:export function compact(n: number): string {
web/src/lib/format.ts:23:export function pct(x: number, digits = 0): string {
web/src/lib/format.ts:27:export function daysAgo(iso: string): string {
web/src/lib/format.ts:33:export const SESSION_COOKIE = "truerate_session";
web/src/proxy.ts:4:export function proxy(request: NextRequest) {
web/src/proxy.ts:12:export const config = {
```

<!-- mapped: .@06d2adf | paths: api/, web/src/ -->
