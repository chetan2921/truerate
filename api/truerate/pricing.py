import math
from dataclasses import dataclass
from statistics import median

import numpy as np
from mapie.regression import CrossConformalRegressor
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from truerate.signals import CATEGORIES, band

K = 6  # past deals compared against
CONFIDENCE = 0.8  # the price range is an 80% conformal interval (MAPIE)
RANGE_METHOD = f"MAPIE cross-conformal (CV+), {CONFIDENCE:.0%} confidence"
SHRINK = 3  # the population's paid-reel drop counts as this many ads of the creator's own


def _group(n: float) -> str:
    """Indian digit grouping: 1,50,000 and 1,23,45,678."""
    digits = str(int(round(n)))
    head, tail = digits[:-3], digits[-3:]
    while len(head) > 2:
        head, tail = head[:-2], head[-2:] + "," + tail
    return f"{head},{tail}" if head else tail


def inr(n: float) -> str:
    return "₹" + _group(n)


def round500(x: float) -> int:
    return int(math.floor(x / 500 + 0.5) * 500)


def features(m: dict) -> list[float]:
    return [math.log(m["views"]), math.log(m["followers"]), m["engagement"], m["comments_per_1k"]] + [float(m["category"] == c) for c in CATEGORIES]


FEATURE_NAMES = (["log views", "log followers", "engagement", "comments per 1,000 views"] + list(CATEGORIES)
                 + ["account age", "log reel seconds", "log reels per month", "ads share", "YouTube link", "contact email", "verified",
                    "English comments", "views spread", "log trend", "likes per view"])


def _num(x) -> float:
    return math.nan if x is None else float(x)


def _log(x) -> float:
    return math.log(x) if x else math.nan


def features_v2(m: dict) -> list[float]:
    """`features` plus what it leaves out: account age, reel length, posting rate, share of ads, a YouTube link, a contact
    email, the tick, English comments, how much views vary, the trend and likes per view. Missing ones stay NaN."""
    n = m.get("n_reels")
    return features(m) + [_num(m.get("age_years")), _log(m.get("reel_seconds")), _log(m.get("reels_per_month")),
                          m["paid_n"] / n if n else math.nan, _num(m.get("youtube")), _num(m.get("email")), _num(m.get("verified")),
                          _num(m.get("english")), _num(m.get("views_cv")), _log(m.get("trend")), _num(m.get("likes_per_view"))]


# On deals the model never saw, a range this wide around the middle held about half of real prices (57% of the 30 held
# out, 42% of the 19 fresh; `truerate experiment`, 2026-10-11). Anything narrower would usually miss: 2x held 30% and 16%.
LIKELY_WIDTH = 3


def likely_band(fair: float, low: float, high: float) -> tuple[int, int]:
    """The "likely" band shown beside the 80% range: LIKELY_WIDTH wide around the middle, never outside the full range."""
    half = math.sqrt(LIKELY_WIDTH)
    return max(round500(fair / half), round500(low)), min(round500(fair * half), round500(high))


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


LOCAL_K = 15  # a creator's range scales with the typical error among this many nearest WLDD deals


def boosting_regressor():
    """Small and slow-learning, and never cheaper for more views or followers (the experiment's `boosting_v2`)."""
    from sklearn.ensemble import HistGradientBoostingRegressor

    return HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_depth=2, min_samples_leaf=10, l2_regularization=1.0,
                                         monotonic_cst=[1, 1] + [0] * (len(FEATURE_NAMES) - 2), random_state=0)


def paid_typical_of(rows: list[dict]) -> float:
    ratios = [r["paid_ratio"] for r in rows if r["paid_n"]]
    return median(ratios) if ratios else 1.0


def boosted_logs(train: list[dict], test: list[dict]) -> np.ndarray:
    """Log price from boosting fitted on `train`, with the same sponsored-performance factor the Ridge path applies."""
    est = boosting_regressor().fit(np.array([features_v2(r) for r in train]), np.log([r["price"] for r in train]))
    typical = paid_typical_of(train)
    return est.predict(np.array([features_v2(r) for r in test])) + np.log([collab_factor(r["paid_n"], r["paid_ratio"], typical)[1] for r in test])


def split_offsets(resid: np.ndarray, level: float) -> tuple[float, float]:
    """Signed split-conformal offsets: the ⌊(n+1)α/2⌋-th smallest residual and the ⌈(n+1)(1−α/2)⌉-th."""
    r, n, a = np.sort(resid), len(resid), (1 - level) / 2
    return float(r[max(math.floor((n + 1) * a), 1) - 1]), float(r[min(math.ceil((n + 1) * (1 - a)), n) - 1])


def _positions(rows: list[dict]) -> np.ndarray:
    return np.log([[r["views"], r["followers"]] for r in rows])


def local_spread(train_pos: np.ndarray, abs_resid: np.ndarray, target_pos: np.ndarray, leave_out_self: bool = False) -> np.ndarray:
    """Typical size of the out-of-fold error among the LOCAL_K training deals nearest each target in views and followers:
    small where similar deals were priced alike, large where they weren't."""
    mu, sd = train_pos.mean(axis=0), train_pos.std(axis=0) + 1e-9
    d = np.linalg.norm(((target_pos - mu) / sd)[:, None, :] - ((train_pos - mu) / sd)[None, :, :], axis=2)
    if leave_out_self:
        np.fill_diagonal(d, np.inf)
    nearest = np.argsort(d, axis=1)[:, :LOCAL_K]
    return np.maximum(abs_resid[nearest].mean(axis=1), 0.05)


@dataclass
class Boosted:
    """Gradient boosting on `features_v2` for the price, and a "local" 80% range: conformal offsets on out-of-fold errors,
    each scaled by how alike WLDD priced the creator's nearest deals."""

    est: object
    lo: float
    hi: float
    pos: np.ndarray  # the training deals' log views and followers
    abs_resid: np.ndarray  # their absolute out-of-fold log errors

    @classmethod
    def fit(cls, rows: list[dict], ranges: bool = True) -> "Boosted":
        est = boosting_regressor().fit(np.array([features_v2(r) for r in rows]), np.log([r["price"] for r in rows]))
        pos = _positions(rows)
        if not ranges:  # point prices only (leave-one-out checks): skip the 10 out-of-fold refits
            return cls(est, 0.0, 0.0, pos, np.zeros(len(rows)))
        oof = np.empty(len(rows))
        for tr, te in KFold(10, shuffle=True, random_state=0).split(rows):
            oof[te] = boosted_logs([rows[i] for i in tr], [rows[i] for i in te])
        resid = np.log([r["price"] for r in rows]) - oof
        lo, hi = split_offsets(resid / local_spread(pos, np.abs(resid), pos, leave_out_self=True), CONFIDENCE)
        return cls(est, lo, hi, pos, np.abs(resid))

    def log_price(self, m: dict) -> float:
        return float(self.est.predict(np.array([features_v2(m)]))[0])

    def spread(self, m: dict) -> float:
        return float(local_spread(self.pos, self.abs_resid, _positions([m]))[0])


@dataclass
class PriceModel:
    core: Core
    w: float  # Ridge's share of the blend, in log space
    lo: float  # 10th and 90th percentile of leave-one-out log residuals
    hi: float
    paid_typical: float  # median share of views a paid reel keeps, across WLDD's creators
    conformal: CrossConformalRegressor | None = None  # gives each creator's 80% price interval
    boosted: Boosted | None = None  # when set, the price and range come from gradient boosting instead of Ridge

    @property
    def rows(self) -> list[dict]:
        return self.core.rows


def fit(rows: list[dict], blend: tuple[float, float, float] | None = None, method: str = "ridge", ranges: bool = True) -> PriceModel:
    """Fit on these deals. Without `blend`, the weight and range come from leave-one-out over the same deals. With
    `method="boosting"` the price and range come from `Boosted`; Ridge's core still gives the comparables and the rate card."""
    if method == "boosting":
        return PriceModel(Core.fit(rows), 1.0, 0.0, 0.0, paid_typical=paid_typical_of(rows), boosted=Boosted.fit(rows, ranges))
    if blend is None:
        loo = np.array([Core.fit(rows[:i] + rows[i + 1 :]).predict_logs(r)[:2] for i, r in enumerate(rows)])
        y = np.log([r["price"] for r in rows])
        w = float(min(np.linspace(0, 1, 11), key=lambda w: np.median(np.abs(y - (w * loo[:, 0] + (1 - w) * loo[:, 1])))))
        lo, hi = np.percentile(y - (w * loo[:, 0] + (1 - w) * loo[:, 1]), [10, 90])
        blend = (w, float(lo), float(hi))
    ratios = [r["paid_ratio"] for r in rows if r["paid_n"]]
    # CV+ (cross-conformal): 10 refits of the same Ridge, each creator's interval built from out-of-fold errors.
    conformal = CrossConformalRegressor(
        make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 3, 20))), confidence_level=CONFIDENCE, method="plus", cv=10, random_state=42
    ).fit_conformalize(np.array([features(r) for r in rows]), np.log([r["price"] for r in rows]))
    return PriceModel(Core.fit(rows), *blend, paid_typical=median(ratios) if ratios else 1.0, conformal=conformal)


FACTOR_FLOOR, FACTOR_CAP = 0.5, 1.0

# Published asking prices for one Instagram reel in India, by follower tier. Context only: WLDD's own deals sit at or
# below these (median ₹16,000 at 10K to 1L followers, ₹25,000 at 1L to 5L, against ₹50,000+ asked at that size).
MARKET_SOURCE = "TickTime Journal, Influencer Rate Card India 2026 (May 2026)"
MARKET_RATES = [  # (followers below, tier, low, high)
    (10_000, "Nano (under 10K followers)", 2_000, 10_000),
    (1_00_000, "Micro (10K to 1L followers)", 8_000, 75_000),
    (5_00_000, "Mid-tier (1L to 5L followers)", 50_000, 3_50_000),
    (10_00_000, "Macro (5L to 10L followers)", 2_00_000, 8_50_000),
    (float("inf"), "Mega (10L+ followers)", 6_00_000, 25_00_000),
]


MIN_DISCOUNT_DEALS = 10  # deals a tier needs before WLDD's discount on the market is read from it
BEYOND_FULL = 3  # this many times WLDD's largest creator or more, and the price is the market estimate


def market_discount(rows: list[dict]) -> float:
    """WLDD's median price over the published market's middle, in the largest follower tier where WLDD has at least
    MIN_DISCOUNT_DEALS deals. On WLDD's deals that is 1L to 5L followers: WLDD pays about 0.19 of the market's middle."""
    found, prev = 1.0, 0
    for below, _tier, low, high in MARKET_RATES:
        prices = [r["price"] for r in rows if prev <= r["followers"] < below]
        if len(prices) >= MIN_DISCOUNT_DEALS:
            found = median(prices) / math.sqrt(low * high)
        prev = below
    return found


def market_reference(followers: int) -> dict:
    below, tier, low, high = next(t for t in MARKET_RATES if followers < t[0])
    return {"tier": tier, "low": low, "high": high, "source": MARKET_SOURCE}


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
    market = math.exp(model.boosted.log_price(m) if model.boosted else model.w * ridge_log + (1 - model.w) * knn_log)
    top_followers, top_views = max(r["followers"] for r in model.rows), max(r["views"] for r in model.rows)
    least_followers = min(r["followers"] for r in model.rows)
    above = max(m["followers"] / top_followers, m["views"] / top_views, 1.0)
    ref = market_reference(m["followers"])
    # Past WLDD's largest deal its own data can't say what a creator will accept (user decision, 2026-10-11): the price
    # moves toward the published rate for the creator's size, times how far below that rate WLDD really pays, fully so
    # from BEYOND_FULL times WLDD's largest creator.
    toward_market = min(math.log(above) / math.log(BEYOND_FULL), 1.0)
    discount = market_discount(model.rows)
    anchor = discount * math.sqrt(ref["low"] * ref["high"])
    anchored = math.exp((1 - toward_market) * math.log(market) + toward_market * math.log(anchor))
    shrunk, factor = collab_factor(m["paid_n"], m["paid_ratio"], model.paid_typical)
    fair = anchored * factor * genuine_share
    steps = [round500(market), round500(anchored), round500(anchored * factor), round500(fair)]
    in_category = [per_1k(r) for r in model.rows if r["category"] == m["category"]]
    # Outside WLDD's deals the range widens about 1.4x per doubling beyond them, toward the side being extrapolated:
    # up for a bigger creator (who will likely ask more), down for a smaller one. The published asking price for the
    # creator's size is returned beside the range, never merged into it (user decision, 2026-10-10).
    below = max(least_followers / m["followers"], 1.0)
    if model.boosted is not None:
        s = model.boosted.spread(m)
        lo_off, hi_off = model.boosted.lo * s, model.boosted.hi * s
    elif model.conformal is not None:
        pred, pis = model.conformal.predict_interval(np.array([features(m)]))
        lo_off, hi_off = pis[0, 0, 0] - pred[0], pis[0, 1, 0] - pred[0]
    else:  # a model pickled before MAPIE
        lo_off, hi_off = model.lo, model.hi
    low = fair * math.exp(lo_off) / math.sqrt(2) ** math.log2(below)
    high = fair * math.exp(hi_off) * math.sqrt(2) ** math.log2(above)
    note = None
    if m["followers"] > top_followers or m["views"] > top_views:
        note = (f"Bigger than any creator WLDD has booked (largest: {_group(top_followers)} followers, {_group(top_views)} typical views). "
                f"WLDD's deals can't say what a creator this size accepts, so the price leans on the published rate for "
                f"{ref['tier'].split(' (')[0].lower()} creators, discounted the way WLDD pays (about {discount:.2f} of the market's "
                "middle in its biggest tier with enough deals). The published asking price is shown separately.")
    elif m["followers"] < least_followers:
        note = f"Smaller than any creator WLDD has booked (smallest: {_group(least_followers)} followers), so the range is wider."
    likely_low, likely_high = likely_band(steps[3], low, high)
    return {
        "market": steps[0],
        "fair": steps[3],
        "low": round500(low),
        "high": round500(high),
        "likely_low": likely_low,
        "likely_high": likely_high,
        "collab_factor": factor,
        "genuine_share": genuine_share,
        "ridge_share": model.w,
        "note": note,
        "market_reference": ref,
        "waterfall": [
            {"step": "Market price from WLDD's past deals", "amount": steps[0]},
            *([{"step": "Bigger than WLDD's deals: toward the market rate, discounted the way WLDD pays", "amount": steps[1] - steps[0]}]
              if toward_market > 0 else []),
            {"step": "Sponsored-performance adjustment", "amount": steps[2] - steps[1]},
            {"step": "Fake-engagement adjustment", "amount": steps[3] - steps[2]},
            {"step": "Middle of the fair range", "amount": steps[3]},
        ],
        "comparables": [
            {"handle": r["handle"], "price": r["price"], "views": r["views"], "followers": r["followers"], "category": r["category"], "per_1k_views": round(per_1k(r))}
            for r in near
        ],
        "delivery": {
            "views": [round(m["views_p25"] * shrunk), round(m["views"] * shrunk), round(m["views_p75"] * shrunk)],
            "likes": round(m["views"] * shrunk * (m["likes_per_view"] or 0)),
            "comments": round(m["views"] * shrunk * m["comments_per_1k"] / 1000),
            "cost_per_1k": round(steps[3] / (m["views"] / 1000)),
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
    """Median error by band, plus the scores judges know: the share of prices within 2x, R² on log price, and the rank
    correlation between predicted and paid (is the order of creators right)."""
    by_band = {b: [e[method] for e in errors if e["band"] == b] for b in ("small", "medium", "big")}
    actual = np.log([e["actual"] for e in errors])
    predicted = np.log([max(e[f"{method}_price"], 1) for e in errors])
    residual, spread = np.sum((actual - predicted) ** 2), np.sum((actual - actual.mean()) ** 2)
    return {"median_error": median(e[method] for e in errors), "by_band": {b: median(v) if v else None for b, v in by_band.items()},
            "within_2x": float(np.mean(np.abs(actual - predicted) <= math.log(2))), "r2_log": float(1 - residual / spread) if spread else None,
            "spearman": float(spearmanr(actual, predicted).statistic)}


BOOSTED_RANGE_METHOD = f"Gradient boosting, conformal {CONFIDENCE:.0%} ranges scaled by the nearest {LOCAL_K} deals' errors"


def validate(rows: list[dict], method: str = "ridge") -> dict:
    """Holdout error by follower band and leave-one-out error by category, against both baselines. Holds no handles or prices."""
    train = [r for r in rows if not r["holdout"]]
    model = fit(train, method=method)

    def errors(r: dict, m: PriceModel, others: list[dict]) -> dict:
        p = price(m, r)
        prices = {"model": p["fair"], "band_median": band_median_price(others, r["followers"]), "modash": modash_price(others, r)}
        return {
            "band": band(r["followers"]),
            "actual": r["price"],
            "predicted": p["fair"],
            **{method: abs(v - r["price"]) / r["price"] for method, v in prices.items()},
            **{f"{method}_price": v for method, v in prices.items()},
            "covered": p["low"] <= r["price"] <= p["high"],
        }

    held = [errors(r, model, train) for r in rows if r["holdout"]]
    # Point prices only: the ranges' out-of-fold refits would cost ten more fits per deal and aren't scored here.
    loo = [(r["category"], errors(r, fit(rows[:i] + rows[i + 1 :], (model.w, model.lo, model.hi), method=method, ranges=False), rows[:i] + rows[i + 1 :]))
           for i, r in enumerate(rows)]
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
        "method": method,
        "blend_weight": model.w,
        "range_method": BOOSTED_RANGE_METHOD if method == "boosting" else RANGE_METHOD,
        "range": [math.exp(model.lo), math.exp(model.hi)],
    }


MIN_RATE_DEALS = 3


def rate_card(model: PriceModel) -> list[dict]:
    """₹ per 1,000 views by category from the deals behind the served model, priciest views first."""
    card = []
    for c in CATEGORIES:
        rows = [r for r in model.rows if r["category"] == c]
        if len(rows) < MIN_RATE_DEALS:  # one or two deals are not a rate
            continue
        p25, mid, p75 = (round(float(q)) for q in np.percentile([per_1k(r) for r in rows], [25, 50, 75]))
        card.append({"category": c, "n": len(rows), "per_1k": {"p25": p25, "median": mid, "p75": p75},
                     "typical_price": round(median(r["price"] for r in rows)), "typical_views": round(median(r["views"] for r in rows))})
    return sorted(card, key=lambda x: -x["per_1k"]["median"])


def thin_categories(model: PriceModel) -> list[dict]:
    """The categories with too few deals for a rate, and how many they have, so the rate card can still list them."""
    counts = {c: sum(r["category"] == c for r in model.rows) for c in CATEGORIES}
    return [{"category": c, "n": n} for c, n in counts.items() if n < MIN_RATE_DEALS]
