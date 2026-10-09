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


def reel_metrics(snapshot: dict) -> dict:
    """Stats over the last 30 unpinned reels with visible views. Own reels are neither paid nor co-authored."""
    reels = sorted((r for r in snapshot["data"]["reels"] if not r["pinned"] and r["views"] > 0), key=lambda r: r["taken_at"], reverse=True)[:30]
    paid = [r for r in reels if is_paid(r)]
    collab = [r for r in reels if r["coauthors"] and not is_paid(r)]
    own = [r for r in reels if not r["coauthors"] and not is_paid(r)]
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
    reels = sorted((r for r in d["reels"] if not r["pinned"] and r["views"] > 0), key=lambda r: r["taken_at"], reverse=True)[:30]
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
        if signals.get(s) is None:
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
