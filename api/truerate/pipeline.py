import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from statistics import median
from typing import Callable

from pymongo.database import Database

from truerate.instagram import fetch_covers
from truerate.pricing import PriceModel, per_1k, price
from truerate.signals import (
    CATEGORIES,
    FACE_SHARE,
    ambiguous,
    audience_signals,
    audience_warnings,
    band,
    band_norms,
    category_from_niche,
    commenter_mix,
    commenter_rings,
    face_share,
    fit_anomaly,
    genuine_share,
    has_face,
    is_paid,
    label_creator,
    label_niche,
    recent_reels,
    reel_metrics,
    verdict,
)

STEPS = ["Reading profile, reels and audience", "Spotting ads and measuring reels", "Checking audience quality", "Calculating fair price"]
MIN_REELS = 12
COMPETITOR_DAYS = 60


@dataclass
class Deps:
    db: Database
    collect: Callable[[str], dict]
    llm: object
    fake_model: object
    embed: Callable
    price_model: PriceModel
    fetch_covers: Callable = fetch_covers
    detect_face: Callable = field(default=has_face)


def _group(n: float) -> str:
    """Indian digit grouping: 1,50,000 and 1,23,45,678."""
    digits = str(int(round(n)))
    head, tail = digits[:-3], digits[-3:]
    while len(head) > 2:
        head, tail = head[:-2], head[-2:] + "," + tail
    return f"{head},{tail}" if head else tail


def inr(n: float) -> str:
    return "₹" + _group(n)


def when(days: int) -> str:
    return "today" if days == 0 else "yesterday" if days == 1 else f"{days} days ago"


def _flag_text(f: dict, s: dict) -> str:
    v, m = f["value"], f["median"]
    return {
        "fake_likers": lambda: f"{v:.0%} of {s['n_likers']} sampled likers look fake (similar creators: {m:.0%})",
        "likes_per_view": lambda: f"{v:.1%} of viewers like a reel (similar creators: {m:.1%})",
        "views_cv": lambda: f"Views barely vary between reels (spread {v:.2f}; similar creators: {m:.2f})",
        "likes_cv": lambda: f"Likes barely vary between reels (spread {v:.2f}; similar creators: {m:.2f})",
        "fake_followers": lambda: f"{v:.0%} of the {s['n_followers']} newest followers look fake (similar creators: {m:.0%})",
        "views_per_follower": lambda: f"Reels reach {v:.2f} views per follower (similar creators: {m:.2f})",
        "generic_comments": lambda: f"{v:.0%} of {s['n_comments']} comments are generic or repeated (similar creators: {m:.0%})",
        "repeat_commenters": lambda: f"{v} accounts comment on 60% or more of reels (similar creators: {m:.0f})",
        "ring_size": lambda: f"Shares 3 or more commenters with {v} other WLDD creators",
    }[f["signal"]]()


def _brand(reel: dict) -> str | None:
    names = reel["sponsors"] + reel["coauthors"] + re.findall(r"@([\w.]+)", reel["caption"])
    return names[0] if names else None


def _days_ago(iso: str) -> int:
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days


def analyze(handle: str, inputs: dict, deps: Deps, step: Callable[[int], None] = lambda i: None) -> dict:
    """One creator end to end. Returns {"status": "done", "result": ...} or {"status": "out_of_scope", "reason": ...}."""
    db = deps.db
    step(0)
    snap = deps.collect(handle)
    db.snapshots.insert_one(snap)
    d = snap["data"]
    if d["profile"]["is_private"]:
        return {"status": "out_of_scope", "reason": f"@{handle} is private, so its reels and audience can't be read."}
    reels = recent_reels(snap)
    if len(reels) < MIN_REELS:
        return {"status": "out_of_scope", "reason": f"@{handle} has {len(reels)} recent reels with visible views; TrueRate needs at least {MIN_REELS}."}

    step(1)
    covers = deps.fetch_covers(reels, limit=10)
    faces = face_share(covers, deps.detect_face)
    if faces is not None and faces < FACE_SHARE:
        return {"status": "out_of_scope", "reason": f"Only {round(faces * len(covers))} of {len(covers)} reel covers show a face. TrueRate prices face creators; About explains the plan for other pages."}
    deal = db.deals.find_one({"handle": handle})
    category = category_from_niche(deal["niche"]) if deal else None
    category_source = "wldd" if category else "gemini"
    with ThreadPoolExecutor(max_workers=2) as pool:  # the niche call runs alongside the long labelling call
        niche = None if category else pool.submit(label_niche, deps.llm, d["profile"]["bio"], [r["caption"] for r in reels])
        labels = label_creator(deps.llm, snap, {code: img for code, img in covers.items() if any(r["code"] == code and ambiguous(r) for r in reels)})
        category = category or niche.result()
    metrics = reel_metrics(snap, labels)

    step(2)
    wldd = [m for m in db.metrics.find({"_id": {"$ne": handle}})]
    signals = audience_signals(snap, metrics, deps.fake_model, deps.embed)
    commenters = {c["user"]["username"] for cs in d["comments"].values() for c in cs}
    signals["ring_size"] = commenter_rings({m["_id"]: set(m.get("commenters", [])) for m in wldd} | {handle: commenters})[handle]
    norms = band_norms(wldd)
    v = verdict(signals, norms)
    share = genuine_share(signals, norms)
    flags = [f | {"text": _flag_text(f, signals)} for f in v["flags"]]

    step(3)
    model = deps.price_model
    p = price(model, metrics | {"category": category}, share)
    same_band = [m["engagement"] for m in wldd if band(m["followers"]) == band(snap["followers"])]
    kinds = labels.get("kinds", {})

    def kind(r):
        if is_paid(r) or r["code"] in labels.get("ads", []) or any(kinds.get(c) == "brand" for c in r["coauthors"]):
            return "paid"
        return "collab" if r["coauthors"] else "repost" if r.get("repost_of") else "own"

    ads = [{"code": r["code"], "taken_at": r["taken_at"], "disclosed": is_paid(r), "brand": _brand(r), "topic": labels["topics"].get(r["code"])}
           for r in reels if kind(r) == "paid"]

    # Audience worth reaching: category value rank by WLDD's ₹ per 1,000 views, and product fit
    by_category = {c: median(per_1k(r) for r in model.rows if r["category"] == c) for c in CATEGORIES if any(r["category"] == c for r in model.rows)}
    rank = sorted(by_category, key=lambda c: -by_category[c])
    product = inputs.get("category")
    topics = list(labels.get("topics", {}).values())
    fit_share = (sum(t == product for t in topics) / len(topics) if topics else 0.0) if product else None
    fit = None if not product else "strong" if product == category else "good" if fit_share >= 0.2 else "weak" if fit_share < 0.1 else "some"
    worth = f"{category} audiences rank {rank.index(category) + 1} of {len(rank)} by WLDD's past ₹ per 1,000 views" if category in rank else f"WLDD has no past {category} deals to rank against"
    if product:
        worth += f"; {fit_share:.0%} of recent reels are about {product}, a {fit} fit."
    else:
        worth += "."
    # Brands that tagged the creator from their own page: collabs that never show on the creator's grid.
    brand_tags = sorted(({"code": t["code"], "taken_at": t["taken_at"], "brand": t["owner"], "topic": labels.get("topics", {}).get(t["code"])}
                         for t in d.get("tagged", []) if kinds.get(t["owner"]) == "brand"), key=lambda t: t["taken_at"], reverse=True)
    recent_same = sorted((x for x in ads + brand_tags if product and x["topic"] == product and _days_ago(x["taken_at"]) <= COMPETITOR_DAYS),
                         key=lambda x: x["taken_at"], reverse=True)
    competitor = {"brand": recent_same[0]["brand"], "days": _days_ago(recent_same[0]["taken_at"]), "code": recent_same[0]["code"]} if recent_same else None

    decision = _decide(v, flags, p, inputs, metrics, model.paid_typical, fit, fit_share, competitor)
    cheaper = sorted((r for r in model.rows if r["category"] == category and per_1k(r) < p["delivery"]["cost_per_1k"]
                      and metrics["views"] / 2 <= r["views"] <= metrics["views"] * 2), key=per_1k)[:3]
    result = {
        "handle": handle,
        "profile": {k: d["profile"][k] for k in ("full_name", "followers", "following", "posts", "bio", "is_verified")},
        "fetched_at": snap["fetched_at"].isoformat(),
        "category": category,
        "category_source": category_source,
        "face_share": faces,
        "decision": decision,
        "price": p,
        "audience": {
            "verdict": v["verdict"],
            "failed_families": v["failed_families"],
            "flags": flags,
            "signals": signals,
            "medians": v["medians"],
            "warnings": audience_warnings(signals, fit_anomaly(wldd)),
            "mix": commenter_mix(snap, deps.fake_model, labels),
        },
        "engagement": {
            "rate": metrics["engagement"],
            "band": band(snap["followers"]),
            "band_median": median(same_band) if same_band else None,
            "percentile": round(100 * sum(e < metrics["engagement"] for e in same_band) / len(same_band)) if same_band else None,
        },
        "placement": {
            "reels": [{"code": r["code"], "taken_at": r["taken_at"], "views": r["views"], "likes": r["likes"], "comments": r["comments"], "kind": kind(r),
                       "thumbnail": r.get("thumbnail", "")} for r in reels],
            "followers_history": [{"at": s["fetched_at"].isoformat(), "followers": s["followers"]} for s in db.snapshots.find({"handle": handle}).sort("fetched_at")],
            "typical_views": metrics["views"],
            "bad_reel_views": metrics["views_p25"],
            "hits_last_10": metrics["hits_last_10"],
            "trend": metrics["trend"],
            "paid": {"n": metrics["paid_n"], "ratio": metrics["paid_ratio"], "typical_ratio": model.paid_typical},
            "collab": {"n": metrics["collab_n"], "ratio": metrics["collab_ratio"]},
            "ads": ads,
            "brand_tags": brand_tags,
            "n_reposts": metrics["n_reposts"],
        },
        "niche": {"category": category, "topics": {t: topics.count(t) for t in set(topics)}, "product": product, "fit": fit, "fit_share": fit_share},
        "worth_reaching": worth,
        "competitor": competitor,
        "cheaper": [{"handle": r["handle"], "per_1k_views": round(per_1k(r)), "views": r["views"], "price": r["price"]} for r in cheaper],
        "suggested": [u["username"] for u in d.get("suggested", [])[:6]],
        "negotiation": _negotiation(p, flags, metrics, category),
    }
    return {"status": "done", "result": result}


def _decide(v, flags, p, inputs, metrics, typical, fit, fit_share, competitor) -> dict:
    avoid, negotiate, good = [], [], []
    texts = [f["text"] for f in flags]
    if v["verdict"] == "Mostly fake":
        avoid += texts
    elif v["verdict"] == "Some fake activity":
        negotiate += texts
    else:
        good.append("Real audience: likes, followers and comments all look like similar creators'")
    if fit == "weak":
        avoid.append(f"Weak fit for {inputs['category']}: {fit_share:.0%} of recent reels are about it")
    if competitor:
        avoid.append(f"Promoted {competitor['brand'] or 'a brand'} in {inputs['category']} {when(competitor['days'])}")
    quote, budget = inputs.get("quote"), inputs.get("budget")
    if quote:
        if quote > p["high"]:
            negotiate.append(f"Quoted {inr(quote)} is {inr(quote - p['high'])} above the fair range ({inr(p['low'])} to {inr(p['high'])})")
        else:
            good.append(f"Quoted {inr(quote)} is {'below' if quote < p['low'] else 'within'} the fair range")
    if budget and p["fair"] > budget:
        negotiate.append(f"Fair price {inr(p['fair'])} is {inr(p['fair'] - budget)} over the {inr(budget)} budget")
    if p["collab_factor"] < 0.85:
        negotiate.append(f"Paid reels keep {metrics['paid_ratio']:.0%} of usual views, against {typical:.0%} for a typical creator")
    call = "Avoid" if avoid else "Negotiate" if negotiate else "Go"
    return {"call": call, "reasons": avoid + negotiate + (good if call == "Go" else [])}


def _negotiation(p: dict, flags: list[dict], metrics: dict, category: str) -> dict:
    d = p["delivery"]
    lines = [f"WLDD's past {category} deals of this size work out to about {inr(d['category_cost_per_1k'])} per 1,000 views." if d["category_cost_per_1k"] else None,
             f"Your typical reel gets {_group(metrics['views'])} views and a weaker one {_group(metrics['views_p25'])}; we price on what a sponsored reel delivers, about {_group(d['views'][1])}.",
             *[f["text"] + "." for f in flags[:2]],
             f"We can do {inr(p['low'])} now and go up to {inr(p['fair'])} for a usage-rights or story add-on."]
    return {"start": p["low"], "target": p["fair"], "walk_away": p["high"], "lines": [x for x in lines if x]}


def check_quote(r: dict, quote: int) -> dict:
    """A creator's quote against a finished report: where it sits, what to counter with, and 3 data-backed points."""
    p, d = r["price"], r["price"]["delivery"]
    position = "below" if quote < p["low"] else "above" if quote > p["high"] else "within"
    per_1k = round(quote / (r["placement"]["typical_views"] / 1000))
    points = [
        f"At {inr(quote)}, a reel costs {inr(per_1k)} per 1,000 typical views"
        + (f"; {r['category']} creators WLDD booked average {inr(d['category_cost_per_1k'])}." if d["category_cost_per_1k"] else "."),
        f"A sponsored reel here should get about {_group(d['views'][1])} views, and we pay for what it delivers.",
    ]
    if r["audience"]["flags"]:
        points.append(r["audience"]["flags"][0]["text"] + ".")
    else:
        paid = [c["price"] for c in p["comparables"]]
        points.append(f"The 6 closest past WLDD deals were paid {inr(min(paid))} to {inr(max(paid))}.")
    return {"quote": quote, "position": position, "difference": quote - p["fair"], "counter_offer": min(quote, p["fair"]), "talking_points": points}
