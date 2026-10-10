from datetime import datetime, timezone

import httpx
from test_pipeline import TopicLLM, deps, target_snapshot, world  # noqa: F401 (world is a fixture)
from test_pricing import synthetic_rows

from truerate.brand import BrandDeps, brand_partners, budget_plan, candidates, parse_brand, profile_brand, run_brand, score, site_text
from truerate.pipeline import analyze
from truerate.pricing import fit

PROFILE = {"name": "Some Brand", "category": "Food", "product": "Packaged food and snacks", "audience": "young snack lovers", "tone": "fun",
           "price_tier": "mid", "rivals": []}
BRAND_DATA = {
    "profile": {"username": "somebrand", "full_name": "Some Brand", "bio": "Home-style snacks", "category": "Food & beverage", "followers": 50_000, "external_url": ""},
    "reels": [{"caption": "new masala chips with @newcreator", "coauthors": ["newcreator"], "tags": ["somebrand"]}],
    "tagged": [{"owner": "fan.creator", "caption": "loving these chips"}],
}


class BrandLLM(TopicLLM):
    """TopicLLM that answers the brand-profile call with PROFILE and records every prompt."""

    def json(self, prompt, schema, images=(), audio=()):
        if "price_tier" in schema["properties"]:
            self.prompts.append(prompt)
            return PROFILE
        return super().json(prompt, schema, images, audio)


def test_parse_brand_tells_handles_websites_and_names_apart():
    assert parse_brand("@boat.nirvana") == {"kind": "instagram", "value": "boat.nirvana"}
    assert parse_brand("https://www.instagram.com/mamaearth.in/") == {"kind": "instagram", "value": "mamaearth.in"}
    assert parse_brand("mamaearth") == {"kind": "instagram", "value": "mamaearth"}
    assert parse_brand("https://mamaearth.in/products") == {"kind": "website", "value": "https://mamaearth.in/products"}
    assert parse_brand("boat-lifestyle.com") == {"kind": "website", "value": "https://boat-lifestyle.com"}
    assert parse_brand("Sleepy Owl Coffee") == {"kind": "name", "value": "Sleepy Owl Coffee"}


def test_site_text_keeps_the_words_and_drops_the_code():
    html = ("<html><head><title>Sleepy Owl</title><meta name='description' content='Cold brew coffee'><style>.a{color:red}</style></head>"
            "<body><script>var tracking = 1</script><h1>Brew better</h1><p>Coffee   for busy people</p></body></html>")
    http = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, text=html)))
    text = site_text(http, "https://sleepyowl.co")
    assert "Sleepy Owl" in text and "Cold brew coffee" in text and "Brew better Coffee for busy people" in text
    assert "tracking" not in text and "color:red" not in text


def test_the_brand_profile_comes_from_the_brands_own_words():
    llm = BrandLLM()
    assert profile_brand(llm, "Instagram bio: Home-style snacks") == PROFILE
    assert "Home-style snacks" in llm.prompts[0]


def test_partners_are_the_creators_seen_with_the_brand_but_never_the_brand_itself():
    assert brand_partners(BRAND_DATA) == ["fan.creator", "newcreator"]


def creator(**changes) -> dict:
    c = {"handle": "x", "sources": ["WLDD booked"], "category": "Food", "topic_share": None, "verdict": "Real audience", "fair": 30_000,
         "likely_low": 17_500, "likely_high": 52_000, "cost_per_1k": 300, "category_cost_per_1k": 400, "expected_views": 1_00_000, "hits_last_10": 8}
    return c | changes


def test_scoring_puts_a_fitting_real_good_value_creator_first_and_says_why():
    brand = PROFILE
    best = score(creator(), brand, 50_000)
    misfit = score(creator(category="Tech and gadgets", topic_share=0.0), brand, 50_000)
    fake = score(creator(verdict="Mostly fake"), brand, 50_000)
    pricey = score(creator(fair=90_000, likely_low=60_000), brand, 50_000)
    assert best["score"] > max(misfit["score"], fake["score"], pricey["score"])
    assert "Makes Food content" in best["reasons"] and "Real audience" in best["reasons"] and "Fits your budget" in best["reasons"]
    assert {a["key"]: a["status"] for a in pricey["answers"]}["budget"] == "bad"
    assert score(creator(sources=["Analysed before", "Worked with the brand"]), brand, None)["score"] > score(creator(), brand, None)["score"]


def test_budget_plan_picks_the_most_views_that_fit_the_budget():
    cs = [{"handle": "a", "fair": 50_000, "expected_views": 1_00_000}, {"handle": "b", "fair": 30_000, "expected_views": 70_000},
          {"handle": "c", "fair": 30_000, "expected_views": 65_000}, {"handle": "d", "fair": 80_000, "expected_views": 1_20_000}]
    assert budget_plan(cs, 60_000) == {"handles": ["b", "c"], "cost": 60_000, "views": 1_35_000}  # two cheaper creators beat the single best
    assert budget_plan(cs, 10_000) == {"handles": [], "cost": 0, "views": 0}


def test_the_pool_labels_where_each_creator_came_from(world):
    model = fit(synthetic_rows())
    r = analyze("newcreator", {}, deps(world, target_snapshot()))["result"]
    world.analyses.insert_one({"_id": "a1", "handle": "newcreator", "status": "done", "result": r, "inputs": {}, "created_at": datetime.now(timezone.utc)})
    by = {c["handle"]: c for c in candidates(world, model, "somebrand", ["newcreator", "unknown.creator"])}
    assert by["creator0"]["sources"] == ["WLDD booked"] and by["creator0"]["fair"] > 0 and by["creator0"]["verdict"]
    assert by["newcreator"]["sources"] == ["Analysed before", "Worked with the brand"] and by["newcreator"]["fair"] == r["price"]["fair"]
    assert by["unknown.creator"]["sources"] == ["Worked with the brand"] and by["unknown.creator"]["fair"] is None  # not analysed yet
    assert "somebrand" not in by


def test_a_brand_run_profiles_ranks_plans_and_lists_who_to_price_next(world):
    llm = BrandLLM()
    steps = []
    out = run_brand(BrandDeps(db=world, llm=llm, price_model=fit(synthetic_rows()), fetch_instagram=lambda handle: BRAND_DATA, fetch_site=lambda url: ""),
                    {"brand": "@somebrand", "budget": 1_00_000, "count": 5}, steps.append)
    assert steps == [0, 1, 2, 3] and out["brand"]["category"] == "Food" and out["brand"]["handle"] == "somebrand"
    picks = out["picks"]
    assert len(picks) == 5 and [p["score"] for p in picks] == sorted((p["score"] for p in picks), reverse=True) and all(p["reasons"] for p in picks)
    assert out["plan"]["cost"] <= 1_00_000 and set(out["plan"]["handles"]) <= {p["handle"] for p in picks}
    # The plan books no one with a clear problem: a weak fit, a fake audience or reels that mostly flop.
    by = {p["handle"]: p for p in picks}
    assert not any(a["status"] == "bad" and a["key"] in ("fit", "audience", "consistency") for h in out["plan"]["handles"] for a in by[h]["answers"])
    assert out["to_price"] == ["fan.creator", "newcreator"]  # seen with the brand, not analysed yet
    deal_prices = {f"{round(row['price'])}" for row in synthetic_rows()}
    assert not any(p in prompt for prompt in llm.prompts for p in deal_prices)


def test_a_brand_on_instagram_costs_three_requests(tmp_path):
    from test_instagram import fake_hiker

    from truerate.brand import instagram_brand

    calls = []
    data = instagram_brand(fake_hiker(tmp_path, calls), "komalpandeyofficial")
    assert data["profile"]["username"] == "komalpandeyofficial" and data["reels"] and isinstance(data["tagged"], list)
    assert len(calls) == 3  # profile, one page of reels, posts that tag the brand


def test_the_plan_never_books_a_creator_with_a_clear_problem():
    from truerate.brand import bookable

    ok = {"handle": "ok", "answers": [{"key": "consistency", "status": "warn"}]}
    flops = {"handle": "flops", "answers": [{"key": "consistency", "status": "bad"}]}
    fake = {"handle": "fake", "answers": [{"key": "audience", "status": "bad"}]}
    misfit = {"handle": "misfit", "answers": [{"key": "fit", "status": "bad"}]}
    pricey = {"handle": "pricey", "answers": [{"key": "budget", "status": "bad"}]}  # the plan's own price check handles this one
    assert [c["handle"] for c in bookable([ok, flops, fake, misfit, pricey])] == ["ok", "pricey"]
