from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import joblib
import typer

from truerate.config import REPO_ROOT, get_settings
from truerate.db import ensure_indexes, get_db, import_deals
from truerate.instagram import Hiker, HikerError, collect
from truerate.llm import Gemini
from truerate.signals import category_from_niche, label_niche, load_kaggle, reel_metrics, train_fake_model

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """TrueRate data, model and validation commands."""


@app.command("import-deals")
def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
    db = get_db()
    ensure_indexes(db)
    counts = import_deals(db, csv_path)
    typer.echo(f"Imported {counts['deals']} deals ({counts['holdout']} held out)")


@app.command("build-fake-model")
def build_fake_model_cmd(
    kaggle_dir: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "external" / "instagram_fake",
    out: Path = REPO_ROOT / "data" / "models" / "fake_accounts.joblib",
) -> None:
    model = train_fake_model(*load_kaggle(kaggle_dir / "train.csv"))
    X_test, y_test = load_kaggle(kaggle_dir / "test.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out)
    typer.echo(f"Fake-account model: {model.score(X_test, y_test):.0%} on {len(y_test)} held-out Kaggle accounts. Saved {out}")


def make_hiker(db) -> Hiker:
    return Hiker(get_settings().hikerapi_key, db)


@app.command("collect")
def collect_cmd(handle: str) -> None:
    db = get_db()
    ensure_indexes(db)
    snap = collect(make_hiker(db), handle.lstrip("@").lower())
    db.snapshots.insert_one(snap)
    d = snap["data"]
    if "reels" not in d:
        typer.echo(f"{snap['handle']}: private, stopped at the profile")
        return
    typer.echo(
        f"{snap['handle']}: {snap['followers']:,} followers, {len(d['reels'])} reels, "
        f"{sum(map(len, d['comments'].values()))} comments on {len(d['comments'])} reels, "
        f"{sum(map(len, d['likers'].values()))} likers on {len(d['likers'])} reels, "
        f"{len(d['followers'])} newest followers, {len(d['suggested'])} suggested"
    )


@app.command("collect-benchmark")
def collect_benchmark_cmd() -> None:
    """Snapshot every deal creator, skipping any fetched in the last 24 h. Stops when HikerAPI credit runs out."""
    db = get_db()
    ensure_indexes(db)
    hiker = make_hiker(db)
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    done = skipped = failed = 0
    for deal in db.deals.find({}, {"handle": 1}).sort("handle"):
        handle = deal["handle"]
        if db.snapshots.find_one({"handle": handle, "fetched_at": {"$gt": since}}):
            skipped += 1
            continue
        try:
            db.snapshots.insert_one(collect(hiker, handle))
            done += 1
        except HikerError as e:
            typer.echo(f"{handle}: {e}")
            if e.status == 402:
                raise typer.Exit(1)
            failed += 1
    typer.echo(f"Collected {done}, skipped {skipped} fetched in the last 24 h, failed {failed}")


def make_llm() -> Gemini:
    settings = get_settings()
    return Gemini(settings.llm_api_key, settings.llm_model)


@app.command("build-metrics")
def build_metrics_cmd() -> None:
    """Metrics and category for every deal creator, from their latest snapshot."""
    db = get_db()
    llm = None
    built = skipped = 0
    for deal in db.deals.find().sort("handle"):
        handle = deal["handle"]
        snap = db.snapshots.find_one({"handle": handle}, sort=[("fetched_at", -1)])
        if not snap or "reels" not in snap["data"] or reel_metrics(snap)["n_reels"] < 12:
            skipped += 1
            continue
        metrics = reel_metrics(snap)
        stored = db.metrics.find_one({"_id": handle}) or {}
        if category := category_from_niche(deal["niche"]):
            source = "wldd"
        elif stored.get("category_source") == "gemini":
            category, source = stored["category"], "gemini"
        else:
            llm = llm or make_llm()
            captions = [r["caption"] for r in sorted(snap["data"]["reels"], key=lambda r: r["taken_at"], reverse=True)]
            category, source = label_niche(llm, snap["data"]["profile"].get("bio", ""), captions), "gemini"
        db.metrics.replace_one({"_id": handle}, {**metrics, "category": category, "category_source": source, "computed_at": datetime.now(timezone.utc)}, upsert=True)
        built += 1
    typer.echo(f"Built metrics for {built} creators; skipped {skipped} without a snapshot of 12+ reels")
