import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import json

import joblib
import typer

from truerate.config import HIKER_DIR, MODELS_DIR, REPO_ROOT, get_settings
from truerate.db import ensure_indexes, get_db, import_deals, training_rows
from truerate.instagram import Hiker, HikerError, collect, fetch_covers
from truerate.llm import Gemini
from truerate.pricing import fit, validate
from truerate.signals import (
    ambiguous,
    audience_signals,
    category_from_niche,
    commenter_mix,
    WINDOW_DAYS,
    commenter_rings,
    deal_window_metrics,
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
def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv",
                     holdout_share: float | None = None, exclude: Path | None = None) -> None:
    """`--holdout-share 0.1 --exclude data/creators.csv`: hold out 10% of each tier, never a creator in `--exclude`."""
    db = get_db()
    ensure_indexes(db)
    skip = {r["handle"].strip().lower() for r in csv.DictReader(exclude.open(newline=""))} if exclude else set()
    counts = import_deals(db, csv_path, holdout_share, skip)
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


def make_hiker() -> Hiker:
    return Hiker(get_settings().hikerapi_key, HIKER_DIR)


@app.command("collect")
def collect_cmd(handle: str) -> None:
    db = get_db()
    ensure_indexes(db)
    snap = collect(make_hiker(), handle.lstrip("@").lower())
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
def collect_benchmark_cmd(workers: int = 1, fresh_hours: int = 24) -> None:
    """Snapshot every deal creator, skipping any fetched in the last `fresh_hours`, `workers` at a time. With
    `--fresh-hours 0` every creator is snapshotted again; saved HikerAPI responses make that nearly free.
    A failed creator is reported and skipped; running out of HikerAPI credit (402) stops the run."""
    db = get_db()
    ensure_indexes(db)
    hiker = make_hiker()
    since = datetime.now(timezone.utc) - timedelta(hours=fresh_hours)
    deals = list(db.deals.find({}, {"handle": 1, "payout_date": 1}).sort("handle"))
    handles = [d["handle"] for d in deals]
    # A dated deal's reels reach back WINDOW_DAYS before its payout, as `scripts/collect_deals.py` saved them.
    back_to = {d["handle"]: d["payout_date"].replace(tzinfo=timezone.utc) - timedelta(days=WINDOW_DAYS) if d.get("payout_date") else None for d in deals}
    todo = [h for h in handles if not db.snapshots.find_one({"handle": h, "fetched_at": {"$gt": since}})]
    done = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(collect, hiker, h, back_to=back_to[h]): h for h in todo}
        for future in as_completed(futures):
            handle = futures[future]
            try:
                snap = future.result()
            except HikerError as e:
                typer.echo(f"{handle}: {e}")
                if e.status == 402:
                    pool.shutdown(cancel_futures=True)
                    raise typer.Exit(1)
                failed += 1
                continue
            except Exception as e:  # one creator's timeout or odd profile must not stop a 3,000-request run
                typer.echo(f"{handle}: {e}")
                failed += 1
                continue
            db.snapshots.insert_one(snap)
            done += 1
            typer.echo(f"[{done + failed}/{len(todo)}] {handle}: {snap['followers']:,} followers, {len(snap['data'].get('reels', []))} reels")
    typer.echo(f"Collected {done}, skipped {len(handles) - len(todo)} fetched in the last {fresh_hours} h, failed {failed}")


def load_fake_model():
    return joblib.load(MODELS_DIR / "fake_accounts.joblib")


def make_llm() -> Gemini:
    settings = get_settings()
    return Gemini(settings.llm_api_key, settings.llm_model)


@app.command("build-metrics")
def build_metrics_cmd(workers: int = 1) -> None:
    """Metrics, category and audience signals for every deal creator, from their latest snapshot. The Gemini and cover
    calls run `workers` at a time; a creator whose call fails is reported and skipped."""
    db = get_db()
    fake_model = load_fake_model()
    items, skipped = [], 0
    for deal in db.deals.find().sort("handle"):
        snap = db.snapshots.find_one({"handle": deal["handle"]}, sort=[("fetched_at", -1)])
        if not snap or "reels" not in snap["data"] or len(recent_reels(snap)) < 12:
            skipped += 1
            continue
        # Saved Gemini labels live in `labels`; older runs kept them in `metrics`.
        items.append((deal, snap, db.labels.find_one({"_id": deal["handle"]}) or db.metrics.find_one({"_id": deal["handle"]}) or {}))
    llm = make_llm() if items else None

    def label(item):
        """Gemini labels and the category; stored ones are reused while the snapshot is the same."""
        deal, snap, stored = item
        if stored.get("labels_for") == snap["_id"]:
            labels = stored["labels"]
        else:
            labels = label_creator(llm, snap, fetch_covers([r for r in recent_reels(snap) if ambiguous(r)]))
        if category := category_from_niche(deal["niche"]):
            return labels, category, "wldd"
        if stored.get("category_source") == "gemini":
            return labels, stored["category"], "gemini"
        captions = [r["caption"] for r in sorted(snap["data"]["reels"], key=lambda r: r["taken_at"], reverse=True)]
        return labels, label_niche(llm, snap["data"]["profile"].get("bio", ""), captions), "gemini"

    def safe_label(item):
        try:
            labels, category, source = out = label(item)
        except Exception as e:  # one creator's Gemini error must not stop the other 149
            return e
        # Saved as soon as it exists, so a crash later in the run never loses Gemini's work.
        deal, snap, _ = item
        db.labels.replace_one({"_id": deal["handle"]}, {"labels": labels, "labels_for": snap["_id"], "category": category, "category_source": source}, upsert=True)
        return out

    with ThreadPoolExecutor(max_workers=workers) as pool:
        labelled = list(pool.map(safe_label, items))
    built = failed = 0
    for (deal, snap, _), out in zip(items, labelled):
        handle = deal["handle"]
        if isinstance(out, Exception):
            typer.echo(f"{handle}: {out}")
            failed += 1
            continue
        labels, category, source = out
        try:
            metrics = reel_metrics(snap, labels)
            audience = audience_signals(snap, metrics, fake_model, minilm_embed)
            mix = commenter_mix(snap, fake_model, labels)
        except Exception as e:  # one odd page must not stop the rest
            typer.echo(f"{handle}: {e}")
            failed += 1
            continue
        commenters = sorted({c["user"]["username"] for cs in snap["data"]["comments"].values() for c in cs})
        doc = {**metrics, **audience, "mix": mix, "labels": labels, "labels_for": snap["_id"], "commenters": commenters,
               "category": category, "category_source": source, "computed_at": datetime.now(timezone.utc)}
        if deal.get("payout_date"):  # what the creator was delivering when WLDD paid them, beside today's numbers
            doc |= deal_window_metrics(snap, deal["payout_date"])
        db.metrics.replace_one({"_id": handle}, doc, upsert=True)
        built += 1
    rings = commenter_rings({m["_id"]: set(m["commenters"]) for m in db.metrics.find({}, {"commenters": 1})})
    for handle, size in rings.items():
        db.metrics.update_one({"_id": handle}, {"$set": {"ring_size": size}})
    typer.echo(f"Built metrics for {built} creators; skipped {skipped} without a snapshot of 12+ reels" + (f"; failed {failed}" if failed else ""))


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


@app.command("experiment")
def experiment_cmd(out_dir: Path = REPO_ROOT / "data" / "models" / "experiments", fresh_csv: Path = REPO_ROOT / "data" / "fresh_test_20.csv",
                   repeats: int = 5, points: str = "", no_fresh: bool = False, dated: bool = False, live_model: Path | None = None) -> None:
    """Model v2 experiments: candidates picked by repeated CV on the training deals, then scored once on the held-out and
    fresh deals. Writes the before/after table, results.json and the graphs; the served model is left alone.
    `--points today,ridge_v2` limits the candidates (default: all; today's model is always one). `--no-fresh` scores the held-out
    deals only; `--dated` uses each deal's stats from the 90 days before its payout; `--live-model data/models/price.joblib` also
    scores the model the app serves now on the held-out deals, as the app prices them (today's stats)."""
    import csv

    from truerate import experiment as ex
    from truerate import experiment_plots as plots
    from truerate.app import parse_handle

    db = get_db()
    today = ex.deal_rows(db)
    rows = ex.dated(today) if dated else today
    if no_fresh:
        fresh = []
        typer.echo(f"{len(rows)} deals; no fresh deals" + (f"; {sum(r.get('views_then') is not None for r in rows)} with stats around the payout" if dated else ""))
    else:
        with fresh_csv.open(newline="") as f:
            prices = {h: float(r["price"].replace(",", "")) for r in csv.DictReader(f) if (h := parse_handle(r["handle"]))}
        fresh = ex.fresh_rows(db, prices)
        typer.echo(f"{len(rows)} deals; {len(fresh)} of {len(prices)} fresh deals have a finished analysis")
    train, holdout = [r for r in rows if not r["holdout"]], [r for r in rows if r["holdout"]]
    chosen = tuple(dict.fromkeys(("today", *points.split(",")))) if points else ex.POINTS
    result = ex.run(train, holdout, fresh, repeats=repeats, points=chosen)
    picked, test = result["picked"]["price"], holdout + fresh
    if live_model:
        result["live"] = ex.live_scores(joblib.load(live_model), [r for r in today if r["holdout"]])
    sizes = tuple(sorted({s for s in (30, 60, 120, 250, 500, 800) if s < len(train)} | {len(train)}))
    curves = {n: ex.learning_curve(n, train, test, sizes) for n in dict.fromkeys(("today", picked))}
    # The ensemble mixes models whose importances are in different units (SHAP in log price, a drop in R²), so it has none.
    imp = {n: ex.importance(n, rows) for n in dict.fromkeys((picked, "ridge_v2")) if n != "ensemble"}
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(result | {"learning_curve": curves, "importance": imp}, indent=1))
    (out_dir / "table.md").write_text(ex.report_table(result))
    names = ("Today, as served", f"{result['picked']['range']}, {'adopted' if result['adopt'] else 'not adopted'}")
    plots.predicted_vs_actual(result, names, out_dir / "predicted_vs_actual.png")
    plots.ranges(result, names, out_dir / "ranges.png")
    for n, values in imp.items():
        plots.importance(values, f"What moves the price in {n}, fitted on all {len(rows)} deals", out_dir / f"importance_{n}.png",
                         permutation=n in ex.PERMUTATION)
    plots.learning(curves, {n: n for n in curves}, len(test), out_dir / "learning_curve.png")
    typer.echo(ex.report_table(result))


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
