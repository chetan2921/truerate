from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import json

import joblib
import typer

from truerate.config import MODELS_DIR, REPO_ROOT, get_settings
from truerate.db import ensure_indexes, get_db, import_deals, training_rows
from truerate.instagram import Hiker, HikerError, collect, fetch_covers
from truerate.llm import Gemini
from truerate.pricing import fit, validate
from truerate.signals import (
    ambiguous,
    audience_signals,
    category_from_niche,
    commenter_mix,
    commenter_rings,
    label_creator,
    label_niche,
    load_kaggle,
    minilm_embed,
    recent_reels,
    redteam,
    reel_metrics,
    train_fake_model,
)

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


def load_fake_model():
    return joblib.load(MODELS_DIR / "fake_accounts.joblib")


def make_llm() -> Gemini:
    settings = get_settings()
    return Gemini(settings.llm_api_key, settings.llm_model)


@app.command("build-metrics")
def build_metrics_cmd() -> None:
    """Metrics, category and audience signals for every deal creator, from their latest snapshot."""
    db = get_db()
    llm = None
    fake_model = load_fake_model()
    built = skipped = 0
    for deal in db.deals.find().sort("handle"):
        handle = deal["handle"]
        snap = db.snapshots.find_one({"handle": handle}, sort=[("fetched_at", -1)])
        if not snap or "reels" not in snap["data"] or len(recent_reels(snap)) < 12:
            skipped += 1
            continue
        stored = db.metrics.find_one({"_id": handle}) or {}
        if stored.get("labels_for") == snap["_id"]:
            labels = stored["labels"]
        else:
            llm = llm or make_llm()
            labels = label_creator(llm, snap, fetch_covers([r for r in recent_reels(snap) if ambiguous(r)]))
        metrics = reel_metrics(snap, labels)
        if category := category_from_niche(deal["niche"]):
            source = "wldd"
        elif stored.get("category_source") == "gemini":
            category, source = stored["category"], "gemini"
        else:
            llm = llm or make_llm()
            captions = [r["caption"] for r in sorted(snap["data"]["reels"], key=lambda r: r["taken_at"], reverse=True)]
            category, source = label_niche(llm, snap["data"]["profile"].get("bio", ""), captions), "gemini"
        audience = audience_signals(snap, metrics, fake_model, minilm_embed)
        commenters = sorted({c["user"]["username"] for cs in snap["data"]["comments"].values() for c in cs})
        doc = {**metrics, **audience, "mix": commenter_mix(snap, fake_model, labels), "labels": labels, "labels_for": snap["_id"], "commenters": commenters,
               "category": category, "category_source": source, "computed_at": datetime.now(timezone.utc)}
        db.metrics.replace_one({"_id": handle}, doc, upsert=True)
        built += 1
    rings = commenter_rings({m["_id"]: set(m["commenters"]) for m in db.metrics.find({}, {"commenters": 1})})
    for handle, size in rings.items():
        db.metrics.update_one({"_id": handle}, {"$set": {"ring_size": size}})
    typer.echo(f"Built metrics for {built} creators; skipped {skipped} without a snapshot of 12+ reels")


@app.command("validate")
def validate_cmd(out_dir: Path = REPO_ROOT / "data" / "models") -> None:
    """Holdout and per-category accuracy against both baselines, then the served price model."""
    rows = training_rows(get_db())
    report = validate(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "model_report.json").write_text(json.dumps(report, indent=1))
    # The holdout numbers come from a model that never saw those 30; the served model learns from every deal.
    joblib.dump(fit(rows), out_dir / "price.joblib")
    h = report["holdout"]
    typer.echo(
        f"Holdout ({h['n']} creators) median error: model {h['model']['median_error']:.0%}, "
        f"band median {h['band_median']['median_error']:.0%}, Modash-style {h['modash']['median_error']:.0%}. "
        f"Range coverage {h['coverage']:.0%}"
    )
    for b, err in h["model"]["by_band"].items():
        typer.echo(f"  {b}: model {err:.0%}" if err is not None else f"  {b}: no holdout creators")
    for c, v in report["by_category"].items():
        typer.echo(f"  {c} ({v['n']}): model {v['model']:.0%}, band median {v['band_median']:.0%}, Modash-style {v['modash']:.0%}")


@app.command("redteam")
def redteam_cmd(out_dir: Path = MODELS_DIR) -> None:
    """Fakes built from every WLDD creator's latest snapshot: catch rate per kind, and how many real creators get flagged."""
    db = get_db()
    snaps = [db.snapshots.find_one({"handle": m["_id"]}, sort=[("fetched_at", -1)]) for m in db.metrics.find({}, {"_id": 1}).sort("_id")]
    report = redteam(snaps, load_fake_model(), minilm_embed)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "redteam.json").write_text(json.dumps(report, indent=1))
    typer.echo(f"Red-team on {report['n']} WLDD creators. Unmodified creators flagged: {report['unmodified_flagged']:.0%}")
    for kind, rate in report["caught"].items():
        typer.echo(f"  {kind}: caught {rate:.0%}, median genuine share {report['genuine_share'][kind]:.2f}")
