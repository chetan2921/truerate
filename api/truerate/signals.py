import csv
from pathlib import Path

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
