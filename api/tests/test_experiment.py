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
