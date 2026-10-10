import math
from dataclasses import dataclass
from statistics import median

import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler

from truerate.signals import CATEGORIES, band

K = 6  # past deals compared against
SHRINK = 3  # the population's paid-reel drop counts as this many ads of the creator's own


def round500(x: float) -> int:
    return int(math.floor(x / 500 + 0.5) * 500)


def features(m: dict) -> list[float]:
    return [math.log(m["views"]), math.log(m["followers"]), m["engagement"], m["comments_per_1k"]] + [float(m["category"] == c) for c in CATEGORIES]


def per_1k(row: dict) -> float:
    return row["price"] / (row["views"] / 1000)


@dataclass
class Core:
    """Ridge on log price plus the 6 most similar past deals, fitted on one set of deals."""

    scaler: StandardScaler
    ridge: RidgeCV
    size: np.ndarray  # each deal's scaled log views and log followers
    rows: list[dict]

    @classmethod
    def fit(cls, rows: list[dict]) -> "Core":
        X = np.array([features(r) for r in rows])
        scaler = StandardScaler().fit(X)
        Xs = scaler.transform(X)
        ridge = RidgeCV(alphas=np.logspace(-2, 3, 20)).fit(Xs, np.log([r["price"] for r in rows]))
        return cls(scaler, ridge, Xs[:, :2], rows)

    def predict_logs(self, m: dict) -> tuple[float, float, list[dict]]:
        """(Ridge log price, KNN log price, the 6 nearest deals). Nearest means same category first, then closest views and followers.
        KNN is their median ₹ per 1,000 views times this creator's views."""
        x = self.scaler.transform([features(m)])
        dist = np.linalg.norm(self.size - x[0, :2], axis=1)
        order = sorted(range(len(self.rows)), key=lambda i: (self.rows[i]["category"] != m["category"], dist[i]))
        near = [self.rows[i] for i in order[:K]]
        return float(self.ridge.predict(x)[0]), math.log(median(map(per_1k, near)) * m["views"] / 1000), near


@dataclass
class PriceModel:
    core: Core
    w: float  # Ridge's share of the blend, in log space
    lo: float  # 10th and 90th percentile of leave-one-out log residuals
    hi: float
    paid_typical: float  # median share of views a paid reel keeps, across WLDD's creators

    @property
    def rows(self) -> list[dict]:
        return self.core.rows


def fit(rows: list[dict], blend: tuple[float, float, float] | None = None) -> PriceModel:
    """Fit on these deals. Without `blend`, the weight and range come from leave-one-out over the same deals."""
    if blend is None:
        loo = np.array([Core.fit(rows[:i] + rows[i + 1 :]).predict_logs(r)[:2] for i, r in enumerate(rows)])
        y = np.log([r["price"] for r in rows])
        w = float(min(np.linspace(0, 1, 11), key=lambda w: np.median(np.abs(y - (w * loo[:, 0] + (1 - w) * loo[:, 1])))))
        lo, hi = np.percentile(y - (w * loo[:, 0] + (1 - w) * loo[:, 1]), [10, 90])
        blend = (w, float(lo), float(hi))
    ratios = [r["paid_ratio"] for r in rows if r["paid_n"]]
    return PriceModel(Core.fit(rows), *blend, paid_typical=median(ratios) if ratios else 1.0)


FACTOR_FLOOR, FACTOR_CAP = 0.5, 1.0


def collab_factor(n: int, ratio: float | None, typical: float, prior: float | None = None) -> tuple[float, float]:
    """(Expected paid-reel share of own-reel views, price factor). Past prices already include the typical drop, so
    the factor divides it out. Bounded to 0.5-1.0: on WLDD's deals an upward factor (viral reels labelled as ads)
    took the holdout error from 57% to 83%, while discounting weak sponsored reach helped (leave-one-out 43% -> 39%)."""
    prior = typical if prior is None else prior
    shrunk = (n * ratio + SHRINK * prior) / (n + SHRINK) if n else prior
    factor = min(max(shrunk / typical, FACTOR_FLOOR), FACTOR_CAP)
    return round(typical * factor, 4), round(factor, 4)


def price(model: PriceModel, m: dict, genuine_share: float = 1.0) -> dict:
    ridge_log, knn_log, near = model.core.predict_logs(m)
    market = math.exp(model.w * ridge_log + (1 - model.w) * knn_log)
    shrunk, factor = collab_factor(m["paid_n"], m["paid_ratio"], model.paid_typical)
    fair = market * factor * genuine_share
    steps = [round500(market), round500(market * factor), round500(fair)]
    in_category = [per_1k(r) for r in model.rows if r["category"] == m["category"]]
    return {
        "market": steps[0],
        "fair": steps[2],
        "low": round500(fair * math.exp(model.lo)),
        "high": round500(fair * math.exp(model.hi)),
        "collab_factor": factor,
        "genuine_share": genuine_share,
        "ridge_share": model.w,
        "waterfall": [
            {"step": "Market price from WLDD's past deals", "amount": steps[0]},
            {"step": "Sponsored-performance adjustment", "amount": steps[1] - steps[0]},
            {"step": "Fake-engagement adjustment", "amount": steps[2] - steps[1]},
            {"step": "Recommended price", "amount": steps[2]},
        ],
        "comparables": [
            {"handle": r["handle"], "price": r["price"], "views": r["views"], "followers": r["followers"], "category": r["category"], "per_1k_views": round(per_1k(r))}
            for r in near
        ],
        "delivery": {
            "views": [round(m["views_p25"] * shrunk), round(m["views"] * shrunk), round(m["views_p75"] * shrunk)],
            "likes": round(m["views"] * shrunk * m["likes_per_view"]),
            "comments": round(m["views"] * shrunk * m["comments_per_1k"] / 1000),
            "cost_per_1k": round(steps[2] / (m["views"] / 1000)),
            "category_cost_per_1k": round(median(in_category)) if in_category else None,
        },
    }


def band_median_price(rows: list[dict], followers: int) -> float:
    same = [r for r in rows if band(r["followers"]) == band(followers)] or rows
    return median(r["price"] for r in same)


def modash_price(rows: list[dict], m: dict) -> float:
    """Views / 1,000 × WLDD's median ₹ per 1,000 views, ±25% for engagement against the band, ×2 at 1M+ followers."""
    same = [r for r in rows if band(r["followers"]) == band(m["followers"])] or rows
    band_engagement = median(r["engagement"] for r in same)
    modifier = 1.25 if m["engagement"] > band_engagement else 0.75 if m["engagement"] < band_engagement else 1.0
    return m["views"] / 1000 * median(map(per_1k, rows)) * modifier * (2 if m["followers"] >= 1_000_000 else 1)


def _summary(errors: list[dict], method: str) -> dict:
    by_band = {b: [e[method] for e in errors if e["band"] == b] for b in ("small", "medium", "big")}
    return {"median_error": median(e[method] for e in errors), "by_band": {b: median(v) if v else None for b, v in by_band.items()}}


def validate(rows: list[dict]) -> dict:
    """Holdout error by follower band and leave-one-out error by category, against both baselines. Holds no handles or prices."""
    train = [r for r in rows if not r["holdout"]]
    model = fit(train)

    def errors(r: dict, m: PriceModel, others: list[dict]) -> dict:
        p = price(m, r)
        return {
            "band": band(r["followers"]),
            "actual": r["price"],
            "predicted": p["fair"],
            "model": abs(p["fair"] - r["price"]) / r["price"],
            "band_median": abs(band_median_price(others, r["followers"]) - r["price"]) / r["price"],
            "modash": abs(modash_price(others, r) - r["price"]) / r["price"],
            "covered": p["low"] <= r["price"] <= p["high"],
        }

    held = [errors(r, model, train) for r in rows if r["holdout"]]
    loo = [(r["category"], errors(r, fit(rows[:i] + rows[i + 1 :], (model.w, model.lo, model.hi)), rows[:i] + rows[i + 1 :])) for i, r in enumerate(rows)]
    return {
        "holdout": {
            "n": len(held),
            "coverage": sum(e["covered"] for e in held) / len(held),
            "points": [{"actual": round(e["actual"]), "predicted": e["predicted"], "band": e["band"]} for e in held],
            **{method: _summary(held, method) for method in ("model", "band_median", "modash")},
        },
        "by_category": {
            c: {"n": len(es), **{method: median(e[method] for e in es) for method in ("model", "band_median", "modash")}}
            for c in CATEGORIES
            if (es := [e for cat, e in loo if cat == c])
        },
        "n_deals": len(rows),
        "blend_weight": model.w,
        "range": [math.exp(model.lo), math.exp(model.hi)],
    }


def rate_card(model: PriceModel) -> list[dict]:
    """₹ per 1,000 views by category from the deals behind the served model, priciest views first."""
    card = []
    for c in CATEGORIES:
        rows = [r for r in model.rows if r["category"] == c]
        if not rows:
            continue
        p25, mid, p75 = (round(float(q)) for q in np.percentile([per_1k(r) for r in rows], [25, 50, 75]))
        card.append({"category": c, "n": len(rows), "per_1k": {"p25": p25, "median": mid, "p75": p75},
                     "typical_price": round(median(r["price"] for r in rows)), "typical_views": round(median(r["views"] for r in rows))})
    return sorted(card, key=lambda x: -x["per_1k"]["median"])
