"""Plain answers from a finished analysis, for people who want the verdict rather than the measurements behind it.
Computed on read from the stored report, so older analyses get them too, and the report and the batch say the same."""

from truerate.pipeline import when
from truerate.pricing import inr, likely_band

# What each audience flag means, without its numbers.
PLAIN_FLAG = {
    "fake_likers": "many likers look like bots",
    "likes_per_view": "few viewers like the reels",
    "views_cv": "views are suspiciously even from reel to reel",
    "likes_cv": "likes are suspiciously even from reel to reel",
    "fake_followers": "many new followers look fake",
    "views_per_follower": "reels reach few of the followers",
    "generic_comments": "many comments are generic or repeated",
    "repeat_commenters": "the same accounts comment on almost every reel",
    "ring_size": "commenters overlap with other WLDD creators, like an engagement pod",
}


def _views(n: float) -> str:
    """1.7L, 45K, 1.2Cr."""
    for size, unit in ((1e7, "Cr"), (1e5, "L"), (1e3, "K")):
        if n >= size:
            return f"{n / size:.1f}".rstrip("0").rstrip(".") + unit
    return str(round(n))


def _sentence(parts: list[str]) -> str:
    text = ", ".join(dict.fromkeys(parts))
    return text[:1].upper() + text[1:] + "."


def outputs(r: dict, inputs: dict) -> list[dict]:
    """Each answer: a key, a status (good, warn, bad or info), a title and a one-sentence detail. Most important first;
    a question nobody asked (no quote, no budget, no product) gets no answer."""
    p, d, placement, niche = r["price"], r["price"]["delivery"], r["placement"], r["niche"]
    out: list[dict] = []

    def add(key: str, status: str, title: str, detail: str = "") -> None:
        out.append({"key": key, "status": status, "title": title, "detail": detail})

    if quote := inputs.get("quote"):
        likely_low, likely_high = (p["likely_low"], p["likely_high"]) if p.get("likely_low") else likely_band(p["fair"], p["low"], p["high"])
        if quote > p["high"]:
            add("quote", "bad", f"Their {inr(quote)} quote is too high", f"Counter at {inr(p['fair'])} and walk away above {inr(p['high'])}.")
        elif quote > likely_high:
            add("quote", "warn", f"Their {inr(quote)} quote is on the high side", f"Most deals like this land lower: counter at {inr(p['fair'])}.")
        elif quote < p["low"]:
            add("quote", "good", f"Their {inr(quote)} quote is a bargain", "It is below the fair range.")
        elif quote < likely_low:
            add("quote", "good", f"Their {inr(quote)} quote is a good price", "It is below where most deals like this land.")
        else:
            add("quote", "good", f"Their {inr(quote)} quote is fair", f"It is where most deals like this land; the middle is {inr(p['fair'])}.")

    if budget := inputs.get("budget"):
        if budget >= p["fair"]:
            add("budget", "good", f"Fits your {inr(budget)} budget", "The middle of the fair range is within it.")
        elif budget >= p["low"]:
            add("budget", "warn", f"Fits your {inr(budget)} budget only at the low end", f"The middle of the fair range is {inr(p['fair'])}.")
        else:
            add("budget", "bad", f"Over your {inr(budget)} budget", f"The fair price starts at {inr(p['low'])}.")

    verdict = r["audience"]["verdict"]
    if verdict == "Real audience":
        add("audience", "good", "Real audience", "Likes, followers and comments look like those of genuine creators this size.")
    else:
        signs = [PLAIN_FLAG[f["signal"]] for f in r["audience"]["flags"] if f["signal"] in PLAIN_FLAG]
        detail = _sentence(signs) if signs else "Some of the engagement doesn't look genuine."
        if p.get("genuine_share", 1.0) < 1:
            detail += " The price pays only for the real part."
        add("audience", "warn" if verdict == "Some fake activity" else "bad", verdict, detail)

    if usual := d.get("category_cost_per_1k"):
        ratio = d["cost_per_1k"] / usual
        if ratio <= 1:
            add("value", "good", "Good value for the views", f"Each view costs less than WLDD usually pays for {r['category']}.")
        elif ratio <= 1.5:
            add("value", "warn", "Views cost a little more than usual", f"A bit above what WLDD usually pays for {r['category']}.")
        else:
            add("value", "bad", "Expensive for the views", f"Each view costs well above what WLDD usually pays for {r['category']}.")

    add("reach", "info", f"Expect about {_views(d['views'][1])} views", f"On the sponsored reel; a weak one gets about {_views(d['views'][0])}.")

    hits = placement["hits_last_10"]
    if hits >= 7:
        add("consistency", "good", "Reliable: most reels perform", f"{hits} of the last 10 reels reached at least half the usual views.")
    elif hits >= 4:
        add("consistency", "warn", "Hit or miss", f"Only {hits} of the last 10 reels reached half the usual views.")
    else:
        add("consistency", "bad", "Unreliable: most recent reels flop", f"Only {hits} of the last 10 reels reached half the usual views.")

    paid, factor = placement["paid"], p.get("collab_factor", 1.0)
    if not paid["n"] or paid.get("ratio") is None:
        add("ads", "info", "No sponsored reels to judge yet", "How an ad does is unknown, so the price follows their own reels.")
    elif factor >= 0.95:
        add("ads", "good", "Ads do as well as their own reels", "Sponsored reels keep their usual reach.")
    elif factor >= 0.75:
        add("ads", "warn", "Ads get fewer views than their own reels", "The price is lowered for it.")
    else:
        add("ads", "bad", "Ads flop", "Sponsored reels get far fewer views than their own; the price is lowered for it.")

    if (product := niche.get("product")) and (fit := niche.get("fit")):
        status, word = {"strong": ("good", "Strong"), "good": ("good", "Good"), "some": ("warn", "Partial"), "weak": ("bad", "Weak")}[fit]
        add("fit", status, f"{word} fit for {product}", "Few recent reels are about it." if fit == "weak" else "Their recent reels cover it.")

    if c := r.get("competitor"):
        brand = f"@{c['brand']}" if c.get("brand") else "a brand"
        add("competitor", "warn", f"Promoted {brand} in {c.get('category') or product or r['category']} {when(c['days'])}", "Check exclusivity before booking.")

    percentile = r["engagement"].get("percentile")
    if percentile is not None and percentile >= 60:
        add("engagement", "good", "Fans engage more than most creators this size")
    elif percentile is not None and percentile < 30:
        add("engagement", "warn", "Fans engage less than most creators this size")

    trend = placement.get("trend")
    if trend is not None and trend <= 0.7:
        add("trend", "warn", "Views are falling", "Recent reels get clearly fewer views than the ones before.")
    elif trend is not None and trend >= 1.3:
        add("trend", "good", "Views are rising", "Recent reels get clearly more views than the ones before.")

    if web := r.get("web_rate"):
        if web["found"]:
            add("web", "info", f"Published online: {inr(web['low'])} to {inr(web['high'])} a reel", web["summary"])
        else:
            add("web", "info", "No published rate for this creator online", "A web search found no rate card, listing or reported deal.")

    if note := p.get("note"):
        if note.startswith("Bigger"):
            add("size", "warn", "Bigger than any creator WLDD has booked",
                "So the price leans on the market rate for this size, discounted the way WLDD pays. Expect them to ask more.")
        else:
            add("size", "warn", "Smaller than any creator WLDD has booked", "The price is less certain this far from WLDD's deals.")
    return out
