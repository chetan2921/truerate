"""Graphs for the model v2 experiments, in DESIGN.md's dark theme for the deck. The two series colours are the brand's
blue and green stepped down for marks, checked with the dataviz validator on #131313 (all checks pass). They hold WLDD
prices, so they are written only to the git-ignored data/models/experiments/."""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator  # noqa: E402

BG, TEXT, MUTED, LINE = "#131313", "#FBFBFB", "#A6A6A6", "#3A3A3A"
BEFORE_C, AFTER_C = "#3987e5", "#4fa61f"
MARKERS = {"holdout": "o", "fresh": "s"}
SET_NAMES = {"holdout": "held out", "fresh": "fresh"}

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "text.color": TEXT, "axes.labelcolor": MUTED,
    "axes.edgecolor": LINE, "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": LINE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.family": ["Arial", "DejaVu Sans"], "font.size": 11,
    "legend.frameon": False, "legend.labelcolor": TEXT,
})


def _inr(x: float, _=None) -> str:
    """₹5K, ₹50K, ₹1L, ₹10L."""
    return f"₹{x / 1e5:g}L" if x >= 1e5 else f"₹{x / 1e3:g}K"


def _log_axis(axis) -> None:
    axis.set_major_locator(LogLocator(subs=(1, 2, 5)))
    axis.set_major_formatter(FuncFormatter(_inr))
    axis.set_minor_formatter(FuncFormatter(lambda *_: ""))


def predicted_vs_actual(result: dict, names: tuple[str, str], path: Path) -> None:
    pts = result["points"]
    vals = [p["actual"] for p in pts] + [p[k]["fair"] for p in pts for k in ("before", "after")]
    lo, hi = min(vals) / 1.5, max(vals) * 1.5
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.4), sharex=True, sharey=True)
    for ax, key, color, name in zip(axes, ("before", "after"), (BEFORE_C, AFTER_C), names):
        ax.set(xscale="log", yscale="log", xlim=(lo, hi), ylim=(lo, hi), aspect="equal")
        ax.plot([lo, hi], [lo, hi], color=MUTED, lw=1.2, ls="--")
        for f in (2, 0.5):
            ax.plot([lo, hi], [lo * f, hi * f], color=LINE, lw=1, ls=":")
        for s, marker in ((s, m) for s, m in MARKERS.items() if result["n"][s]):
            sel = [p for p in pts if p["set"] == s]
            ax.scatter([p["actual"] for p in sel], [p[key]["fair"] for p in sel], s=42, marker=marker, color=color, edgecolor=BG, linewidth=1.2, label=f"{SET_NAMES[s]} ({result['n'][s]})")
        errs = {s: result[s][result["picked"]["range"] if key == "after" else "today_served"]["error"] for s in MARKERS if result["n"][s]}
        ax.set_title(f"{name}\nmedian error: " + ", ".join(f"{SET_NAMES[s]} {e:.0%}" for s, e in errs.items()), color=TEXT, loc="left", fontsize=12)
        ax.set_xlabel("What WLDD paid")
        _log_axis(ax.xaxis)
        _log_axis(ax.yaxis)
        ax.legend(loc="upper left", fontsize=10)
    axes[0].set_ylabel("Middle of TruRate's range")
    fig.text(0.01, 0.01, "Dashed: prediction equals the price paid. Dotted: twice or half the price. No point was seen in training.", color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def ranges(result: dict, names: tuple[str, str], path: Path) -> None:
    pts = sorted(result["points"], key=lambda p: (p["set"] != "holdout", p["actual"]))
    fig, ax = plt.subplots(figsize=(13, 5.4))
    for i, p in enumerate(pts):
        for key, color, dx in (("before", BEFORE_C, -0.17), ("after", AFTER_C, 0.17)):
            ax.plot([i + dx, i + dx], [p[key]["low80"], p[key]["high80"]], color=color, lw=3, solid_capstyle="round")
        ax.scatter([i], [p["actual"]], s=22, color=TEXT, zorder=3, edgecolor=BG, linewidth=0.8)
    split = sum(p["set"] == "holdout" for p in pts) - 0.5
    ax.axvline(split, color=MUTED, lw=1, ls="--")
    ax.set(yscale="log", xlim=(-1, len(pts)), xticks=[])
    _log_axis(ax.yaxis)
    top = ax.get_ylim()[1]
    ax.text(split / 2, top, "Held out, cheapest to dearest", ha="center", va="bottom", color=MUTED, fontsize=10)
    if result["n"]["fresh"]:
        ax.text(split + (len(pts) - split) / 2, top, "Fresh deals, cheapest to dearest", ha="center", va="bottom", color=MUTED, fontsize=10)
    b, a = (result[s][k] for s, k in (("holdout", "today_served"), ("holdout", result["picked"]["range"])))

    def holds(x: dict, k: str) -> str:
        return f"holds {x['coverage80']:.0%} held out" + (f" / {result['fresh'][k]['coverage80']:.0%} fresh" if result["n"]["fresh"] else "")
    handles = [plt.Line2D([], [], color=BEFORE_C, lw=3), plt.Line2D([], [], color=AFTER_C, lw=3),
               plt.Line2D([], [], color=TEXT, marker="o", ls="", markersize=5)]
    ax.legend(handles, [f"{names[0]}: 80% range, median {b['width80']:.1f}× wide, {holds(b, 'today_served')}",
                        f"{names[1]}: 80% range, median {a['width80']:.1f}× wide, {holds(a, result['picked']['range'])}",
                        "Price WLDD paid"], loc="upper left", fontsize=10)
    ax.set_ylabel("₹ per reel")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def importance(values: dict[str, float], title: str, path: Path, permutation: bool = False, top: int = 12) -> None:
    """Linear models: mean |SHAP| in log price, labelled as a price multiplier. Others: permutation importance, which is
    a drop in R² and has no price meaning, so it is labelled as is."""
    items = list(values.items())[:top][::-1]
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.barh([n for n, _ in items], [v for _, v in items], color=AFTER_C, height=0.6)
    for i, (_, v) in enumerate(items):
        ax.text(v, i, f"  {v:.3f}" if permutation else f"  ×{math.exp(v):.2f}", va="center", color=TEXT, fontsize=10)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", colors=TEXT)
    ax.set_xlabel("Drop in R² when the feature is shuffled (permutation importance)" if permutation
                  else "Typical effect on price (mean |SHAP| in log price; label: as a multiplier)")
    ax.set_title(title, color=TEXT, loc="left", fontsize=12)
    ax.set_xlim(0, max(v for _, v in items) * 1.25)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def learning(curves: dict[str, list[dict]], labels: dict[str, str], n_test: int, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for (name, curve), color in zip(curves.items(), (BEFORE_C, AFTER_C)):
        n = [c["n"] for c in curve]
        ax.fill_between(n, [c["low"] for c in curve], [c["high"] for c in curve], color=color, alpha=0.15, linewidth=0)
        ax.plot(n, [c["error"] for c in curve], color=color, lw=2, marker="o", markersize=7, label=labels[name])
        ax.text(n[-1], curve[-1]["error"], f"  {curve[-1]['error']:.0%}", va="center", color=TEXT, fontsize=10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_xlabel("WLDD deals the model learned from")
    ax.set_ylabel(f"Median error on the {n_test} test deals")
    ax.set_title("More deals, smaller error? Shaded: best and worst of 20 random draws", color=TEXT, loc="left", fontsize=12)
    ax.legend(loc="upper right", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)
