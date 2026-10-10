"""Brand match: from a brand (Instagram handle, website or name) to the creators worth booking for it, why each, and
the set that brings the most views within a budget. Gemini only ever sees the brand's own public words."""

import html as html_lib
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from truerate.instagram import _or_empty
from truerate.pricing import PriceModel, likely_band, price
from truerate.signals import CATEGORIES, PRODUCT_CATEGORY, PRODUCTS, band_norms, genuine_share, verdict

_HANDLE = re.compile(r"^@?([A-Za-z0-9._]{1,30})$")
_INSTAGRAM = re.compile(r"^(?:https?://)?(?:www\.)?instagram\.com/([A-Za-z0-9._]{1,30})/?", re.I)
_DOMAIN = re.compile(r"\.(com|in|co|io|org|net|shop|store|app|ai)(/|$)", re.I)

STEPS = ["Reading the brand", "Working out what the brand sells and to whom", "Gathering creators", "Ranking them"]


def parse_brand(text: str) -> dict:
    """{"kind": "instagram" | "website" | "name", "value"}. A bare word is read as an Instagram handle."""
    t = text.strip()
    if m := _INSTAGRAM.match(t):
        return {"kind": "instagram", "value": m.group(1).lower()}
    if t.startswith("@") and _HANDLE.match(t):
        return {"kind": "instagram", "value": t[1:].lower()}
    if "://" in t:
        return {"kind": "website", "value": t}
    if " " not in t and _DOMAIN.search(t):
        return {"kind": "website", "value": f"https://{t}"}
    if _HANDLE.match(t):
        return {"kind": "instagram", "value": t.lower()}
    return {"kind": "name", "value": t}


def site_text(http, url: str, limit: int = 3000) -> str:
    """The words on a brand's site: title, meta description and visible text, without scripts or styles."""
    page = http.get(url, timeout=15, follow_redirects=True).text
    title = re.search(r"<title[^>]*>(.*?)</title>", page, re.S | re.I)
    description = re.search(r"<meta[^>]+name=['\"]description['\"][^>]+content=['\"](.*?)['\"]", page, re.S | re.I)
    body = re.sub(r"<head[^>]*>.*?</head>", " ", page, flags=re.S | re.I)
    body = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    words = " ".join(html_lib.unescape(re.sub(r"<[^>]+>", " ", body)).split())
    parts = [title.group(1).strip() if title else "", description.group(1).strip() if description else "", words]
    return "\n".join(p for p in parts if p)[:limit]


PROFILE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "name": {"type": "STRING"},
        "category": {"type": "STRING", "enum": list(CATEGORIES)},
        "product": {"type": "STRING", "enum": [p for products in PRODUCTS.values() for p in products]},
        "audience": {"type": "STRING", "description": "who the brand sells to, in one short phrase"},
        "tone": {"type": "STRING", "description": "the brand's voice, in a few words"},
        "price_tier": {"type": "STRING", "enum": ["budget", "mid", "premium"]},
        "rivals": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Instagram handles of direct rivals, if known"},
    },
    "required": ["name", "category", "product", "audience", "tone", "price_tier", "rivals"],
}


def profile_brand(llm, text: str) -> dict:
    """What the brand sells and to whom, from its own words (Instagram or website), for picking creators."""
    prompt = ("Describe this brand for planning an Instagram influencer campaign in India: its name, which category and product "
              f"it sells, its audience, its tone and price tier, and direct rivals if you know them.\n\n{text}")
    return llm.json(prompt, PROFILE_SCHEMA)


def instagram_brand(hiker, handle: str) -> dict:
    """The brand's profile, one page of its reels and the posts that tag it: about 3 HikerAPI requests."""
    profile = hiker.profile(handle)
    if profile["is_private"]:
        return {"profile": profile, "reels": [], "tagged": []}
    return {"profile": profile, "reels": hiker.reels(profile["pk"], pages=1), "tagged": _or_empty(hiker.tagged, profile["pk"], [])}


def brand_partners(data: dict) -> list[str]:
    """Accounts seen with the brand: co-authors and people tagged in its reels, and accounts whose posts tag it."""
    me = data["profile"]["username"].lower()
    names = {n.lower() for r in data.get("reels", []) for n in r.get("coauthors", []) + r.get("tags", [])}
    names |= {t["owner"].lower() for t in data.get("tagged", [])}
    return sorted(names - {me})


EMPTY = {"category": None, "topics": {}, "verdict": None, "fair": None, "likely_low": None, "likely_high": None, "cost_per_1k": None,
         "category_cost_per_1k": None, "expected_views": None, "hits_last_10": None, "followers": None, "analysis_id": None}


def candidates(db, model: PriceModel, brand_handle: str | None, partners: list[str]) -> list[dict]:
    """Every creator worth considering, each labelled with where it came from: WLDD's own creators (priced now with the
    served model), creators analysed before (from their stored report), and accounts seen with the brand."""
    pool: dict[str, dict] = {}

    def add(handle: str, source: str, data: dict | None = None) -> None:
        c = pool.setdefault(handle, {"handle": handle, "sources": [], **EMPTY})
        if source not in c["sources"]:
            c["sources"].append(source)
        if data:
            c.update(data)

    wldd = list(db.metrics.find({}, {"commenters": 0}))
    norms = band_norms(wldd) if len(wldd) >= 10 else None
    for m in wldd:
        p = price(model, m, genuine_share(m, norms) if norms else 1.0)
        topics = Counter((m.get("labels") or {}).get("topics", {}).values())
        add(m["_id"], "WLDD booked", {
            "category": m["category"], "topics": dict(topics), "verdict": verdict(m, norms)["verdict"] if norms else None, "fair": p["fair"],
            "likely_low": p["likely_low"], "likely_high": p["likely_high"], "cost_per_1k": p["delivery"]["cost_per_1k"],
            "category_cost_per_1k": p["delivery"]["category_cost_per_1k"], "expected_views": p["delivery"]["views"][1],
            "hits_last_10": m["hits_last_10"], "followers": m["followers"]})
    latest = {}
    for a in db.analyses.find({"status": "done"}, {"handle": 1, "result": 1, "created_at": 1}).sort("created_at", 1):
        latest[a["handle"]] = a
    for handle, a in latest.items():
        r, p = a["result"], a["result"]["price"]
        low, high = (p["likely_low"], p["likely_high"]) if p.get("likely_low") else likely_band(p["fair"], p["low"], p["high"])
        add(handle, "Analysed before", {
            "category": r["category"], "topics": r["niche"]["topics"], "verdict": r["audience"]["verdict"], "fair": p["fair"],
            "likely_low": low, "likely_high": high, "cost_per_1k": p["delivery"]["cost_per_1k"],
            "category_cost_per_1k": p["delivery"]["category_cost_per_1k"], "expected_views": p["delivery"]["views"][1],
            "hits_last_10": r["placement"]["hits_last_10"], "followers": r["profile"]["followers"], "analysis_id": a["_id"]})
    for handle in partners:
        add(handle, "Worked with the brand")
    pool.pop((brand_handle or "").lower(), None)
    return list(pool.values())


def score(c: dict, brand: dict, budget: int | None) -> dict:
    """Points for what matters to the booking, each with a plain answer: fit, audience, value, budget, reliability, and
    whether the creator has already worked with the brand."""
    answers, total = [], 0.0

    def add(key: str, status: str, title: str, points: float) -> None:
        nonlocal total
        answers.append({"key": key, "status": status, "title": title})
        total += points

    category = brand["category"]
    topics = c.get("topics") or {}
    share = c.get("topic_share")
    if share is None and topics:
        share = topics.get(category, 0) / sum(topics.values())
    if c["category"] == category:
        add("fit", "good", f"Makes {category} content", 3)
    elif share is not None and share >= 0.2:
        add("fit", "good", f"Often covers {category}", 2)
    elif share is not None and share >= 0.1:
        add("fit", "warn", f"Sometimes covers {category}", 1)
    else:
        add("fit", "bad", f"Rarely covers {category}", -1)

    v = c.get("verdict")
    if v == "Real audience":
        add("audience", "good", "Real audience", 2)
    elif v == "Some fake activity":
        add("audience", "warn", "Some fake activity", 0)
    elif v == "Mostly fake":
        add("audience", "bad", "Mostly fake audience", -3)

    if c.get("cost_per_1k") and c.get("category_cost_per_1k"):
        ratio = c["cost_per_1k"] / c["category_cost_per_1k"]
        if ratio <= 1:
            add("value", "good", "Good value for the views", 2)
        elif ratio <= 1.5:
            add("value", "warn", "Views cost a little more than usual", 1)
        else:
            add("value", "bad", "Expensive for the views", 0)

    if budget:
        if c["fair"] <= budget:
            add("budget", "good", "Fits your budget", 1)
        elif (c.get("likely_low") or c["fair"]) <= budget:
            add("budget", "warn", "Fits your budget only at the low end", 0)
        else:
            add("budget", "bad", "Over your budget", -2)

    hits = c.get("hits_last_10")
    if hits is not None:
        if hits >= 7:
            add("consistency", "good", "Reliable: most reels perform", 1)
        elif hits >= 4:
            add("consistency", "warn", "Hit or miss", 0)
        else:
            add("consistency", "bad", "Unreliable: most recent reels flop", -1)

    if "Worked with the brand" in c["sources"]:
        add("brand", "good", f"Has worked with {brand.get('name') or 'this brand'}", 1)
    return {"score": total, "answers": answers, "reasons": [a["title"] for a in answers if a["status"] == "good"]}


def budget_plan(cands: list[dict], budget: int, unit: int = 500) -> dict:
    """The set of creators with the most expected views whose prices to aim for fit the budget (0/1 knapsack in ₹500 steps)."""
    cap = budget // unit
    best: dict[int, tuple[int, tuple[dict, ...]]] = {0: (0, ())}
    for c in cands:
        if not c.get("fair") or not c.get("expected_views") or c["fair"] > budget:
            continue
        weight = math.ceil(c["fair"] / unit)
        for cost, (views, chosen) in list(best.items()):
            if cost + weight <= cap and (cost + weight not in best or views + c["expected_views"] > best[cost + weight][0]):
                best[cost + weight] = (views + c["expected_views"], chosen + (c,))
    views, chosen = max(best.values(), key=lambda x: x[0])
    return {"handles": [c["handle"] for c in chosen], "cost": sum(c["fair"] for c in chosen), "views": views}


@dataclass
class BrandDeps:
    db: object
    llm: object
    price_model: PriceModel
    fetch_instagram: Callable[[str], dict]  # {"profile", "reels", "tagged"} for a brand's handle
    fetch_site: Callable[[str], str]  # a website's visible text


def run_brand(deps: BrandDeps, req: dict, step: Callable[[int], None] = lambda i: None) -> dict:
    """The brand's profile, its top creators with reasons, a budget plan, and the accounts seen with it that have no
    analysis yet."""
    step(0)
    src = parse_brand(req["brand"])
    data = None
    if src["kind"] == "instagram":
        data = deps.fetch_instagram(src["value"])
        p = data["profile"]
        captions = "\n".join(f"- {r.get('caption', '')[:200]}" for r in data.get("reels", [])[:12])
        text = (f"Instagram @{p['username']} ({p.get('full_name', '')}), {p.get('followers', 0):,} followers, category: {p.get('category', '')}\n"
                f"Bio: {p.get('bio', '')}\nWebsite: {p.get('external_url', '')}\nRecent captions:\n{captions}")
    elif src["kind"] == "website":
        text = f"Website {src['value']}:\n{deps.fetch_site(src['value'])}"
    else:
        text = f"Brand name: {src['value']}"

    step(1)
    profile = dict(profile_brand(deps.llm, text))
    if product := req.get("product"):  # what the campaign sells wins over what the brand sells in general
        profile |= {"product": product, "category": PRODUCT_CATEGORY.get(product, profile["category"])}

    step(2)
    handle = src["value"] if src["kind"] == "instagram" else None
    pool = candidates(deps.db, deps.price_model, handle, brand_partners(data) if data else [])

    step(3)
    budget = req.get("budget")
    scored = sorted((c | score(c, profile, budget) for c in pool if c["fair"] is not None), key=lambda c: (-c["score"], c["cost_per_1k"] or math.inf))
    picks = scored[: req.get("count") or 10]
    bookable = [c for c in picks if not any(a["key"] in ("audience", "fit") and a["status"] == "bad" for a in c["answers"])]
    return {
        "brand": profile | {"source": src["kind"], "handle": handle, "url": src["value"] if src["kind"] == "website" else None},
        "picks": picks,
        "plan": budget_plan(bookable, budget) if budget else None,
        "to_price": [c["handle"] for c in pool if c["fair"] is None][:20],
        "pool_size": len(scored),
    }
