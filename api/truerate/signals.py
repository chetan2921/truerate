import copy
import csv
import math
import re
from functools import lru_cache
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.ensemble import RandomForestClassifier

# The Kaggle columns we can fill from a likers or followers list without an extra request per account.
KAGGLE_LIGHT = ["profile pic", "nums/length username", "fullname words", "nums/length fullname", "name==username", "private"]


def _digit_ratio(text: str) -> float:
    return round(sum(c.isdigit() for c in text) / len(text), 2) if text else 0


def account_features(acc: dict) -> list[float]:
    """An account as `{username, full_name, has_pic, is_private}`, in `KAGGLE_LIGHT` order."""
    name = acc["full_name"].strip()
    return [
        int(acc["has_pic"]),
        _digit_ratio(acc["username"]),
        len(name.split()),
        _digit_ratio(name),
        int(name.lower() == acc["username"].lower()),
        int(acc["is_private"]),
    ]


def load_kaggle(path: Path) -> tuple[list[list[float]], list[int]]:
    rows = list(csv.DictReader(path.open()))
    return [[float(r[c]) for c in KAGGLE_LIGHT] for r in rows], [int(r["fake"]) for r in rows]


def train_fake_model(X: list[list[float]], y: list[int]) -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=300, random_state=42).fit(X, y)


def fake_share(model: RandomForestClassifier, accounts: list[dict]) -> float | None:
    """Share of accounts the model calls fake. None when there are none to check (likes hidden, say)."""
    if not accounts:
        return None
    return round(float(sum(model.predict([account_features(a) for a in accounts])) / len(accounts)), 4)


# WLDD's categories, each with the CSV genres that fall under it.
CATEGORIES = {
    "Tech and gadgets": ["Technology", "Gadgets", "Gaming"],
    "Fashion and beauty": ["Fashion", "Beauty"],
    "Lifestyle and travel": ["Lifestyle", "Vlogger", "Travel"],
    "Entertainment": ["Entertainment", "Storytelling", "Creative Sketches", "Comedy Sketches", "Filmmaker", "Music", "Dance", "Memes"],
    "Education, finance and news": ["Education", "Finance", "News and Media"],
    "Food": ["Food"],
    "Fitness": ["Fitness"],
}
_GENRE_CATEGORY = {g: c for c, genres in CATEGORIES.items() for g in genres}


def category_from_niche(genres: list[str]) -> str | None:
    """The category of WLDD's first listed genre, or None when the CSV has no niche."""
    return next((_GENRE_CATEGORY[g] for g in genres if g in _GENRE_CATEGORY), None)


# ASCI disclosure hashtags. `#adventure` must not match, hence the word boundary.
_AD_TAG = re.compile(r"#(ad|ads|sponsored|collab|partnership|paidpartnership|paidcollab|freegift|gifted)\b", re.IGNORECASE)


def is_paid(reel: dict) -> bool:
    return reel["paid"] or bool(reel["sponsors"]) or bool(_AD_TAG.search(reel["caption"]))


def recent_reels(snapshot: dict) -> list[dict]:
    """The last 30 unpinned reels with visible views, newest first."""
    return sorted((r for r in snapshot["data"]["reels"] if not r["pinned"] and r["views"] > 0), key=lambda r: r["taken_at"], reverse=True)[:30]


def reel_metrics(snapshot: dict, labels: dict | None = None) -> dict:
    """Stats over the recent reels. Paid: the rules, Gemini's hidden ads, or a brand co-author. Collab: any other co-author.
    Own: the rest."""
    ads = set((labels or {}).get("ads", []))
    kinds = (labels or {}).get("kinds", {})

    def paid_reel(r):
        return is_paid(r) or r["code"] in ads or any(kinds.get(c) == "brand" for c in r["coauthors"])

    reels = recent_reels(snapshot)
    paid = [r for r in reels if paid_reel(r)]
    collab = [r for r in reels if r["coauthors"] and not paid_reel(r)]
    reposts = [r for r in reels if r.get("repost_of") and not r["coauthors"] and not paid_reel(r)]
    own = [r for r in reels if not r["coauthors"] and not paid_reel(r) and not r.get("repost_of")]
    views = median(r["views"] for r in own)

    def ratio(group):
        return round(median(r["views"] for r in group) / views, 4) if group else None

    last10, prev10 = reels[:10], reels[10:20]
    return {
        "followers": snapshot["followers"],
        "n_reels": len(reels),
        "n_own": len(own),
        "views": views,
        "views_p25": float(np.percentile([r["views"] for r in own], 25)),
        "views_p75": float(np.percentile([r["views"] for r in own], 75)),
        "views_per_follower": round(views / snapshot["followers"], 4),
        "engagement": round(median((r["likes"] + r["comments"]) / r["views"] for r in own), 4),
        "likes_per_view": round(median(r["likes"] / r["views"] for r in own), 4),
        "comments_per_1k": round(median(r["comments"] * 1000 / r["views"] for r in own), 4),
        "hits_last_10": sum(r["views"] >= views / 2 for r in last10),
        "trend": round(median(r["views"] for r in last10) / median(r["views"] for r in prev10), 4) if prev10 else None,
        "paid_n": len(paid),
        "paid_ratio": ratio(paid),
        "collab_n": len(collab),
        "collab_ratio": ratio(collab),
        "n_reposts": len(reposts),
    }


def label_niche(llm, bio: str, captions: list[str]) -> str:
    """One of CATEGORIES, from the bio and the 12 newest captions."""
    lines = "\n".join(f"- {c[:300]}" for c in captions[:12])
    prompt = f"Pick the one category that fits this Instagram creator best.\n\nBio: {bio}\n\nRecent reel captions:\n{lines}"
    schema = {"type": "OBJECT", "properties": {"category": {"type": "STRING", "enum": list(CATEGORIES)}}, "required": ["category"]}
    return llm.json(prompt, schema)["category"]


def band(followers: int) -> str:
    return "small" if followers < 20_000 else "medium" if followers < 100_000 else "big"


@lru_cache
def _minilm():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def minilm_embed(texts: list[str]) -> np.ndarray:
    return _minilm().encode(texts, normalize_embeddings=True)


# What bought and pod comments look like, in English and Hinglish. MiniLM is multilingual, so close variants match too.
GENERIC_TEMPLATES = ["nice", "nice post", "great content", "amazing video", "love this", "awesome", "wow", "so beautiful", "superb",
                     "keep it up", "very nice", "bahut badhiya", "mast hai", "op bhai"]
GENERIC_SIM = 0.8  # checked on real comments: catches "Wow" and emoji strings, not sentences
REPEAT_SIM = 0.92
POD_SHARE = 0.6  # a commenter on this share of reels or more is a repeat commenter


def comment_signals(comments_by_reel: dict[str, list[dict]], embed) -> dict:
    """Share of generic or repeated comments, and how many accounts commented on 60%+ of the reels."""
    flat = [(rid, c) for rid, cs in comments_by_reel.items() for c in cs]
    if not flat:
        return {"generic_comments": None, "repeat_commenters": 0, "n_comments": 0}
    texts = [c["text"] for _, c in flat]
    emoji_only = np.array([not re.sub(r"[\W_]+", "", t) for t in texts])
    vecs = np.asarray(embed(texts))
    generic = (vecs @ np.asarray(embed(GENERIC_TEMPLATES)).T).max(axis=1) >= GENERIC_SIM
    other_reel = np.array([[a != b for b, _ in flat] for a, _ in flat])
    repeated = ((vecs @ vecs.T >= REPEAT_SIM) & other_reel).any(axis=1)
    reels_by_user: dict[str, set] = {}
    for rid, c in flat:
        reels_by_user.setdefault(c["user"]["username"], set()).add(rid)
    with_comments = sum(1 for cs in comments_by_reel.values() if cs)
    return {
        "generic_comments": round(float(np.mean(emoji_only | generic | repeated)), 4),
        "repeat_commenters": sum(len(rs) >= POD_SHARE * with_comments for rs in reels_by_user.values()),
        "n_comments": len(flat),
    }


def _cv(values: list[float]) -> float:
    return round(float(np.std(values) / np.mean(values)), 4)


def audience_signals(snapshot: dict, metrics: dict, fake_model, embed) -> dict:
    d = snapshot["data"]
    reels = recent_reels(snapshot)
    likers = [a for accounts in d["likers"].values() for a in accounts]
    return {
        "followers": snapshot["followers"],
        "fake_likers": fake_share(fake_model, likers),
        "n_likers": len(likers),
        "likes_per_view": metrics["likes_per_view"],
        "views_cv": _cv([r["views"] for r in reels]),
        "likes_cv": _cv([r["likes"] for r in reels]),
        "fake_followers": fake_share(fake_model, d["followers"]),
        "n_followers": len(d["followers"]),
        "views_per_follower": metrics["views_per_follower"],
        **comment_signals(d["comments"], embed),
        "former_usernames": d["about"]["former_usernames"],
    }


# signal: (family, bad direction, compare in log scale, smallest gap from the band median that counts)
AUDIENCE_SIGNALS = {
    "fake_likers": ("likes", "high", False, 0.10),
    "likes_per_view": ("likes", "low", True, math.log(2)),
    "views_cv": ("likes", "low", True, math.log(2)),
    "likes_cv": ("likes", "low", True, math.log(2)),
    "fake_followers": ("followers", "high", False, 0.10),
    "views_per_follower": ("followers", "low", True, math.log(2)),
    "generic_comments": ("comments", "high", False, 0.15),
    "repeat_commenters": ("comments", "high", False, 3),
    "ring_size": ("comments", "high", False, 2),
}
VERDICTS = ["Real audience", "Some fake activity", "Mostly fake"]


def _scale(value: float, log: bool) -> float:
    return math.log(max(value, 1e-6)) if log else value


def band_norms(rows: list[dict]) -> dict:
    """Per follower band (and "all"), each signal's median and its box-plot fence (1.5 IQR past the quartile, toward bad)."""
    groups = {"all": rows} | {b: [r for r in rows if band(r["followers"]) == b] for b in ("small", "medium", "big")}
    norms = {}
    for name, group in groups.items():
        if len(group) < 10:
            continue
        norms[name] = {}
        for s, (_, direction, log, _) in AUDIENCE_SIGNALS.items():
            values = [r[s] for r in group if r.get(s) is not None]
            if not values:
                continue
            q1, q3 = np.percentile([_scale(v, log) for v in values], [25, 75])
            fence = q3 + 1.5 * (q3 - q1) if direction == "high" else q1 - 1.5 * (q3 - q1)
            norms[name][s] = {"median": float(median(values)), "fence": float(fence)}
    return norms


def verdict(signals: dict, norms: dict) -> dict:
    """A signal is bad when it is past its band's fence and at least its minimum gap from the band median.
    A family with a bad signal fails; 0, 1, or 2+ failed families give the three verdicts."""
    ref = norms.get(band(signals["followers"]), norms["all"])
    flags = []
    for s, (family, direction, log, gap) in AUDIENCE_SIGNALS.items():
        if signals.get(s) is None or s not in ref:
            continue
        value, mid, fence = _scale(signals[s], log), _scale(ref[s]["median"], log), ref[s]["fence"]
        bad = value > fence and value - mid >= gap if direction == "high" else value < fence and mid - value >= gap
        if bad:
            flags.append({"signal": s, "family": family, "value": signals[s], "median": ref[s]["median"]})
    failed = [f for f in ("likes", "followers", "comments") if any(x["family"] == f for x in flags)]
    return {"verdict": VERDICTS[min(len(failed), 2)], "failed_families": failed, "flags": flags, "medians": {s: v["median"] for s, v in ref.items()}}


def genuine_share(signals: dict, norms: dict) -> float:
    """1 minus the largest fake share above the band median, counted only for flagged signals: fake likers, fake followers,
    and seeded views (likes per view below the band). Pod comments flag the creator but come from real accounts, so no discount."""
    excess = [0.0]
    for f in verdict(signals, norms)["flags"]:
        if f["signal"] in ("fake_likers", "fake_followers"):
            excess.append(f["value"] - f["median"])
        elif f["signal"] == "likes_per_view":
            excess.append(1 - f["value"] / f["median"])
    return round(1 - max(excess), 2)


FAKE_KINDS = ["flat_views", "flat_views_noise", "bot_likers", "pod_comments", "bought_followers", "smart_fake"]
_POD_TEXTS = ["Great content 🔥", "Amazing 😍", "Nice post", "Wow", "Superb 👏"]
_SMART_TOPICS = ["transition", "colour grade", "hook", "ending", "background score", "outfit", "voiceover", "framing"]


def _bot(rng) -> dict:
    return {"pk": str(rng.integers(10**9, 10**10)), "username": f"user{rng.integers(10**7, 10**8)}", "full_name": "", "has_pic": False,
            "is_private": False, "is_verified": False}


def make_fake(snapshot: dict, kind: str, rng) -> dict:
    """A copy of a real creator's snapshot with one kind of fakery added. The smart fake is every kind, mild."""
    snap = copy.deepcopy(snapshot)
    d = snap["data"]
    reels = [r for r in d["reels"] if not r["pinned"]]
    typical = median(r["views"] for r in reels)
    smart = kind == "smart_fake"
    if kind in ("flat_views", "flat_views_noise") or smart:
        for r in reels:
            if smart:
                r["views"] = int(0.5 * r["views"] + 0.5 * typical * rng.uniform(0.85, 1.15))
            else:
                r["views"] = int(typical * (rng.uniform(0.9, 1.1) if kind == "flat_views_noise" else 1))
    if kind == "bot_likers" or smart:
        share = 0.25 if smart else 0.5
        for rid, accounts in d["likers"].items():
            n = int(len(accounts) * share)
            d["likers"][rid] = [_bot(rng) for _ in range(n)] + accounts[n:]
        for r in reels:
            r["likes"] = int(r["likes"] / (1 - share))  # bought likes on top of the real ones
    if kind == "pod_comments" or smart:
        members = [{"pk": f"pod{m}", "username": f"pod.member{m}", "full_name": "Rahul Verma", "has_pic": True, "is_private": False, "is_verified": False}
                   for m in range(5 if smart else 12)]
        reel_ids = list(d["comments"])
        for rid in reel_ids[: math.ceil(len(reel_ids) * (0.6 if smart else 0.8))]:
            for m, user in enumerate(members):
                text = f"the {_SMART_TOPICS[(m + len(rid)) % 8]} at {rng.integers(2, 40)}s is so well done" if smart else str(rng.choice(_POD_TEXTS))
                d["comments"][rid].append({"text": text, "user": user, "at": "", "likes": 0})
    if kind == "bought_followers" or smart:
        mult, share = (1.5, 0.3) if smart else (3, 0.7)
        snap["followers"] = int(snap["followers"] * mult)
        n = int(len(d["followers"]) * share)
        d["followers"] = [_bot(rng) for _ in range(n)] + d["followers"][n:]
    return snap


def redteam(snapshots: list[dict], fake_model, embed, seed: int = 7) -> dict:
    """Catch rate per fake kind (verdict other than Real audience), the median genuine share each gets, and how many
    unmodified creators are flagged. Norms come from the unmodified creators."""
    rng = np.random.default_rng(seed)

    def signals(snap):
        return audience_signals(snap, reel_metrics(snap), fake_model, embed)

    base = [signals(s) for s in snapshots]
    norms = band_norms(base)
    caught, shares = {}, {}
    for kind in FAKE_KINDS:
        fakes = [signals(make_fake(s, kind, rng)) for s in snapshots]
        caught[kind] = round(float(np.mean([verdict(f, norms)["verdict"] != VERDICTS[0] for f in fakes])), 3)
        shares[kind] = float(median(genuine_share(f, norms) for f in fakes))
    return {
        "n": len(snapshots),
        "unmodified_flagged": round(float(np.mean([verdict(b, norms)["verdict"] != VERDICTS[0] for b in base])), 3),
        "caught": caught,
        "genuine_share": shares,
    }


_PROMO = re.compile(r"\b(code|coupon|discount|link in bio|use my|shop now|available (on|at)|order now|buy now)\b", re.IGNORECASE)


def ambiguous(reel: dict) -> bool:
    """Not an ad by the rules, but something in it could be one: a co-author, a tag, a mention or promo words."""
    return not is_paid(reel) and bool(reel["coauthors"] or reel.get("tags") or "@" in reel["caption"] or _PROMO.search(reel["caption"]))


def top_commenters(comments_by_reel: dict[str, list[dict]], n: int = 15) -> list[dict]:
    counts: dict[str, list] = {}
    for cs in comments_by_reel.values():
        for c in cs:
            counts.setdefault(c["user"]["username"], [0, c["user"]])[0] += 1
    return [user for _, user in sorted(counts.values(), key=lambda x: (-x[0], x[1]["username"]))[:n]]


_LABEL_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "reels": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "code": {"type": "STRING"}, "ad": {"type": "BOOLEAN"}, "topic": {"type": "STRING", "enum": list(CATEGORIES)}}, "required": ["code", "ad", "topic"]}},
        "accounts": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "username": {"type": "STRING"}, "kind": {"type": "STRING", "enum": ["person", "creator", "brand"]}}, "required": ["username", "kind"]}},
        "languages": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "language": {"type": "STRING"}, "share": {"type": "NUMBER"}}, "required": ["language", "share"]}},
    },
    "required": ["reels", "accounts", "languages"],
}


def label_creator(llm, snapshot: dict, images: dict[str, bytes]) -> dict:
    """One Gemini call: hidden ads among the ambiguous reels (covers attached), every reel's topic, who the co-authors and
    top commenters are, and the comment languages. No price goes in."""
    d = snapshot["data"]
    reels = recent_reels(snapshot)
    unclear = [r["code"] for r in reels if ambiguous(r)]
    with_cover = [code for code in unclear if code in images]
    tagged = d.get("tagged", [])
    accounts = list(dict.fromkeys(sorted({c for r in reels for c in r["coauthors"]}) + [t["owner"] for t in tagged] + [u["username"] for u in top_commenters(d["comments"])]))
    comments = [c["text"][:200] for cs in d["comments"].values() for c in cs][:80]
    reel_lines = "\n".join(f"{r['code']} | {r['caption'][:300]!r} | co-authors: {', '.join(r['coauthors']) or '-'} | tagged: {', '.join(r.get('tags', [])) or '-'}" for r in reels)
    tagged_lines = "\n".join(f"{t['code']} | by @{t['owner']} | {t['caption'][:200]!r}" for t in tagged)
    prompt = (
        "You label an Instagram creator's content for an influencer-marketing team.\n"
        "1. For each reel and tagged post: is it an ad (a paid promotion of a brand, product or app, even without #ad)? And its topic.\n"
        "2. For each account: a person, a creator (an influencer or public page) or a brand.\n"
        "3. The languages the comments are written in, as shares adding to 1. Romanised Hindi counts as Hinglish.\n\n"
        f"Bio: {d['profile'].get('bio', '')}\n\nReels (code | caption | co-authors | tagged):\n{reel_lines}\n\n"
        + (f"Posts by other accounts that tag this creator (code | owner | caption):\n{tagged_lines}\n\n" if tagged else "")
        + f"Accounts: {', '.join(accounts) or '-'}\n\nComments:\n" + "\n".join(f"- {c}" for c in comments)
        + (f"\n\nCover images follow, in this order: {', '.join(with_cover)}" if with_cover else "")
    )
    reply = llm.json(prompt, _LABEL_SCHEMA, images=[images[code] for code in with_cover])
    return {
        "ads": [r["code"] for r in reply["reels"] if r["ad"] and r["code"] in unclear],
        "topics": {r["code"]: r["topic"] for r in reply["reels"]},
        "kinds": {a["username"]: a["kind"] for a in reply["accounts"]},
        "languages": sorted(reply["languages"], key=lambda x: -x["share"]),
    }


def commenter_mix(snapshot: dict, fake_model, labels: dict) -> dict:
    """The top commenters, each counted once as fake-looking, a brand, a creator (verified or labelled) or a person."""
    top = top_commenters(snapshot["data"]["comments"])
    fake = fake_model.predict([account_features(u) for u in top]) if top else []
    kinds = labels.get("kinds", {})
    mix = {"top": len(top), "fake": 0, "brands": 0, "creators": 0, "people": 0}
    for user, is_fake in zip(top, fake):
        kind = kinds.get(user["username"])
        key = "fake" if is_fake else "brands" if kind == "brand" else "creators" if user.get("is_verified") or kind == "creator" else "people"
        mix[key] += 1
    return mix | {"languages": labels.get("languages", [])}


FACE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite"
# Out of scope below this: fewer than 2 of 10 covers with a face. A food creator showed 2 of 10, so stricter rejects real ones.
FACE_SHARE = 0.15


@lru_cache
def _face_detector():
    import httpx
    from mediapipe.tasks.python import BaseOptions, vision

    from truerate.config import MODELS_DIR

    path = MODELS_DIR / "blaze_face_short_range.tflite"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(httpx.get(FACE_MODEL_URL, timeout=60).raise_for_status().content)
    return vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(base_options=BaseOptions(model_asset_path=str(path)), min_detection_confidence=0.5))


def has_face(image: bytes) -> bool:
    import io

    import mediapipe as mp
    from PIL import Image

    rgb = np.asarray(Image.open(io.BytesIO(image)).convert("RGB"))
    return bool(_face_detector().detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)).detections)


def face_share(covers: dict[str, bytes], detect=has_face) -> float | None:
    """Share of reel covers with a face. None without covers to check."""
    if not covers:
        return None
    return round(sum(detect(img) for img in covers.values()) / len(covers), 2)


RING_MIN_SHARED = 3  # two creators are linked when at least this many accounts comment on both


def commenter_rings(commenters_by_creator: dict[str, set[str]]) -> dict[str, int]:
    """Louvain communities on the graph of creators linked by shared commenters. Each creator's ring size is how many
    other creators sit in its community. Pods use real accounts, so the shared accounts are what give them away."""
    import networkx as nx

    graph = nx.Graph()
    graph.add_nodes_from(commenters_by_creator)
    names = sorted(commenters_by_creator)
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            shared = len(commenters_by_creator[a] & commenters_by_creator[b])
            if shared >= RING_MIN_SHARED:
                graph.add_edge(a, b, weight=shared)
    return {c: len(group) - 1 for group in nx.community.louvain_communities(graph, weight="weight", seed=42) for c in group}


_ANOMALY_SIGNALS = ["fake_likers", "likes_per_view", "views_cv", "likes_cv", "fake_followers", "views_per_follower", "generic_comments", "repeat_commenters"]


def _anomaly_row(signals: dict) -> list[float]:
    return [_scale(signals.get(s) or 0, AUDIENCE_SIGNALS[s][2]) for s in _ANOMALY_SIGNALS]


def fit_anomaly(rows: list[dict]):
    """IsolationForest over WLDD creators' signals: finds fakes shaped in ways no single check predicts."""
    from sklearn.ensemble import IsolationForest

    return IsolationForest(contamination=0.05, random_state=42).fit([_anomaly_row(r) for r in rows])


def audience_warnings(signals: dict, forest) -> list[str]:
    """Things that don't change the verdict but a buyer should know."""
    out = []
    if signals.get("former_usernames"):
        out.append(f"Changed username {signals['former_usernames']} times")
    if forest.predict([_anomaly_row(signals)])[0] == -1:
        out.append("Unusual overall pattern compared with WLDD's creators")
    return out
