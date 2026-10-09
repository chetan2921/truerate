"""Seeds the dev database and dev models with synthetic data from the pipeline tests' world, for building screens
before the 150 real creators are collected. Never touches the real database or data/models.

    cd api && uv run python scripts/seed_dev.py
    MONGODB_DB=truerate_dev MODELS_DIR=data/models_dev uv run uvicorn truerate.app:app --port 8000
"""

import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import mongomock
import numpy as np
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from test_audience import fake_embed, genuine_snapshot  # noqa: E402
from test_pipeline import FAKE_MODEL, deps, target_snapshot  # noqa: E402
from test_pricing import synthetic_rows  # noqa: E402

from truerate.config import REPO_ROOT, get_settings  # noqa: E402
from truerate.db import ensure_indexes  # noqa: E402
from truerate.pipeline import analyze  # noqa: E402
from truerate.pricing import fit, validate  # noqa: E402
from truerate.signals import audience_signals, make_fake, redteam, reel_metrics  # noqa: E402

DEV_DB = "truerate_dev"
DEV_MODELS = REPO_ROOT / "data" / "models_dev"

world = mongomock.MongoClient().world
ensure_indexes(world)
rng = np.random.default_rng(5)
wldd = [genuine_snapshot(i, rng) for i in range(30)]
for s in wldd:
    m = reel_metrics(s)
    commenters = sorted({c["user"]["username"] for cs in s["data"]["comments"].values() for c in cs})
    world.metrics.insert_one({"_id": s["handle"], **m, **audience_signals(s, m, FAKE_MODEL, fake_embed), "commenters": commenters, "category": "Food"})


def snap_for(handle, seed):
    s = target_snapshot(handle, seed)
    for j, r in enumerate(s["data"]["reels"]):
        if j in (4, 11, 19):
            r["paid"], r["sponsors"] = True, [f"brand{j}"]
        if j in (7, 15):
            r["coauthors"] = ["friend.creator"]
    for k, days in enumerate((60, 30, 10)):  # earlier snapshots, so the follower line has history
        world.snapshots.insert_one({"handle": handle, "fetched_at": datetime.now(timezone.utc) - timedelta(days=days),
                                    "followers": int(s["followers"] * (0.9 + 0.03 * k)), "data": {}})
    return s


db = MongoClient(get_settings().mongodb_uri)[DEV_DB]
db.analyses.delete_many({})
now = datetime.now(timezone.utc)


def save(aid, handle, inputs, out, minutes):
    db.analyses.insert_one({"_id": aid, "handle": handle, "inputs": {"category": None, "quote": None, "budget": None} | inputs, "status": out["status"],
                            "step": 3, "result": out.get("result"), "reason": out.get("reason"),
                            "created_at": now - timedelta(minutes=minutes), "finished_at": now - timedelta(minutes=minutes - 1)})


out = analyze("asha.cooks", {}, deps(world, snap_for("asha.cooks", 99)))
save("demo-go", "asha.cooks", {}, out, 50)
save("demo-competitor", "asha.cooks", {"category": "Food"}, analyze("asha.cooks", {"category": "Food"}, deps(world, snap_for("asha.cooks", 99))), 45)
quote = out["result"]["price"]["high"] * 2
save("demo-quote", "asha.cooks", {"quote": quote}, analyze("asha.cooks", {"quote": quote}, deps(world, snap_for("asha.cooks", 99))), 40)
fake = make_fake(make_fake(snap_for("bought.buzz", 77), "bot_likers", np.random.default_rng(1)), "pod_comments", np.random.default_rng(2))
fake["handle"] = "bought.buzz"
save("demo-fake", "bought.buzz", {}, analyze("bought.buzz", {}, deps(world, fake)), 30)
save("demo-private", "private.page", {}, {"status": "out_of_scope", "reason": "@private.page is private, so its reels and audience can't be read."}, 20)
db.analyses.insert_one({"_id": "demo-failed", "handle": "credit.gone", "inputs": {}, "status": "failed", "step": 0,
                        "error": "HikerAPI 402 on /v1/user/by/username: Top up your account", "created_at": now - timedelta(minutes=10)})
db.analyses.insert_one({"_id": "demo-running", "handle": "still.working", "inputs": {}, "status": "running", "step": 2, "created_at": now - timedelta(minutes=1)})

# A shortlist made of the demo analyses, for the batch table.
db.batches.delete_many({})
db.batches.insert_one({"_id": "demo-batch", "inputs": {"category": None, "quote": None, "budget": 22000}, "handles": [], "created_at": now})
db.analyses.update_many({"_id": {"$in": ["demo-go", "demo-fake", "demo-private", "demo-running"]}}, {"$set": {"batch_id": "demo-batch"}})

# Synthetic models and reports, so the rate card and About have something to show.
DEV_MODELS.mkdir(parents=True, exist_ok=True)
rows = synthetic_rows()
joblib.dump(fit(rows), DEV_MODELS / "price.joblib")
(DEV_MODELS / "model_report.json").write_text(json.dumps(validate(rows), indent=1))
(DEV_MODELS / "redteam.json").write_text(json.dumps(redteam(wldd, FAKE_MODEL, fake_embed), indent=1))
real_fake = REPO_ROOT / "data" / "models" / "fake_accounts.joblib"
if real_fake.exists():
    shutil.copy(real_fake, DEV_MODELS / "fake_accounts.joblib")
print(f"Seeded {db.analyses.count_documents({})} analyses into {DEV_DB} and synthetic models into {DEV_MODELS}")
