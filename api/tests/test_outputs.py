from test_pipeline import deps, target_snapshot, world  # noqa: F401 (world is a fixture)

from truerate.outputs import outputs
from truerate.pipeline import analyze


def result(**changes) -> dict:
    """The parts of a stored report the verdicts read: a genuine, reliable creator priced ₹20,000 to ₹60,000."""
    r = {
        "category": "Food",
        "decision": {"call": "Go"},
        "price": {"low": 20_000, "fair": 35_000, "high": 60_000, "likely_low": 25_000, "likely_high": 45_000, "collab_factor": 1.0, "genuine_share": 1.0, "note": None,
                  "delivery": {"views": [60_000, 1_00_000, 1_80_000], "cost_per_1k": 350, "category_cost_per_1k": 500}},
        "audience": {"verdict": "Real audience", "flags": []},
        "engagement": {"percentile": 55},
        "placement": {"hits_last_10": 8, "trend": 1.0, "paid": {"n": 4, "ratio": 0.9, "typical_ratio": 0.9}},
        "niche": {"product": None, "fit": None},
        "competitor": None,
    }
    for path, value in changes.items():
        *keys, last = path.split("__")
        target = r
        for k in keys:
            target = target[k]
        target[last] = value
    return r


def by_key(r: dict, inputs: dict | None = None) -> dict:
    return {o["key"]: o for o in outputs(r, inputs or {})}


def test_a_genuine_good_value_creator_reads_as_plain_answers():
    o = by_key(result())
    assert [o[k]["status"] for k in ("audience", "value", "consistency", "ads")] == ["good"] * 4
    assert o["audience"]["title"] == "Real audience" and o["value"]["title"].startswith("Good value")
    assert o["reach"]["status"] == "info" and "1L views" in o["reach"]["title"]
    assert "quote" not in o and "budget" not in o and "fit" not in o and "competitor" not in o  # nothing asked, nothing said


def test_a_quote_is_judged_against_the_likely_band_first():
    assert by_key(result(), {"quote": 40_000})["quote"]["title"].endswith("is fair")
    # Inside the wide full range but above where most deals land: worth a counter, not a yes.
    pricey = by_key(result(), {"quote": 55_000})["quote"]
    assert pricey["status"] == "warn" and "high side" in pricey["title"] and "₹35,000" in pricey["detail"]
    high = by_key(result(), {"quote": 90_000})["quote"]
    assert high["status"] == "bad" and "too high" in high["title"] and "₹35,000" in high["detail"]
    assert by_key(result(), {"quote": 22_000})["quote"]["status"] == "good" and "bargain" in by_key(result(), {"quote": 15_000})["quote"]["title"]


def test_the_budget_says_whether_the_creator_fits():
    assert by_key(result(), {"budget": 50_000})["budget"]["status"] == "good"
    assert by_key(result(), {"budget": 25_000})["budget"]["status"] == "warn"  # only at the low end of the range
    over = by_key(result(), {"budget": 10_000})["budget"]
    assert over["status"] == "bad" and "₹20,000" in over["detail"]


def test_fake_activity_is_named_in_plain_words_not_numbers():
    flags = [{"signal": "fake_likers", "text": "61% of 600 sampled likers look fake (similar creators: 9%)"}]
    o = by_key(result(audience__verdict="Some fake activity", audience__flags=flags, price__genuine_share=0.7))["audience"]
    assert o["status"] == "warn" and "likers look like bots" in o["detail"] and "%" not in o["detail"]
    assert by_key(result(audience__verdict="Mostly fake"))["audience"]["status"] == "bad"


def test_value_reliability_and_ads_have_three_grades():
    assert by_key(result(price__delivery__cost_per_1k=650))["value"]["status"] == "warn"
    assert by_key(result(price__delivery__cost_per_1k=900))["value"]["status"] == "bad"
    assert by_key(result(placement__hits_last_10=5))["consistency"]["status"] == "warn"
    assert by_key(result(placement__hits_last_10=2))["consistency"]["status"] == "bad"
    assert by_key(result(price__collab_factor=0.8))["ads"]["status"] == "warn"
    assert by_key(result(price__collab_factor=0.5))["ads"]["status"] == "bad"
    assert by_key(result(placement__paid={"n": 0, "ratio": None, "typical_ratio": 0.9}))["ads"]["status"] == "info"


def test_product_fit_and_a_rival_ad_are_answers_too():
    o = by_key(result(niche__product="Skincare", niche__fit="weak", competitor={"brand": "rivalbrand", "days": 3, "category": "Fashion and beauty"}))
    assert o["fit"]["status"] == "bad" and "Skincare" in o["fit"]["title"]
    assert o["competitor"]["status"] == "warn" and "@rivalbrand" in o["competitor"]["title"]


def test_every_finished_analysis_gets_verdicts(world):
    r = analyze("newcreator", {}, deps(world, target_snapshot()))["result"]
    o = outputs(r, {})
    assert {x["status"] for x in o} <= {"good", "warn", "bad", "info"} and {"audience", "reach", "consistency", "ads"} <= {x["key"] for x in o}
