import numpy as np
from test_pipeline import TopicLLM, deps, target_snapshot, world  # noqa: F401 (world is a fixture)
from test_pricing import synthetic_rows

from truerate.pipeline import analyze
from truerate.webcheck import web_rate


class SearchLLM(TopicLLM):
    """TopicLLM that also answers a web search with a fixed reply and records each search prompt."""

    def __init__(self, reply: str, sources=({"title": "example.in", "url": "https://example.in/rates"},)):
        super().__init__()
        self.reply, self.sources, self.searches = reply, list(sources), []

    def search(self, prompt):
        self.searches.append(prompt)
        return {"text": self.reply, "sources": self.sources}


FOUND = "FOUND: yes\nLOW_INR: 250000\nHIGH_INR: 400000\nSUMMARY: An agency listing quotes 2.5 to 4 lakh per reel."


def test_a_stated_rate_is_read_with_its_sources():
    out = web_rate(SearchLLM(FOUND), "bigcreator", "Big Creator", 2_100_000, "Tech and gadgets")
    assert out == {"found": True, "low": 250_000, "high": 400_000, "summary": "An agency listing quotes 2.5 to 4 lakh per reel.",
                   "sources": [{"title": "example.in", "url": "https://example.in/rates"}]}


def test_nothing_found_or_a_garbled_reply_says_so_instead_of_inventing_a_price():
    none = web_rate(SearchLLM("FOUND: no\nLOW_INR: none\nHIGH_INR: none\nSUMMARY: Nothing published."), "bigcreator", "", 2_100_000, "Food")
    assert none["found"] is False and none["low"] is None and none["summary"] == "Nothing published."
    garbled = web_rate(SearchLLM("FOUND: yes\nLOW_INR: lots\nHIGH_INR: 3\nSUMMARY: ?"), "bigcreator", "", 2_100_000, "Food")
    assert garbled["found"] is False and garbled["low"] is None  # unreadable or impossible figures are not a price
    unsourced = web_rate(SearchLLM(FOUND, sources=()), "bigcreator", "", 2_100_000, "Food")
    assert unsourced["found"] is False  # a figure with no source behind it is not shown as found


def test_only_creators_bigger_than_wldds_largest_get_a_web_check_and_it_never_sees_a_deal_price(world):
    small = SearchLLM(FOUND)
    analyze("newcreator", {}, deps(world, target_snapshot(), small))
    assert small.searches == []
    big_snap = target_snapshot()
    big_snap["followers"] = big_snap["data"]["profile"]["followers"] = max(r["followers"] for r in synthetic_rows()) * 3
    big = SearchLLM(FOUND)
    r = analyze("newcreator", {}, deps(world, big_snap, big))["result"]
    assert len(big.searches) == 1 and r["web_rate"]["found"] and r["web_rate"]["low"] == 250_000
    deal_prices = {f"{round(row['price'])}" for row in synthetic_rows()}
    assert not any(p in big.searches[0] for p in deal_prices) and "@newcreator" in big.searches[0]


def test_a_failed_web_check_never_fails_the_analysis(world):
    class Broken(SearchLLM):
        def search(self, prompt):
            raise RuntimeError("search is down")

    snap = target_snapshot()
    snap["followers"] = snap["data"]["profile"]["followers"] = max(r["followers"] for r in synthetic_rows()) * 3
    out = analyze("newcreator", {}, deps(world, snap, Broken(FOUND)))
    assert out["status"] == "done" and out["result"]["web_rate"] is None
    assert np.isfinite(out["result"]["price"]["fair"])
