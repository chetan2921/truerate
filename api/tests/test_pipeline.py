import re
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest
from test_audience import fake_embed, genuine_snapshot
from test_pricing import synthetic_rows

from truerate.pipeline import Deps, analyze, check_quote, inr, when
from truerate.instagram import HikerError
from truerate.pricing import fit
from truerate.signals import audience_signals, make_fake, reel_metrics, train_fake_model

FAKE_MODEL = train_fake_model([[1, 0, 2, 0, 0, 0]] * 20 + [[0, 0.67, 0, 0, 0, 0]] * 20, [0] * 20 + [1] * 20)


class TopicLLM:
    """Gemini stand-in: every reel is about `topic`, no hidden ads, every account a person, and the niche is `topic`."""

    def __init__(self, topic="Food"):
        self.topic, self.prompts = topic, []

    def json(self, prompt, schema, images=(), audio=()):
        self.prompts.append(prompt)
        if "category" in schema["properties"]:
            return {"category": self.topic}
        if "quote" in schema["properties"]["reels"]["items"]["properties"]:  # the spoken-ad call: the first clip is an ad
            codes = prompt.split("in this order: ")[1].split(".")[0].split(", ")
            return {"reels": [{"code": c, "ad": i == 0, "brand": "spokenbrand" if i == 0 else "", "quote": "use my code SPOKEN" if i == 0 else ""}
                              for i, c in enumerate(codes)]}
        codes = [line.split(" | ")[0] for line in prompt.splitlines() if " | co-authors:" in line or " | by @" in line]
        accounts = next((line.split(": ", 1)[1].split(", ") for line in prompt.splitlines() if line.startswith("Accounts: ")), [])
        return {"reels": [{"code": c, "ad": False, "topic": self.topic} for c in codes],
                "accounts": [{"username": a, "kind": "brand"} for a in accounts if "brand" in a], "languages": [{"language": "English", "share": 1.0}]}


def target_snapshot(handle="newcreator", seed=99):
    snap = genuine_snapshot(seed, np.random.default_rng(seed))
    snap["handle"], snap["fetched_at"] = handle, datetime.now(timezone.utc)
    snap["data"]["profile"] = {"pk": "1", "username": handle, "full_name": "New Creator", "followers": snap["followers"], "following": 300, "posts": 200,
                               "bio": "Home cooking in Pune", "external_url": "", "category": "", "is_private": False, "is_verified": False, "has_pic": True}
    for r in snap["data"]["reels"]:
        r |= {"thumbnail": "https://example.invalid/t.jpg", "tags": [], "duration": 30, "counts_hidden": False}
    snap["data"]["suggested"] = [{"username": f"similar{i}", "full_name": "", "is_private": False, "is_verified": False, "has_pic": True, "pk": str(i)} for i in range(8)]
    return snap


@pytest.fixture
def world(db):
    """30 believable WLDD creators for the norms and a price model fitted on synthetic deals."""
    rng = np.random.default_rng(5)
    for i in range(30):
        snap = genuine_snapshot(i, rng)
        m = reel_metrics(snap)
        commenters = sorted({c["user"]["username"] for cs in snap["data"]["comments"].values() for c in cs})
        db.metrics.insert_one({"_id": snap["handle"], **m, **audience_signals(snap, m, FAKE_MODEL, fake_embed), "commenters": commenters, "category": "Food"})
    return db


def deps(db, snap, llm=None, face=True, audio=False):
    return Deps(db=db, collect=lambda handle: snap, llm=llm or TopicLLM(), fake_model=FAKE_MODEL, embed=fake_embed,
                price_model=fit(synthetic_rows()), fetch_covers=lambda reels, limit=10: {r["code"]: b"img" for r in reels[:limit]},
                detect_face=lambda img: face, fetch_audio=lambda reels: {r["code"]: b"wav" for r in reels} if audio else {})


def test_a_genuine_creator_gets_go_with_a_full_report(world):
    steps = []
    llm = TopicLLM()
    out = analyze("newcreator", {}, deps(world, target_snapshot(), llm), step=steps.append)
    assert steps == [0, 1, 2, 3] and out["status"] == "done"
    r = out["result"]
    assert r["decision"]["call"] == "Go" and r["decision"]["reasons"]
    assert not any(reason.startswith("Expected") for reason in r["decision"]["reasons"])  # the decision block already says it
    typical = r["placement"]["typical_views"]
    assert all(typical / 2 <= c["views"] <= typical * 2 for c in r["cheaper"])  # alternatives at a similar reach only
    assert r["audience"]["verdict"] == "Real audience" and r["price"]["genuine_share"] == 1.0
    p = r["price"]
    assert p["low"] <= p["fair"] <= p["high"] and len(p["comparables"]) == 6 and {c["category"] for c in p["comparables"]} == {"Food"}
    assert r["category"] == "Food" and r["niche"]["fit"] is None
    assert len(r["placement"]["reels"]) == 30 and {x["kind"] for x in r["placement"]["reels"]} == {"own"}
    assert 0 <= r["engagement"]["percentile"] <= 100 and r["suggested"][:2] == ["similar0", "similar1"]
    assert r["negotiation"]["start"] == p["low"] and r["negotiation"]["walk_away"] == p["high"] and r["negotiation"]["lines"]
    assert world.snapshots.count_documents({"handle": "newcreator"}) == 1
    deal_prices = {f"{round(row['price'])}" for row in synthetic_rows()}
    assert not any(price in prompt for prompt in llm.prompts for price in deal_prices)


def test_bot_likers_stop_a_go_and_say_why(world):
    snap = make_fake(target_snapshot(), "bot_likers", np.random.default_rng(1))
    r = analyze("newcreator", {}, deps(world, snap))["result"]
    assert r["audience"]["verdict"] != "Real audience" and r["decision"]["call"] in ("Negotiate", "Avoid")
    assert any("likers" in reason for reason in r["decision"]["reasons"])
    assert r["price"]["genuine_share"] < 1


def test_a_quote_above_the_range_means_negotiate(world):
    fair = analyze("newcreator", {}, deps(world, target_snapshot()))["result"]["price"]
    r = analyze("newcreator", {"quote": fair["high"] * 2}, deps(world, target_snapshot()))["result"]
    assert r["decision"]["call"] == "Negotiate" and any("above" in reason for reason in r["decision"]["reasons"])


def test_a_product_outside_the_creators_niche_means_avoid(world):
    r = analyze("newcreator", {"category": "Tech and gadgets"}, deps(world, target_snapshot()))["result"]
    assert r["niche"]["fit"] == "weak" and r["decision"]["call"] == "Avoid"
    assert "Tech and gadgets" in r["worth_reaching"]


def test_private_and_faceless_pages_are_out_of_scope(world):
    private = target_snapshot()
    private["data"] = {"profile": private["data"]["profile"] | {"is_private": True}}
    out = analyze("newcreator", {}, deps(world, private))
    assert out["status"] == "out_of_scope" and "private" in out["reason"]
    out = analyze("newcreator", {}, deps(world, target_snapshot(), face=False))
    assert out["status"] == "out_of_scope" and "face" in out["reason"]


def test_quote_check_places_the_quote_and_counters(world):
    r = analyze("newcreator", {}, deps(world, target_snapshot()))["result"]
    p = r["price"]
    high = check_quote(r, p["high"] + 10_000)
    assert high["position"] == "above" and high["difference"] == p["high"] + 10_000 - p["fair"] and high["counter_offer"] == p["fair"]
    assert len(high["talking_points"]) == 3 and all(point.endswith(".") for point in high["talking_points"])
    within = check_quote(r, p["fair"] - 500)
    assert within["position"] == "within" and within["counter_offer"] == p["fair"] - 500  # at or under fair: take it
    below = check_quote(r, max(p["low"] - 1_000, 500))
    assert below["position"] == "below" and below["counter_offer"] == below["quote"]
    # Inside the wide full range but above where most deals land: "high", with a counter at the middle.
    r["price"] |= {"likely_low": p["fair"] - 1_000, "likely_high": p["fair"] + 1_000, "high": p["fair"] + 20_000}
    pricey = check_quote(r, p["fair"] + 5_000)
    assert pricey["position"] == "high" and pricey["counter_offer"] == p["fair"]


def test_a_brand_that_tagged_the_creator_recently_is_a_competitor(world):
    snap = target_snapshot()
    recent = (datetime.now(timezone.utc) - timedelta(days=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
    snap["data"]["tagged"] = [{"code": "TAG1", "taken_at": recent, "owner": "rivalbrand", "caption": "new flavour with our favourite cook", "paid": False}]
    r = analyze("newcreator", {"category": "Food"}, deps(world, snap))["result"]
    # Creators promote brands in their own niche all the time, and TrueRate doesn't know WLDD's client: Negotiate, not Avoid.
    assert r["competitor"]["brand"] == "rivalbrand" and r["competitor"]["days"] == 12 and r["decision"]["call"] == "Negotiate"
    assert any("rivalbrand" in x and "check exclusivity" in x for x in r["decision"]["reasons"])
    assert r["placement"]["brand_tags"][0]["brand"] == "rivalbrand"


def test_money_uses_indian_grouping_and_days_read_naturally():
    assert (inr(150000), inr(28000), inr(12345678), inr(999)) == ("₹1,50,000", "₹28,000", "₹1,23,45,678", "₹999")
    assert (when(0), when(1), when(12)) == ("today", "yesterday", "12 days ago")


def test_reasons_and_lines_use_indian_grouping(world):
    r = analyze("newcreator", {"quote": 1_500_000}, deps(world, target_snapshot()))["result"]
    text = " ".join(r["decision"]["reasons"] + r["negotiation"]["lines"])
    assert "₹15,00,000" in text
    assert not re.search(r"₹\d{3},\d{3}\b|₹\d{1,3},\d{3},\d{3}", text)  # no Western grouping like ₹150,000 or ₹1,500,000


def test_a_handle_instagram_doesnt_know_reads_as_a_plain_sentence(world):
    def missing(handle):
        raise HikerError(404, 'HikerAPI 404 on /v1/user/by/username: {"exc_type":"UserNotFound"}')

    d = deps(world, None)
    d.collect = missing
    out = analyze("no.such.person", {}, d)
    assert out == {"status": "out_of_scope", "reason": "Instagram has no account called @no.such.person. Check the spelling, or paste the profile link."}


def test_a_spoken_ad_makes_the_reel_paid_and_shows_the_quote(world):
    snap = target_snapshot()
    first = sorted(snap["data"]["reels"], key=lambda r: r["taken_at"], reverse=True)[0]["code"]
    r = analyze("newcreator", {}, deps(world, snap, audio=True))["result"]
    assert next(x for x in r["placement"]["reels"] if x["code"] == first)["kind"] == "paid"
    ad = next(a for a in r["placement"]["ads"] if a["code"] == first)
    assert (ad["brand"], ad["spoken"], ad["disclosed"]) == ("spokenbrand", "use my code SPOKEN", False)


def test_the_creators_own_handle_is_never_the_brand(world):
    # Live: "Promoted dollysingh in Fashion and beauty" because her caption tagged her own handle first.
    snap = target_snapshot()
    reel = sorted(snap["data"]["reels"], key=lambda r: r["taken_at"], reverse=True)[0]
    reel["caption"] = "new drop with @newcreator x @realbrand #ad"
    r = analyze("newcreator", {}, deps(world, snap))["result"]
    assert next(a for a in r["placement"]["ads"] if a["code"] == reel["code"])["brand"] == "realbrand"


def test_a_specific_product_is_matched_through_its_pricing_category(world):
    r = analyze("newcreator", {"category": "Recipes and cooking"}, deps(world, target_snapshot()))["result"]
    assert r["niche"]["fit"] == "strong" and r["niche"]["product"] == "Recipes and cooking"
    assert "Recipes and cooking" in r["worth_reaching"] and "Food" in r["worth_reaching"]
    other = analyze("newcreator", {"category": "Skincare"}, deps(world, target_snapshot()))["result"]
    assert other["niche"]["fit"] == "weak" and other["decision"]["call"] == "Avoid"


def test_a_competitor_for_a_specific_product_is_named_by_the_category_it_was_matched_in(world):
    snap = target_snapshot()
    recent = (datetime.now(timezone.utc) - timedelta(days=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
    snap["data"]["tagged"] = [{"code": "TAG1", "taken_at": recent, "owner": "rivalbrand", "caption": "new flavour with our favourite cook", "paid": False}]
    r = analyze("newcreator", {"category": "Beverages"}, deps(world, snap))["result"]
    # The tagged post is labelled Food, not Beverages: say what was matched, not more.
    assert r["competitor"]["category"] == "Food"
    assert any("rivalbrand in Food" in x for x in r["decision"]["reasons"])


def test_a_creator_wldd_has_booked_is_never_turned_away_by_the_cover_check(world):
    # Some booked creators post covers of food or scenery; WLDD's own records say they are face creators.
    world.deals.insert_one({"handle": "newcreator", "tier": "big", "niche": ["Food"], "price": 140_000, "holdout": False})
    out = analyze("newcreator", {}, deps(world, target_snapshot(), face=False))
    assert out["status"] == "done"


def test_a_quote_above_where_most_deals_land_means_negotiate():
    from truerate.pipeline import _decide

    p = {"low": 10_000, "fair": 30_000, "high": 90_000, "likely_low": 17_500, "likely_high": 52_000, "collab_factor": 1.0}
    def call(quote):
        return _decide({"verdict": "Real audience"}, [], p, {"quote": quote}, {"paid_ratio": 1.0}, 1.0, None, None, None)

    assert call(40_000)["call"] == "Go"
    # Inside the wide full range but above where most deals land: worth a counter, not a yes.
    pricey = call(70_000)
    assert pricey["call"] == "Negotiate" and any("most deals" in reason for reason in pricey["reasons"])


def test_the_price_model_gets_the_extra_features_boosting_reads(world, monkeypatch):
    from truerate import pipeline

    seen = {}
    real = pipeline.price

    def spy(model, m, genuine_share=1.0):
        seen.update(m)
        return real(model, m, genuine_share)

    monkeypatch.setattr(pipeline, "price", spy)
    out = analyze("newcreator", {}, deps(world, target_snapshot()))
    assert out["status"] == "done"
    for key in ("age_years", "reel_seconds", "reels_per_month", "youtube", "email", "verified", "english", "views_cv", "trend", "likes_per_view", "n_reels"):
        assert key in seen, key
    assert seen["reel_seconds"] == 30 and seen["verified"] is False  # from the snapshot the analysis read
