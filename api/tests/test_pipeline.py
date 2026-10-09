from datetime import datetime, timezone

import numpy as np
import pytest
from test_audience import fake_embed, genuine_snapshot
from test_pricing import synthetic_rows

from truerate.pipeline import Deps, analyze
from truerate.pricing import fit
from truerate.signals import audience_signals, make_fake, reel_metrics, train_fake_model

FAKE_MODEL = train_fake_model([[1, 0, 2, 0, 0, 0]] * 20 + [[0, 0.67, 0, 0, 0, 0]] * 20, [0] * 20 + [1] * 20)


class TopicLLM:
    """Gemini stand-in: every reel is about `topic`, no hidden ads, every account a person, and the niche is `topic`."""

    def __init__(self, topic="Food"):
        self.topic, self.prompts = topic, []

    def json(self, prompt, schema, images=()):
        self.prompts.append(prompt)
        if "category" in schema["properties"]:
            return {"category": self.topic}
        codes = [line.split(" | ")[0] for line in prompt.splitlines() if " | co-authors:" in line]
        return {"reels": [{"code": c, "ad": False, "topic": self.topic} for c in codes], "accounts": [], "languages": [{"language": "English", "share": 1.0}]}


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


def deps(db, snap, llm=None, face=True):
    return Deps(db=db, collect=lambda handle: snap, llm=llm or TopicLLM(), fake_model=FAKE_MODEL, embed=fake_embed,
                price_model=fit(synthetic_rows()), fetch_covers=lambda reels, limit=10: {r["code"]: b"img" for r in reels[:limit]},
                detect_face=lambda img: face)


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
