import csv
import random
from collections import defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from truerate.config import get_settings

ACCOUNTS_TTL_SECONDS = 30 * 24 * 3600
HOLDOUT_PER_TIER = 10
SEED = 42


@lru_cache
def _client(uri: str) -> MongoClient:
    return MongoClient(uri)


def get_db() -> Database:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise RuntimeError("Set MONGODB_URI in .env")
    return _client(settings.mongodb_uri)[settings.mongodb_db]


def ensure_indexes(db: Database) -> None:
    db.deals.create_index("handle", unique=True)
    db.snapshots.create_index([("handle", ASCENDING), ("fetched_at", DESCENDING)])
    db.accounts.create_index("fetched_at", expireAfterSeconds=ACCOUNTS_TTL_SECONDS)
    db.analyses.create_index([("created_at", DESCENDING)])
    db.analyses.create_index("batch_id")


def import_deals(db: Database, csv_path: Path, holdout_share: float | None = None, exclude: set[str] | None = None) -> dict[str, int]:
    """Replaces the deals with the CSV's. Held out: HOLDOUT_PER_TIER per tier, or, with `holdout_share`, that share of
    each tier drawn only from creators not in `exclude` (the ones the served model was trained on, so it can be
    scored fairly on the same held-out set). A `payout_date` column is kept as a date; `paid` is ignored."""
    with csv_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    exclude = exclude or set()
    handles_by_tier: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        handles_by_tier[row["tier"]].append(row["handle"].strip().lower())
    rng = random.Random(SEED)
    holdout: set[str] = set()
    for tier in sorted(handles_by_tier):
        handles = sorted(handles_by_tier[tier])
        if holdout_share is None:
            holdout.update(rng.sample(handles, min(HOLDOUT_PER_TIER, len(handles))))
        else:
            eligible = [h for h in handles if h not in exclude]
            holdout.update(rng.sample(eligible, min(round(holdout_share * len(handles)), len(eligible))))
    docs = []
    for row in rows:
        handle = row["handle"].strip().lower()
        doc = {
            "handle": handle,
            "tier": row["tier"],
            "niche": [g.strip() for g in (row.get("niche") or "").split(",") if g.strip()],
            "price": int(float(row["price"])),
            "holdout": handle in holdout,
        }
        if row.get("payout_date"):
            doc["payout_date"] = datetime.strptime(row["payout_date"].strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        docs.append(doc)
    db.deals.delete_many({})
    db.deals.insert_many(docs)
    return {"deals": len(docs), "holdout": len(holdout)}


def training_rows(db: Database) -> list[dict]:
    """Every deal that has metrics, as one flat row: the metrics plus handle, price and holdout."""
    deals = {d["handle"]: d for d in db.deals.find()}
    return [
        {**{k: v for k, v in m.items() if k not in ("_id", "computed_at")}, "handle": m["_id"], "price": deals[m["_id"]]["price"], "holdout": deals[m["_id"]]["holdout"]}
        for m in db.metrics.find().sort("_id")
        if m["_id"] in deals
    ]
