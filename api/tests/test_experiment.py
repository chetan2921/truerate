import json
import math
import re
from datetime import datetime, timezone

import numpy as np
import pytest
from test_pipeline import deps, target_snapshot, world  # noqa: F401 (world is a fixture)
from test_pricing import synthetic_rows

from truerate.experiment import conformal_offsets, coverage_by_width, extra_features, fresh_rows, importance, learning_curve, predict, report_table, run
from truerate.pipeline import analyze
from truerate.pricing import fit, price


def test_extra_features_read_account_age_reel_length_posting_rate_and_contact():
    snap = target_snapshot()  # 30 reels of 30 s, one a day from 1 to 30 September
    snap["fetched_at"] = datetime(2026, 10, 1, tzinfo=timezone.utc)
    snap["data"]["about"] = {"joined": "October 2020", "country": "", "former_usernames": 0}
    snap["data"]["profile"] |= {"external_url": "https://www.youtube.com/@cook", "bio": "Home cooking. Collabs: team@agency.in", "is_verified": True}
    x = extra_features(snap)
    assert round(x["age_years"], 1) == 6.0 and x["reel_seconds"] == 30 and round(x["reels_per_month"]) == 31
    assert (x["youtube"], x["email"], x["verified"]) == (True, True, True)
    snap["data"]["about"] = {"joined": "", "country": "", "former_usernames": 0}
    snap["data"]["profile"] |= {"external_url": "https://linktr.ee/cook", "bio": "Home cooking", "is_verified": False}
    x = extra_features(snap)
    assert x["age_years"] is None and (x["youtube"], x["email"], x["verified"]) == (False, False, False)


def test_ranges_hold_close_to_their_stated_share_of_unseen_prices():
    in80, in50 = [], []
    for seed in range(4):
        out = predict("ridge_v2", "global", synthetic_rows(90, seed), test := synthetic_rows(60, seed + 100))
        in80 += [o["low80"] <= r["price"] <= o["high80"] for o, r in zip(out, test)]
        in50 += [o["low50"] <= r["price"] <= o["high50"] for o, r in zip(out, test)]
    assert 0.7 <= np.mean(in80) <= 0.9 and 0.38 <= np.mean(in50) <= 0.62


def test_ranges_by_follower_band_are_narrower_where_similar_deals_agree():
    rng = np.random.default_rng(3)
    rows = synthetic_rows(160, 3)
    for r in rows:  # medium creators' prices agree; big creators' prices are all over the place
        r["price"] *= math.exp(rng.normal(0, 0.05 if r["followers"] < 100_000 else 0.8))
    width = {b: hi - lo for b, (lo, hi) in ((b, o[0.8]) for b, o in conformal_offsets(rows, "ridge_v2", by_band=True).items())}
    lo, hi = conformal_offsets(rows, "ridge_v2", by_band=False)["all"][0.8]
    assert width["medium"] < hi - lo < width["big"]


def _sets(seed=7):
    rows = synthetic_rows(60, seed)
    fresh = [r | {"handle": f"fresh{i}", "holdout": False} for i, r in enumerate(synthetic_rows(12, seed + 1))]
    return [r for r in rows if not r["holdout"]], [r for r in rows if r["holdout"]], fresh


def test_the_pick_never_looks_at_held_out_or_fresh_prices():
    train, holdout, fresh = _sets()
    small = {"repeats": 1, "folds": 3, "points": ("today", "ridge_v2", "elasticnet_v2")}
    a = run(train, holdout, fresh, **small)
    b = run(train, [r | {"price": r["price"] * 7} for r in holdout], [r | {"price": r["price"] / 5} for r in fresh], **small)
    assert a["picked"] == b["picked"] and a["cv"] == b["cv"]
    assert a["holdout"] != b["holdout"] and a["fresh"] != b["fresh"]  # the scramble did reach the test scores
    assert a["picked"]["price"] in small["points"] and ("/" in a["picked"]["range"] or a["picked"]["range"] == "today_served")
    assert not re.search(r"(creator|fresh)\d", json.dumps(a))  # no handles in what gets written
    table = report_table(a)
    assert all(f"| {name} " in table for name in a["cv"]) and "today_served" in table.split("\n| ")[2]  # today first, after the header
    assert ("Adopted: yes" in table) == a["adopt"] and not re.search(r"(creator|fresh)\d", table)
    assert "| Width (high ÷ low) | 1.5× | 2× | 3× | 4× | 6× | 8× |" in table and "| Held out |" in table


def test_fresh_rows_rebuild_the_features_a_stored_analysis_was_priced_from(world):
    d = deps(world, target_snapshot(), audio=True)  # the spoken-ad call marks a reel paid that no caption shows
    out = analyze("newcreator", {}, d)["result"]
    world.analyses.insert_one({"_id": "a1", "handle": "newcreator", "status": "done", "result": out, "created_at": datetime.now(timezone.utc)})
    (row,) = fresh_rows(world, {"newcreator": 50_000})
    assert row["price"] == 50_000 and row["paid_n"] >= 1 and row["category"] == out["category"]
    p = price(d.price_model, row, out["price"]["genuine_share"])
    assert (p["fair"], p["low"], p["high"]) == (out["price"]["fair"], out["price"]["low"], out["price"]["high"])


def test_learning_curve_and_importance_have_one_value_per_size_and_feature():
    train, holdout, fresh = _sets()
    curve = learning_curve("ridge_v2", train, holdout + fresh, sizes=(15, 30, len(train)), draws=2)
    assert [c["n"] for c in curve] == [15, 30, len(train)] and all(c["error"] > 0 for c in curve)
    imp = importance("ridge_v2", train)
    assert len(imp) >= 10 and all(v >= 0 for v in imp.values()) and "log views" in imp


def test_tabpfn_uses_the_v2_weights_whose_license_allows_commercial_use():
    pytest.importorskip("tabpfn")  # in the `experiments` dependency group only
    from truerate.experiment import ESTIMATORS, POINTS

    model = ESTIMATORS["tabpfn_v2"]()
    assert "tabpfn_v2" in POINTS and "v2.5" not in str(model.model_path) and "v3" not in str(model.model_path)
    assert str(model.model_path).endswith(".ckpt") and model.device == "cpu"  # runs locally; the cloud client is never used


def test_fresh_deals_are_scored_by_the_model_exactly_as_served():
    # MAPIE's folds follow row order; the served model is fitted on the deals sorted by handle (`training_rows`).
    train, holdout, fresh = _sets()
    a = run(train, holdout, fresh, repeats=1, folds=3, points=("today",))
    served = fit(sorted(train + holdout, key=lambda r: r["handle"]))
    expected = [{"fair": p["fair"], "low80": p["low"], "high80": p["high"]} for p in (price(served, r) for r in fresh)]
    assert [p["before"] for p in a["points"] if p["set"] == "fresh"] == expected


def test_per_creator_ranges_are_narrow_where_similar_deals_agree_and_still_hold_their_level():
    def noisy(n, seed):
        rng = np.random.default_rng(seed)
        rows = synthetic_rows(n, seed)
        for r in rows:  # creators under 1L followers are priced steadily, bigger ones erratically
            r["price"] *= math.exp(rng.normal(0, 0.08 if r["followers"] < 100_000 else 0.9))
        return rows

    steady, wild, held = [], [], []
    for seed in range(3):
        test = noisy(80, seed + 50)
        out = predict("ridge_v2", "local", noisy(160, seed), test)
        held += [o["low80"] <= r["price"] <= o["high80"] for o, r in zip(out, test)]
        for o, r in zip(out, test):
            (steady if r["followers"] < 100_000 else wild).append(o["high80"] / o["low80"])
    assert np.median(steady) < 0.5 * np.median(wild)
    assert 0.7 <= np.mean(held) <= 0.9


def test_coverage_by_width_counts_prices_inside_a_range_of_each_width_around_the_middle():
    test = [{"price": 100.0}, {"price": 100.0}, {"price": 100.0}, {"price": 100.0}]
    preds = [{"fair": 100}, {"fair": 120}, {"fair": 200}, {"fair": 400}]  # off by 1.0x, 1.2x, 2x and 4x
    # A range 2x wide spans the middle ÷1.41 to ×1.41, so it holds the first two; 4x wide (÷2 to ×2) holds three.
    assert coverage_by_width(test, preds, widths=(2, 4, 16)) == {2: 0.5, 4: 0.75, 16: 1.0}


def test_the_ensemble_averages_its_members_in_log_price():
    from truerate.experiment import ENSEMBLE, POINT_FNS

    def with_extras(rows, seed):  # boosting needs the new features to have values, as WLDD's deals do
        rng = np.random.default_rng(seed)
        return [r | {"age_years": rng.uniform(1, 9), "reel_seconds": rng.uniform(10, 90), "reels_per_month": rng.uniform(4, 30), "n_reels": 30,
                     "youtube": bool(rng.integers(2)), "email": bool(rng.integers(2)), "verified": bool(rng.integers(2)), "english": rng.uniform(),
                     "views_cv": rng.uniform(0.3, 2), "trend": rng.uniform(0.5, 1.5)} for r in rows]

    train, test = with_extras(synthetic_rows(60, 3), 1), with_extras(synthetic_rows(10, 4), 2)
    members = np.mean([POINT_FNS[m](train, test) for m in ENSEMBLE], axis=0)
    assert np.allclose(POINT_FNS["ensemble"](train, test), members) and "tabpfn_v2" not in ENSEMBLE  # runs with the servers on


def test_dated_rows_use_the_stats_around_the_payout_where_there_are_any():
    from truerate.experiment import dated

    then = {"views_then": 5000, "engagement_then": 0.07, "comments_per_1k_then": 3.0, "likes_per_view_then": 0.06, "n_then": 9}
    rows = [{"handle": "a", "views": 9000, "engagement": 0.05, "comments_per_1k": 2.0, "likes_per_view": 0.04} | then,
            {"handle": "b", "views": 8000, "engagement": 0.04, "comments_per_1k": 1.0, "likes_per_view": 0.03, "views_then": None, "n_then": 1}]
    a, b = dated(rows)
    assert (a["views"], a["engagement"], a["comments_per_1k"], a["likes_per_view"]) == (5000, 0.07, 3.0, 0.06)
    assert (a["views_today"], b["views"]) == (9000, 8000)  # no reels around the payout: today's stats stand in
    assert rows[0]["views"] == 9000  # the input is left alone


def test_run_scores_one_held_out_set_when_there_are_no_fresh_deals():
    train, holdout, _ = _sets()
    out = run(train, holdout, [], repeats=1, folds=3, points=("today", "ridge_v2"))
    assert out["n"]["fresh"] == 0 and out["fresh"] == {} and "fresh" not in out["coverage_by_width"]
    assert out["holdout"]["today_served"]["n"] == len(holdout)
    assert out["adopt"] == (out["picked"]["range"] != "today_served" and
                            out["holdout"][out["picked"]["range"]]["error"] <= out["holdout"]["today_served"]["error"] and
                            out["holdout"][out["picked"]["range"]]["width80"] <= out["holdout"]["today_served"]["width80"] and
                            (out["holdout"][out["picked"]["range"]]["error"] < out["holdout"]["today_served"]["error"] or
                             out["holdout"][out["picked"]["range"]]["width80"] < out["holdout"]["today_served"]["width80"]) and
                            out["holdout"][out["picked"]["range"]]["coverage80"] >= 0.75)
    assert report_table(out)


def test_live_model_is_scored_on_the_held_out_deals_exactly_as_the_app_prices_them():
    from truerate.experiment import live_scores

    model = fit(synthetic_rows(60, 5))
    test = synthetic_rows(12, 6)
    out = live_scores(model, test)
    expected = [price(model, r) for r in test]
    assert out["n"] == 12 and out["error"] == pytest.approx(float(np.median([abs(p["fair"] - r["price"]) / r["price"] for r, p in zip(test, expected)])))
    assert 0 <= out["coverage80"] <= 1 and out["width80"] > 1
