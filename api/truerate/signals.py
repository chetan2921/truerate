import csv
import re
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
    return sum(model.predict([account_features(a) for a in accounts])) / len(accounts)


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
