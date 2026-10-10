import json

import joblib
import numpy as np
from typer.testing import CliRunner

from truerate import cli
from truerate.pricing import MARKET_SOURCE, band, band_median_price, collab_factor, fit, modash_price, price, rate_card, round500, validate

# Synthetic deals: price = the category's ₹ per 1,000 views × views, with 15% noise.
CAT_PER_1K = {"Tech and gadgets": 1500, "Food": 600, "Entertainment": 1000}


def synthetic_rows(n=90, seed=1):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        category = list(CAT_PER_1K)[i % 3]
        followers = int(10 ** rng.uniform(4.3, 6.3))
        views = int(followers * 10 ** rng.uniform(-0.7, 0.3))
        engagement = float(rng.uniform(0.02, 0.12))
        paid_n = int(rng.integers(0, 4))
        rows.append({
            "handle": f"creator{i}", "category": category, "followers": followers, "views": views, "engagement": engagement,
            "comments_per_1k": float(rng.uniform(0.5, 5)), "likes_per_view": engagement * 0.9, "views_p25": views * 0.7, "views_p75": views * 1.4,
            "paid_n": paid_n, "paid_ratio": 0.6 if paid_n else None, "holdout": i % 6 == 0,
            "price": CAT_PER_1K[category] * views / 1000 * float(np.exp(rng.normal(0, 0.15))),
        })
    return rows


def test_bands_and_rounding():
    assert [band(f) for f in (19_999, 20_000, 99_999, 100_000)] == ["small", "medium", "medium", "big"]
    assert (round500(12_249), round500(12_250), round500(12_800)) == (12_000, 12_500, 13_000)


def test_collab_factor_shrinks_few_ads_toward_the_typical_drop():
    # one ad keeping 20% of views, typical creator keeps 60%: (1×0.2 + 3×0.6) / 4 = 0.5, so 0.5 / 0.6 of the market price
    shrunk, factor = collab_factor(1, 0.2, typical=0.6)
    assert (round(shrunk, 4), round(factor, 4)) == (0.5, 0.8333)
    assert collab_factor(0, None, typical=0.6) == (0.6, 1.0)
    assert collab_factor(30, 0.6, typical=0.6)[1] == 1.0


def test_collab_factor_never_raises_a_price_and_never_more_than_halves_it():
    # Real data: a few viral reels labelled as ads made paid reels look 100x stronger, and prices followed. Past
    # prices already include strong creators, so the factor only discounts weak sponsored reach, down to half.
    assert collab_factor(5, 10.0, typical=0.9) == (0.9, 1.0)
    assert collab_factor(20, 0.05, typical=0.9) == (0.45, 0.5)


def test_baselines():
    rows = [{"followers": 50_000, "price": p, "views": 20_000, "engagement": e} for p, e in [(10_000, 0.04), (20_000, 0.05), (30_000, 0.06)]]
    assert band_median_price(rows, 60_000) == 20_000
    # ₹1,000 per 1,000 views; above the band's median engagement is +25%; 1M+ followers doubles
    assert modash_price(rows, {"followers": 50_000, "views": 40_000, "engagement": 0.08}) == 50_000
    assert modash_price(rows, {"followers": 1_500_000, "views": 40_000, "engagement": 0.01}) == 60_000


def test_price_has_a_range_waterfall_comparables_and_delivery():
    rows = synthetic_rows()
    model = fit([r for r in rows if not r["holdout"]])
    target = rows[0] | {"paid_n": 2, "paid_ratio": 0.3}
    p = price(model, target, genuine_share=0.8)
    assert p["low"] < p["fair"] < p["high"] and p["fair"] % 500 == 0
    steps = [s["amount"] for s in p["waterfall"]]
    assert steps[0] == p["market"] and sum(steps[:3]) == steps[3] == p["fair"]
    assert steps[1] < 0 and steps[2] < 0  # weak ads and fake engagement both cut the price
    assert len(p["comparables"]) == 6 and {"handle", "price", "views", "per_1k_views"} <= set(p["comparables"][0])
    assert p["ridge_share"] == model.w  # the report says how much of the market price is the regression
    d = p["delivery"]
    assert d["views"][0] < d["views"][1] < d["views"][2] and d["likes"] > 0 and d["cost_per_1k"] > 0 and d["category_cost_per_1k"] > 0


def test_validate_beats_both_baselines_on_synthetic_deals():
    report = validate(synthetic_rows())
    h = report["holdout"]
    assert h["n"] == 15
    assert h["model"]["median_error"] < 0.2
    assert h["model"]["median_error"] < h["band_median"]["median_error"] and h["model"]["median_error"] < h["modash"]["median_error"]
    assert set(report["by_category"]) == set(CAT_PER_1K) and report["by_category"]["Food"]["n"] == 30
    pts = h["points"]  # predicted vs actual for the About chart, without handles
    assert len(pts) == 15 and set(pts[0]) == {"actual", "predicted", "band"}
    assert "creator" not in json.dumps(report)  # no handles, so the report can go in the pitch


def test_range_covers_most_held_out_prices():
    # A 10th-90th percentile range should hold about 80%. 15 held-out deals swing too much by chance, so pool 4 synthetic sets.
    held = [validate(synthetic_rows(seed=s))["holdout"] for s in (1, 2, 3, 4)]
    assert sum(h["coverage"] * h["n"] for h in held) / sum(h["n"] for h in held) >= 0.7


def test_validate_command_saves_model_and_report(db, tmp_path, monkeypatch):
    for r in synthetic_rows():
        db.deals.insert_one({"handle": r["handle"], "tier": band(r["followers"]), "niche": [], "price": r["price"], "holdout": r["holdout"]})
        db.metrics.insert_one({"_id": r["handle"], **{k: v for k, v in r.items() if k not in ("handle", "price", "holdout")}})
    monkeypatch.setattr(cli, "get_db", lambda: db)
    result = CliRunner().invoke(cli.app, ["validate", "--out-dir", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Holdout (15 creators) median error: model" in result.output
    assert json.loads((tmp_path / "model_report.json").read_text())["holdout"]["n"] == 15
    served = joblib.load(tmp_path / "price.joblib")
    assert len(served.rows) == 90  # served model learns from every deal once validation is done


def test_rate_card_per_category():
    card = rate_card(fit(synthetic_rows()))
    assert [c["category"] for c in card][0] == "Tech and gadgets"  # most expensive views first
    food = next(c for c in card if c["category"] == "Food")
    assert food["n"] == 30 and 500 < food["per_1k"]["median"] < 700
    assert food["per_1k"]["p25"] <= food["per_1k"]["median"] <= food["per_1k"]["p75"] and food["typical_price"] > 0


def test_a_creator_bigger_than_any_wldd_deal_gets_a_note():
    rows = synthetic_rows()
    model = fit([r for r in rows if not r["holdout"]])
    big = rows[0] | {"followers": max(r["followers"] for r in rows) * 10, "views": max(r["views"] for r in rows) * 10}
    assert "Bigger than any creator WLDD has booked" in price(model, big)["note"]
    assert price(model, rows[0])["note"] is None


def test_rate_card_leaves_out_categories_with_fewer_than_3_deals():
    rows = synthetic_rows() + [synthetic_rows(n=3, seed=9)[0] | {"category": "Fitness", "handle": "only.one"}]
    assert "Fitness" not in {c["category"] for c in rate_card(fit(rows))}


def test_every_price_carries_the_published_asking_range_for_its_size():
    model = fit(synthetic_rows())
    p = price(model, synthetic_rows()[0] | {"followers": 50_000})
    assert p["market_reference"] == {"tier": "Micro (10K to 1L followers)", "low": 8_000, "high": 75_000, "source": MARKET_SOURCE}
    assert price(model, synthetic_rows()[0] | {"followers": 3_000_000})["market_reference"]["low"] == 6_00_000


def test_beyond_wldds_largest_creator_the_range_widens_and_reaches_the_market():
    rows = synthetic_rows()
    model = fit(rows)
    top = max(r["followers"] for r in rows)
    inside = price(model, rows[0])
    big = price(model, rows[0] | {"followers": top * 8, "views": rows[0]["views"] * 8})
    # A bigger creator is likely to ask more, not less: only the top of the range widens (a mega creator at ₹6,000 is nonsense)
    assert big["high"] / big["fair"] > inside["high"] / inside["fair"]
    assert abs(big["fair"] / big["low"] - inside["fair"] / inside["low"]) < 0.25
    assert big["high"] >= big["market_reference"]["low"]
    assert "published rate cards" in big["note"]


def test_below_wldds_smallest_creator_only_the_bottom_widens():
    rows = synthetic_rows()
    model = fit(rows)
    least = min(r["followers"] for r in rows)
    inside = price(model, rows[0])
    tiny = price(model, rows[0] | {"followers": least // 8})
    assert tiny["fair"] / tiny["low"] > inside["fair"] / inside["low"] and "Smaller than any creator" in tiny["note"]
