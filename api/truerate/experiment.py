"""Model v2 experiments (handoff step 2). Candidate price models and ranges are picked by repeated cross-validation on
the training deals only, then scored once on the 30 held-out deals and on the fresh test deals. Nothing returned holds a
handle; actual prices appear only in `points`, which stay in the git-ignored data/models/experiments/."""

import math
import re
from importlib.util import find_spec
from datetime import datetime, timezone
from functools import partial
from statistics import mean, median

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNetCV, RidgeCV
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from truerate.db import training_rows
from truerate.pricing import FACTOR_FLOOR, SHRINK, collab_factor, features, fit, price, round500
from truerate.signals import CATEGORIES, band, recent_reels, reel_metrics

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
LEVELS = (0.8, 0.5)
POINTS = ("today", "today_uncapped", "ridge_v2", "elasticnet_v2", "boosting_v2") + (("tabpfn_v2",) if find_spec("tabpfn") else ())
RANGES = ("global", "band", "local")
K_LOCAL = 15  # "local" ranges scale with the typical error among this many nearest training deals
BEFORE = "today_served"
BANDS = ("small", "medium", "big")
PERMUTATION = ("boosting_v2", "tabpfn_v2")  # not linear: importance is the drop in R² when a feature is shuffled, not SHAP
MIN_BAND = 15  # fewer deals than this in a follower band: its range comes from all deals
FEATURE_NAMES = (["log views", "log followers", "engagement", "comments per 1,000 views"] + list(CATEGORIES)
                 + ["account age", "log reel seconds", "log reels per month", "ads share", "YouTube link", "contact email", "verified",
                    "English comments", "views spread", "log trend", "likes per view"])


def extra_features(snap: dict) -> dict:
    """What today's model leaves out: account age, reel length, posting rate, a YouTube link, a contact email, the tick."""
    d, reels = snap["data"], recent_reels(snap)
    try:
        joined = datetime.strptime(d.get("about", {}).get("joined") or "", "%B %Y").replace(tzinfo=timezone.utc)
        age = (_utc(snap["fetched_at"]) - joined).days / 365.25
    except ValueError:
        age = None
    times = [datetime.fromisoformat(r["taken_at"].replace("Z", "+00:00")) for r in reels]
    days = (max(times) - min(times)).total_seconds() / 86400 if times else 0
    seconds = [r["duration"] for r in reels if r.get("duration")]
    p = d["profile"]
    return {
        "age_years": age,
        "reel_seconds": median(seconds) if seconds else None,
        "reels_per_month": len(reels) / days * 30 if days else None,
        "youtube": "youtu" in (p.get("external_url") or "").lower(),
        "email": bool(EMAIL.search(p.get("bio") or "")),
        "verified": bool(p.get("is_verified")),
    }


def _utc(t: datetime) -> datetime:
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)


def _with_extras(row: dict, snap: dict, mix: dict | None) -> dict:
    langs = (mix or {}).get("languages") or []
    english = next((x["share"] for x in langs if x["language"] == "English"), 0.0) if langs else None
    return row | extra_features(snap) | {"english": english}


def deal_rows(db) -> list[dict]:
    """Every deal with metrics, plus the new features from the snapshot those metrics came from."""
    return [_with_extras(r, db.snapshots.find_one({"_id": r["labels_for"]}), r.get("mix")) for r in training_rows(db)]


def fresh_rows(db, prices: dict[str, float]) -> list[dict]:
    """Test deals with creators analysed live, as each latest finished analysis priced them: the snapshot it read, and
    its paid reels as the report listed them, give back the exact metrics without a new Gemini call."""
    rows = []
    for handle, paid in prices.items():
        a = db.analyses.find_one({"handle": handle, "status": "done"}, sort=[("created_at", -1)])
        if not a:
            continue
        r = a["result"]
        at = datetime.fromisoformat(r["fetched_at"]).astimezone(timezone.utc)
        snap = min(db.snapshots.find({"handle": handle}), key=lambda s: abs(_utc(s["fetched_at"]) - at), default=None)
        if not snap or abs(_utc(snap["fetched_at"]) - at).total_seconds() > 2:
            continue
        m = reel_metrics(snap, {"ads": [x["code"] for x in r["placement"]["reels"] if x["kind"] == "paid"]})
        rows.append(_with_extras(r["audience"]["signals"] | m, snap, r["audience"]["mix"])
                    | {"handle": handle, "price": paid, "category": r["category"], "holdout": False})
    return rows


def _num(x) -> float:
    return math.nan if x is None else float(x)


def _log(x) -> float:
    return math.log(x) if x else math.nan


def features_v2(m: dict) -> list[float]:
    n = m.get("n_reels")
    return features(m) + [_num(m.get("age_years")), _log(m.get("reel_seconds")), _log(m.get("reels_per_month")),
                          m["paid_n"] / n if n else math.nan, _num(m.get("youtube")), _num(m.get("email")), _num(m.get("verified")),
                          _num(m.get("english")), _num(m.get("views_cv")), _log(m.get("trend")), _num(m.get("likes_per_view"))]


def _paid_typical(rows: list[dict]) -> float:
    ratios = [r["paid_ratio"] for r in rows if r["paid_n"]]
    return median(ratios) if ratios else 1.0


def _linear(regressor):
    return make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler(), regressor)


ESTIMATORS = {
    "ridge_v2": lambda: _linear(RidgeCV(alphas=np.logspace(-2, 3, 20))),
    "elasticnet_v2": lambda: _linear(ElasticNetCV(l1_ratio=[0.2, 0.5, 0.8, 1.0], cv=5, max_iter=20_000)),
    # Small and slow-learning, and never cheaper for more views or followers.
    "boosting_v2": lambda: HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_depth=2, min_samples_leaf=10, l2_regularization=1.0,
                                                         monotonic_cst=[1, 1] + [0] * (len(FEATURE_NAMES) - 2), random_state=0),
    "tabpfn_v2": lambda: _tabpfn(),
}


def _tabpfn():
    """Prior Labs' pretrained small-table model, run locally on the CPU. Pinned to the v2 weights: their licence
    (Apache 2.0 with attribution) allows commercial use, unlike the package's default weights. Never the cloud client:
    WLDD's prices stay on this machine."""
    from tabpfn import TabPFNRegressor
    from tabpfn.constants import ModelVersion

    return TabPFNRegressor.create_default_for_version(ModelVersion.V2, device="cpu", random_state=0)


def _sklearn_point(name: str, train: list[dict], test: list[dict]) -> np.ndarray:
    """Log price with the same sponsored-performance factor today's model applies."""
    est = ESTIMATORS[name]().fit(np.array([features_v2(r) for r in train]), np.log([r["price"] for r in train]))
    typical = _paid_typical(train)
    return est.predict(np.array([features_v2(r) for r in test])) + np.log([collab_factor(r["paid_n"], r["paid_ratio"], typical)[1] for r in test])


_FITS: dict = {}  # today's model per training set: its fit runs a leave-one-out, and the CV asks for the same set often


def _today(train: list[dict]):
    key = tuple((r["handle"], r["price"]) for r in train)
    if key not in _FITS:
        _FITS[key] = fit(train)
    return _FITS[key]


def _today_point(train: list[dict], test: list[dict], capped: bool = True) -> np.ndarray:
    """Today's fair price before rounding (`pricing.price`); uncapped, strong sponsored reach can also raise it."""
    model, out = _today(train), []
    for r in test:
        ridge_log, knn_log, _ = model.core.predict_logs(r)
        if capped:
            factor = collab_factor(r["paid_n"], r["paid_ratio"], model.paid_typical)[1]
        else:
            typical = model.paid_typical
            shrunk = (r["paid_n"] * r["paid_ratio"] + SHRINK * typical) / (r["paid_n"] + SHRINK) if r["paid_n"] else typical
            factor = max(shrunk / typical, FACTOR_FLOOR)
        out.append(model.w * ridge_log + (1 - model.w) * knn_log + math.log(factor))
    return np.array(out)


POINT_FNS = {"today": _today_point, "today_uncapped": partial(_today_point, capped=False)} | {n: partial(_sklearn_point, n) for n in ESTIMATORS}

# Models whose mistakes differ (one better on the held-out deals, another on the fresh ones), averaged in log price.
# TabPFN stays out so the ensemble can run while the app's servers are up.
ENSEMBLE = ("today", "elasticnet_v2", "boosting_v2")
POINT_FNS["ensemble"] = lambda train, test: np.mean([POINT_FNS[m](train, test) for m in ENSEMBLE], axis=0)


def _oof(rows: list[dict], point: str, folds: int = 10, seed: int = 0) -> np.ndarray:
    pred = np.empty(len(rows))
    for tr, te in KFold(folds, shuffle=True, random_state=seed).split(rows):
        pred[te] = POINT_FNS[point]([rows[i] for i in tr], [rows[i] for i in te])
    return pred


def _offsets(resid: np.ndarray) -> dict:
    """Signed split-conformal offsets per level: the ⌊(n+1)α/2⌋-th smallest residual and the ⌈(n+1)(1−α/2)⌉-th."""
    r, n = np.sort(resid), len(resid)
    out = {}
    for level in LEVELS:
        a = (1 - level) / 2
        out[level] = (float(r[max(math.floor((n + 1) * a), 1) - 1]), float(r[min(math.ceil((n + 1) * (1 - a)), n) - 1]))
    return out


def _band_offsets(rows: list[dict], resid: np.ndarray, by_band: bool) -> dict:
    out = {"all": _offsets(resid)}
    if by_band:
        bands = np.array([band(r["followers"]) for r in rows])
        out |= {b: _offsets(resid[bands == b]) if (bands == b).sum() >= MIN_BAND else out["all"] for b in BANDS}
    return out


def conformal_offsets(rows: list[dict], point: str, by_band: bool = False, folds: int = 10, seed: int = 0) -> dict:
    """Log offsets around the fair price for each range level, from out-of-fold errors on `rows`, overall or per follower band."""
    return _band_offsets(rows, np.log([r["price"] for r in rows]) - _oof(rows, point, folds, seed), by_band)


def _local_spread(train: list[dict], resid: np.ndarray, targets: list[dict], leave_out_self: bool = False) -> np.ndarray:
    """Typical size of the out-of-fold error among the K_LOCAL training deals nearest each target in views and
    followers: small where similar deals were priced alike, large where they weren't."""
    def pos(rows):
        return np.log([[r["views"], r["followers"]] for r in rows])

    A = pos(train)
    mu, sd = A.mean(axis=0), A.std(axis=0) + 1e-9
    d = np.linalg.norm(((pos(targets) - mu) / sd)[:, None, :] - ((A - mu) / sd)[None, :, :], axis=2)
    if leave_out_self:
        np.fill_diagonal(d, np.inf)
    nearest = np.argsort(d, axis=1)[:, :K_LOCAL]
    return np.maximum(np.abs(resid)[nearest].mean(axis=1), 0.05)


def _widen(rows: list[dict], m: dict) -> tuple[float, float]:
    """As in `pricing.price`: about 1.4x wider per doubling beyond WLDD's deals, toward the side being extrapolated."""
    above = max(m["followers"] / max(r["followers"] for r in rows), m["views"] / max(r["views"] for r in rows), 1.0)
    below = max(min(r["followers"] for r in rows) / m["followers"], 1.0)
    return math.sqrt(2) ** math.log2(below), math.sqrt(2) ** math.log2(above)


def _predict_both(point: str, train: list[dict], test: list[dict], folds: int = 10) -> dict[str, list[dict]]:
    """Fair price and 80% and 50% ranges for each test creator, with global and per-band offsets, fitted on `train` only."""
    logs = POINT_FNS[point](train, test)
    resid = np.log([r["price"] for r in train]) - _oof(train, point, folds)
    # Local: each training deal's error measured in units of its neighbourhood's typical error (itself left out),
    # so one set of conformal offsets serves every creator, scaled by the spread around them.
    local = _offsets(resid / _local_spread(train, resid, train, leave_out_self=True))
    spread = _local_spread(train, resid, test)
    out = {}
    for rng in RANGES:
        offs = _band_offsets(train, resid, rng == "band")
        preds = []
        for j, (r, lp) in enumerate(zip(test, logs)):
            below, above = _widen(train, r)
            fair = math.exp(lp)
            row = {"fair": round500(fair)}
            levels = {lv: (lo * spread[j], hi * spread[j]) for lv, (lo, hi) in local.items()} if rng == "local" else offs.get(band(r["followers"]), offs["all"])
            for level, (lo, hi) in levels.items():
                k = round(level * 100)
                row[f"low{k}"], row[f"high{k}"] = round500(fair * math.exp(lo) / below), round500(fair * math.exp(hi) * above)
            preds.append(row)
        out[rng] = preds
    return out


def predict(point: str, rng: str, train: list[dict], test: list[dict]) -> list[dict]:
    return _predict_both(point, train, test)[rng]


def _served(train: list[dict], test: list[dict]) -> list[dict]:
    """Exactly what the app shows: `pricing.price`, with MAPIE's 80% range."""
    model = _today(train)
    return [{"fair": p["fair"], "low80": p["low"], "high80": p["high"]} for p in (price(model, r) for r in test)]


def _all_preds(train: list[dict], test: list[dict], points, folds: int = 10) -> dict[str, list[dict]]:
    out = {}
    for p in points:
        both = _predict_both(p, train, test, folds)
        out |= {f"{p}/{rng}": both[rng] for rng in RANGES}
    if "today" in points:
        out[BEFORE] = _served(train, test)
    return out


def _summary(pairs: list[tuple[dict, dict]]) -> dict:
    s = {"n": len(pairs), "error": median(abs(p["fair"] - r["price"]) / r["price"] for r, p in pairs)}
    for k in (80, 50):
        if f"low{k}" in pairs[0][1]:
            s[f"coverage{k}"] = mean(p[f"low{k}"] <= r["price"] <= p[f"high{k}"] for r, p in pairs)
            s[f"width{k}"] = median(p[f"high{k}"] / p[f"low{k}"] if p[f"low{k}"] else math.inf for r, p in pairs)
    return s


def score(test: list[dict], preds: list[dict]) -> dict:
    """Median error, the share of prices inside each range and its median high/low width, overall and by follower band."""
    pairs = list(zip(test, preds))
    by_band = {b: _summary(ps) for b in BANDS if (ps := [(r, p) for r, p in pairs if band(r["followers"]) == b])}
    return _summary(pairs) | {"by_band": by_band}


WIDTHS = (1.5, 2, 3, 4, 6, 8)


def coverage_by_width(test: list[dict], preds: list[dict], widths=WIDTHS) -> dict:
    """Share of real prices inside a range of each width (high ÷ low) centred on the middle price: what a range of
    that width would have held."""
    off = [max(p["fair"] / r["price"], r["price"] / p["fair"]) for r, p in zip(test, preds)]
    return {w: float(np.mean([x <= math.sqrt(w) + 1e-12 for x in off])) for w in widths}


def _mean(scores: list[dict]) -> dict:
    return {k: _mean([s[k] for s in scores if k in s]) if isinstance(v, dict) else float(np.mean([s[k] for s in scores]))
            for k, v in scores[0].items()}


def repeated_cv(train: list[dict], points=POINTS, repeats: int = 5, folds: int = 10) -> dict:
    """Every candidate scored on deals it never saw: `repeats` shuffles of `folds` folds, averaged over shuffles."""
    per: dict[str, list] = {}
    for rep in range(repeats):
        preds: dict[str, list] = {}
        for tr, te in KFold(folds, shuffle=True, random_state=rep).split(train):
            out = _all_preds([train[i] for i in tr], [train[i] for i in te], points, folds)
            for name, ps in out.items():
                preds.setdefault(name, [None] * len(train))
                for i, p in zip(te, ps):
                    preds[name][i] = p
        for name, ps in preds.items():
            per.setdefault(name, []).append(score(train, ps))
    return {name: _mean(s) for name, s in per.items()}


def pick(cv: dict, points=POINTS) -> dict:
    """Price: the lowest CV error among models whose 80% range holds at least 75% of prices. Range: around that model,
    the narrowest that holds at least 77% (or, if none does, the one that holds the most)."""
    ok = [p for p in points if cv[f"{p}/global"]["coverage80"] >= 0.75] or list(points)
    best = min(ok, key=lambda p: cv[f"{p}/global"]["error"])
    options = [f"{best}/{rng}" for rng in RANGES] + ([BEFORE] if best == "today" else [])
    holding = [o for o in options if cv[o]["coverage80"] >= 0.77]
    rng = min(holding, key=lambda o: cv[o]["width80"]) if holding else max(options, key=lambda o: cv[o]["coverage80"])
    return {"price": best, "range": rng}


def beats(after: dict, before: dict) -> bool:
    """Better on one count and no worse on the other, with the 80% range still holding at least 75% of prices."""
    return after["coverage80"] >= 0.75 and ((after["error"] < before["error"] and after["width80"] <= before["width80"])
                                             or (after["width80"] < before["width80"] and after["error"] <= before["error"]))


def _bootstrap(test: list[dict], after: list[dict], before: list[dict], draws: int = 2000, seed: int = 0) -> dict:
    """90% intervals, over resampled test creators, of how much the median error drops and how the median width changes."""
    y = np.array([r["price"] for r in test], dtype=float)

    def arrays(ps):
        return np.abs(np.array([p["fair"] for p in ps]) - y) / y, np.array([p["high80"] / p["low80"] for p in ps])

    (ea, wa), (eb, wb) = arrays(after), arrays(before)
    idx = np.random.default_rng(seed).integers(0, len(y), (draws, len(y)))
    drop = np.median(eb[idx], axis=1) - np.median(ea[idx], axis=1)
    ratio = np.median(wa[idx], axis=1) / np.median(wb[idx], axis=1)
    return {"error_drop": [float(x) for x in np.percentile(drop, [5, 50, 95])], "width_ratio": [float(x) for x in np.percentile(ratio, [5, 50, 95])]}


def run(train: list[dict], holdout: list[dict], fresh: list[dict], repeats: int = 5, folds: int = 10, points=POINTS) -> dict:
    """The pick uses `train` only. Held-out deals are scored by models fitted on `train`, fresh ones by models fitted on all deals."""
    _FITS.clear()
    cv = repeated_cv(train, points, repeats, folds)
    picked = pick(cv, points)
    after = picked["range"]
    deals = sorted(train + holdout, key=lambda r: r["handle"])  # the served model's order (`training_rows`); MAPIE's folds follow it
    hold, new = _all_preds(train, holdout, points, folds), _all_preds(deals, fresh, points, folds)
    shown = (f"{picked['price']}/global" if after == BEFORE else after)  # where the 50% band comes from
    points_out = [{"set": s, "band": band(r["followers"]), "actual": r["price"], "before": preds[BEFORE][i], "after": preds[after][i] | {
                   k: v for k, v in preds[shown][i].items() if k.endswith("50")},
                   "beyond": r["followers"] > max(x["followers"] for x in base) or r["views"] > max(x["views"] for x in base)}
                  for s, rows, preds, base in (("holdout", holdout, hold, train), ("fresh", fresh, new, deals)) for i, r in enumerate(rows)]
    _FITS.clear()
    result = {
        "n": {"train": len(train), "holdout": len(holdout), "fresh": len(fresh)},
        "cv": cv,
        "picked": picked,
        "holdout": {name: score(holdout, ps) for name, ps in hold.items()},
        "fresh": {name: score(fresh, ps) for name, ps in new.items()},
        "bootstrap": _bootstrap(holdout + fresh, hold[after] + new[after], hold[BEFORE] + new[BEFORE]),
        "points": points_out,
    }
    result["coverage_by_width"] = {s: coverage_by_width(rows, preds[BEFORE]) for s, rows, preds in (("holdout", holdout, hold), ("fresh", fresh, new))}
    result["adopt"] = after != BEFORE and all(beats(result[s][after], result[s][BEFORE]) for s in ("holdout", "fresh"))
    return result


def learning_curve(point: str, train: list[dict], test: list[dict], sizes, draws: int = 20, seed: int = 0) -> list[dict]:
    """Median error on `test` when the model learns from n of the training deals, averaged over random draws of n."""
    rng, out = np.random.default_rng(seed), []
    for n in sizes:
        errs = []
        for _ in range(draws if n < len(train) else 1):
            sub = [train[i] for i in sorted(rng.choice(len(train), n, replace=False))]
            errs.append(score(test, [{"fair": round500(math.exp(x))} for x in POINT_FNS[point](sub, test)])["error"])
        out.append({"n": n, "error": float(np.mean(errs)), "low": float(min(errs)), "high": float(max(errs))})
    _FITS.clear()
    return out


def importance(point: str, rows: list[dict]) -> dict[str, float]:
    """Mean absolute SHAP value per feature in log price (exact for a linear model: coefficient times the centred,
    scaled feature). Boosting gets permutation importance instead. Largest first."""
    y = np.log([r["price"] for r in rows])
    if point in ("today", "today_uncapped"):
        model = fit(rows)
        names, Xs, coef = FEATURE_NAMES[: 4 + len(CATEGORIES)], model.core.scaler.transform([features(r) for r in rows]), model.core.ridge.coef_ * model.w
        values = np.abs(coef * (Xs - Xs.mean(axis=0))).mean(axis=0)
    elif point in PERMUTATION:
        X = np.array([features_v2(r) for r in rows])
        est = ESTIMATORS[point]().fit(X, y)
        names, values = FEATURE_NAMES, np.maximum(permutation_importance(est, X, y, n_repeats=20, random_state=0).importances_mean, 0)
    else:
        X = np.array([features_v2(r) for r in rows])
        est = ESTIMATORS[point]().fit(X, y)
        Xs = est[:-1].transform(X)
        names, values = FEATURE_NAMES, np.abs(est[-1].coef_ * (Xs - Xs.mean(axis=0))).mean(axis=0)
    return dict(sorted(((n, float(v)) for n, v in zip(names, values)), key=lambda kv: -kv[1]))



def report_table(result: dict) -> str:
    """The before/after table: every candidate's CV, held-out and fresh numbers, today's served model first."""
    def pct(x):
        return "–" if x is None else f"{x:.0%}"

    def width(x):
        return "–" if x is None else f"{x:.1f}×"

    def cells(s):
        return [pct(s["error"]), pct(s.get("coverage80")), width(s.get("width80")), pct(s.get("coverage50")), width(s.get("width50"))]

    p, n, b = result["picked"], result["n"], result["bootstrap"]
    head = ["Candidate"] + [f"{s} {c}" for s in ("CV", "Held-out", "Fresh") for c in ("error", "in 80%", "80% width", "in 50%", "50% width")]
    lines = [f"Deals: {n['train']} training, {n['holdout']} held out, {n['fresh']} fresh. Error is the median gap between the middle of the "
             "range and the price paid; width is the median high ÷ low.",
             f"Picked on CV of the training deals only: price `{p['price']}`, range `{p['range']}`. Adopted: {'yes' if result['adopt'] else 'no'}.",
             f"Held out and fresh together, challenger against today (90% bootstrap): error drops {pct(b['error_drop'][0])} to "
             f"{pct(b['error_drop'][2])} (middle {pct(b['error_drop'][1])}); 80% width × {b['width_ratio'][0]:.2f} to {b['width_ratio'][2]:.2f}.",
             "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for name in [BEFORE] + [x for x in result["cv"] if x != BEFORE]:
        mark = " ←" if name == p["range"] else ""
        lines.append(f"| {name}{mark} | " + " | ".join(cells(result["cv"][name]) + cells(result["holdout"][name]) + cells(result["fresh"][name])) + " |")
    if "coverage_by_width" in result:
        lines += ["", "How wide a range must be: the share of real prices inside a range of each width around today's middle price.", "",
                  "| Width (high ÷ low) | " + " | ".join(f"{w:g}×" for w in WIDTHS) + " |", "|" + "---|" * (len(WIDTHS) + 1)]
        for s, label in (("holdout", "Held out"), ("fresh", "Fresh")):
            lines.append(f"| {label} | " + " | ".join(pct(result["coverage_by_width"][s][w]) for w in WIDTHS) + " |")
    return "\n".join(lines) + "\n"
