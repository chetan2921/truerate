"""Builds the pitch deck (at most 12 slides, DESIGN.md colours) from the validation and red-team reports.

    cd api && uv run python scripts/make_deck.py                      # real reports in data/models
    cd api && uv run python scripts/make_deck.py --models-dir data/models_dev

Writes data/pitch/TruRate.pptx. The deck stays out of git: its chart comes from WLDD's prices.
Arial, not Urbanist: a .pptx can't embed fonts and must look right on any judging laptop.
"""

import argparse
import json
import math
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.chart.data import XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_MARKER_STYLE
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

REPO = Path(__file__).resolve().parents[2]
BG, SURFACE, TEXT = RGBColor(0x13, 0x13, 0x13), RGBColor(0x20, 0x20, 0x20), RGBColor(0xFB, 0xFB, 0xFB)
MUTED, LINE = RGBColor(0xA6, 0xA6, 0xA6), RGBColor(0x3A, 0x3A, 0x3A)
ACCENT, NEGOTIATE, AVOID, INFO = RGBColor(0x96, 0xFF, 0x43), RGBColor(0xFF, 0xF1, 0x36), RGBColor(0xF5, 0x66, 0x6E), RGBColor(0x97, 0xBA, 0xFF)
FONT = "Arial"
FAKES = {
    "flat_views": ("Flat views", "Every reel set to the same views"),
    "flat_views_noise": ("Flat views with noise", "Same views, plus or minus 10%"),
    "bot_likers": ("Bot likers", "Half the likers swapped for bots, likes inflated"),
    "pod_comments": ("Pod comments", "12 accounts, generic comments on 80% of reels"),
    "bought_followers": ("Bought followers", "Followers tripled, 70% of the newest are bots"),
    "smart_fake": ("Smart fake", "All of the above, mild, specific-sounding comments"),
}
BANDS = [("small", "Under 20K"), ("medium", "20K to 100K"), ("big", "100K+")]


def pct(x) -> str:
    return "n/a" if x is None else f"{x:.0%}"


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)

    def slide(self, title: str, note: str = ""):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = BG
        self.text(s, 0.6, 0.45, 12, 0.9, [(title, 30, TEXT, True)])
        if note:
            self.text(s, 0.6, 6.85, 12, 0.4, [(note, 11, MUTED, False)])
        return s

    def text(self, s, x, y, w, h, lines, gap=6):
        box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = box.text_frame
        tf.word_wrap = True
        for i, (txt, size, color, bold) in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(gap)
            run = p.add_run()
            run.text = txt
            run.font.name, run.font.size, run.font.bold = FONT, Pt(size), bold
            run.font.color.rgb = color
        return box

    def table(self, s, x, y, widths, rows, size=13, bold_row=None, colors=None):
        shape = s.shapes.add_table(len(rows), len(widths), Inches(x), Inches(y), Inches(sum(widths)), Inches(0.42 * len(rows)))
        tbl = shape.table
        _plain_style(tbl)
        for j, w in enumerate(widths):
            tbl.columns[j].width = Inches(w)
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                cell = tbl.cell(i, j)
                cell.fill.solid()
                cell.fill.fore_color.rgb = SURFACE if i == 0 else BG
                cell.margin_left = cell.margin_right = Inches(0.12)
                cell.margin_top = cell.margin_bottom = Inches(0.07)
                _bottom_rule(cell)
                run = cell.text_frame.paragraphs[0].add_run()
                run.text = str(value)
                run.font.name, run.font.size = FONT, Pt(size)
                run.font.bold = i == 0 or i == bold_row
                run.font.color.rgb = MUTED if i == 0 else (colors or {}).get((i, j), TEXT)
        return shape


def _plain_style(tbl):
    """PowerPoint's "No Style, No Grid", so tables don't get the default heavy white grid."""
    tbl_pr = tbl._tbl.tblPr
    for old in tbl_pr.findall(qn("a:tableStyleId")):
        tbl_pr.remove(old)
    etree.SubElement(tbl_pr, qn("a:tableStyleId")).text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"


def _bottom_rule(cell):
    """A hairline under each row, in the DESIGN.md line colour."""
    tc_pr = cell._tc.get_or_add_tcPr()
    ln = etree.SubElement(tc_pr, qn("a:lnB"), w="9525")
    fill = etree.SubElement(ln, qn("a:solidFill"))
    etree.SubElement(fill, qn("a:srgbClr"), val=str(LINE))


def _log_axes(chart):
    """python-pptx has no log-scale switch; set c:logBase on both value axes."""
    ns = "http://schemas.openxmlformats.org/drawingml/2006/chart"
    for ax in chart._chartSpace.findall(f".//{{{ns}}}valAx"):
        scaling = ax.find(f"{{{ns}}}scaling")
        log = etree.SubElement(scaling, f"{{{ns}}}logBase")
        log.set("val", "10")
        scaling.remove(log)
        scaling.insert(0, log)


def build_deck(report: dict, rt: dict, screenshot: Path | None, out: Path) -> None:
    d = Deck()
    h = report["holdout"]
    model_err = h["model"]["median_error"]

    s = d.slide("")
    d.text(s, 0.6, 2.2, 12, 1.4, [("TruRate", 66, TEXT, True)])
    d.text(s, 0.6, 3.6, 11, 1.2, [("What one reel is worth, and whether WLDD should book the creator", 26, ACCENT, False)])
    d.text(s, 0.6, 5.2, 11, 1, [(f"Held-out median error {pct(model_err)} against {pct(h['modash']['median_error'])} for a Modash-style formula. "
                                 f"Smart fakes caught: {pct(rt['caught']['smart_fake'])}.", 18, TEXT, False),
                                ("WLDD hackathon · Problem 02", 14, MUTED, False)])

    s = d.slide("Brands overpay for audiences that aren't there")
    d.table(s, 0.6, 1.6, [3.2, 4.6, 4.3], [
        ["Fraud", "What it looks like", "How TruRate catches it"],
        ["Bought followers", "A block of empty accounts, views far below followers", "Fake-looking newest followers; views per follower"],
        ["Seeded views", "Views with no real viewers behind them", "Likes per view; views and likes too even"],
        ["Engagement pods", "Real accounts trading comments", "Repeat commenters; Louvain rings across WLDD creators"],
        ["Hidden ads", "Paid reels without #ad, flattering the views", "Rules, then Gemini with cover images, and Gemini listening to the reel"],
    ], size=15)
    d.text(s, 0.6, 4.6, 12, 1.4, [("Paste any face creator. Get a fair price per reel, a range, what it should deliver, and Go, Negotiate or Avoid with the reasons.", 20, TEXT, False)])

    s = d.slide("From a handle to a price in about a minute", "Judging 1: architecture")
    steps = [("Paste a creator", "Handle, optional product, quote, budget"), ("Read Instagram", "About 20 HikerAPI requests, each saved once"),
             ("Find ads", "Rules, then Gemini with covers"), ("Check the audience", "3 families against WLDD creators of the same size"),
             ("Price", "Ridge on WLDD's deals, then adjusted"), ("Decide", "Go, Negotiate or Avoid, with reasons")]
    for i, (t, sub) in enumerate(steps):
        d.text(s, 0.6 + i * 2.1, 2.0, 1.75, 1.8, [(t, 17, ACCENT if i in (3, 4) else TEXT, True), (sub, 12, MUTED, False)])
        if i < len(steps) - 1:
            d.text(s, 2.42 + i * 2.1, 1.95, 0.3, 0.5, [("›", 24, ACCENT, True)])
    d.text(s, 0.6, 4.5, 12, 1.6, [("FastAPI, MongoDB, scikit-learn (Ridge, RandomForest, IsolationForest), MiniLM, networkx Louvain, MediaPipe, Gemini; Next.js report.", 15, MUTED, False),
                                  ("Every number on the report shows its basis and the similar-creator comparison.", 15, TEXT, False)])

    s = d.slide("Signals, and why each one is there", "Judging 2: signals")
    d.table(s, 0.6, 1.5, [2.0, 4.6, 5.5], [
        ["Area", "Signal", "Why"],
        ["Authenticity", "Fake-looking likers (account model, ~600 likers)", "Like counts are cheap to fake; account quality is not"],
        ["Authenticity", "Newest followers; views per follower", "Bought followers arrive as a block and bring no reach"],
        ["Authenticity", "Likes per view; evenness across reels", "Seeded views don't like; bot delivery is flat"],
        ["Authenticity", "Generic and repeated comments; repeat commenters; rings", "Pods use real accounts; only coordination shows"],
        ["Engagement", "Per-view engagement, percentile in the follower band", "Comparable across account sizes"],
        ["Placement", "Paid vs own, collab vs own, consistency, trend", "A brand buys sponsored performance and the floor"],
        ["Audience", "Niche, commenter mix, languages, product fit", "The same views are worth more in some categories"],
    ], size=12)

    s = d.slide("Pricing across small, medium and big creators", "Judging 3: pricing logic")
    d.text(s, 0.6, 1.5, 6.6, 4.5, [
        ("Market price", 18, ACCENT, True),
        (("Ridge regression on log price over WLDD's deals: views, followers, engagement, comments and category. Leave-one-out gave the 6-nearest-deals estimate "
          "no weight, so they are shown as comparables only." if report["blend_weight"] >= 0.99 else
          f"A blend in log space of Ridge on log price ({report['blend_weight']:.0%}) and the 6 most similar past WLDD deals' ₹ per 1,000 views, weighted by leave-one-out."), 14, TEXT, False),
        ("Adjustments", 18, ACCENT, True),
        ("Sponsored performance: paid reels' share of own-reel views, pulled toward WLDD's typical drop when there are few ads. It only discounts, to half at most.", 14, TEXT, False),
        ("Fake engagement: only the fake share above similar creators comes off.", 14, TEXT, False),
        ("Range", 18, ACCENT, True),
        (f"{report.get('range_method', 'Leave-one-out errors')}: each creator's interval comes from out-of-fold errors over 10 refits. "
         f"It held {report['holdout']['coverage']:.0%} of held-out real prices.", 14, TEXT, False),
        ("Past WLDD's largest creator the range widens upward, and the published market asking price for that size is shown beside it, never mixed in.", 14, TEXT, False),
    ])
    d.table(s, 7.6, 1.6, [2.0, 1.6, 1.6], [["Follower band", "TruRate", "Band median"]] +
            [[label, pct(h["model"]["by_band"][b]), pct(h["band_median"]["by_band"][b])] for b, label in BANDS], size=14)

    s = d.slide("Tested against prices WLDD actually paid", "Judging 5: tested against known prices. Points are held-out creators, never seen in training.")
    # Axes in ₹ lakh on a log scale, fitted to the data in powers of 10; the dashed line is "predicted equals paid".
    values = [v / 1e5 for p in h["points"] for v in (p["actual"], p["predicted"])]
    lo, hi = 10 ** math.floor(math.log10(min(values))), 10 ** math.ceil(math.log10(max(values)))
    data = XyChartData()
    series = data.add_series("Held-out creators")
    for p in h["points"]:
        series.add_data_point(p["actual"] / 1e5, p["predicted"] / 1e5)
    equal = data.add_series("Equal")
    equal.add_data_point(lo, lo)
    equal.add_data_point(hi, hi)
    chart = s.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, Inches(0.6), Inches(1.4), Inches(6.4), Inches(5.2), data).chart
    chart.has_legend = False
    _log_axes(chart)
    for ax, title in ((chart.category_axis, "What WLDD paid (₹ lakh)"), (chart.value_axis, "TruRate's price (₹ lakh)")):
        ax.minimum_scale, ax.maximum_scale = lo, hi
        ax.tick_labels.number_format, ax.tick_labels.number_format_is_linked = "General", False
        ax.has_major_gridlines = False
        ax.tick_labels.font.color.rgb, ax.tick_labels.font.size, ax.tick_labels.font.name = MUTED, Pt(11), FONT
        ax.format.line.color.rgb = LINE
        ax.has_title = True
        ax.axis_title.text_frame.text = title
        run = ax.axis_title.text_frame.paragraphs[0].runs[0]
        run.font.color.rgb, run.font.size, run.font.name = MUTED, Pt(12), FONT
    plot = chart.plots[0].series[0]
    plot.marker.style, plot.marker.size = XL_MARKER_STYLE.CIRCLE, 9
    plot.marker.format.fill.solid()
    plot.marker.format.fill.fore_color.rgb = ACCENT
    plot.marker.format.line.color.rgb = ACCENT
    plot.format.line.fill.background()
    line = chart.plots[0].series[1]
    line.marker.style = XL_MARKER_STYLE.NONE
    line.format.line.color.rgb = MUTED
    line.format.line.dash_style = MSO_LINE.DASH
    line.format.line.width = Pt(1.25)
    d.table(s, 7.4, 1.6, [3.2, 1.8], [["Method", "Median error"],
                                     ["TruRate", pct(model_err)],
                                     ["Band median price", pct(h["band_median"]["median_error"])],
                                     ["Modash-style formula", pct(h["modash"]["median_error"])]], size=14, bold_row=1)
    d.text(s, 7.4, 3.6, 5.4, 2.4, [(f"{h['n']} creators held out, 10 per follower tier. {pct(h['coverage'])} of their real prices fall inside TruRate's range.", 15, TEXT, False),
                                   ("Prices were agreed at different past dates but only today's stats are visible, so some error is a floor.", 13, MUTED, False)])

    s = d.slide("Error by category", f"Leave-one-out over all {report['n_deals']} deals: each deal priced by a model that never saw it.")
    rows = [["Category", "Deals", "TruRate", "Band median", "Modash-style"]]
    rows += [[c, v["n"], pct(v["model"]), pct(v["band_median"]), pct(v["modash"])] for c, v in report["by_category"].items()]
    d.table(s, 0.6, 1.5, [4.0, 1.4, 1.8, 1.9, 1.9], rows, size=14)

    s = d.slide("Built to resist gaming", "Judging 4: each fake is built from a real WLDD creator's data. Caught means a verdict other than Real audience.")
    rows, colors = [["Fake", "How it is built", "Caught", "Price cut"]], {}
    for i, (kind, rate) in enumerate(rt["caught"].items(), start=1):
        name, how = FAKES.get(kind, (kind, ""))
        rows.append([name, how, pct(rate), pct(1 - rt["genuine_share"][kind])])
        colors[(i, 2)] = ACCENT if rate >= 0.8 else NEGOTIATE if rate >= 0.5 else AVOID
    d.table(s, 0.6, 1.5, [2.8, 5.6, 1.6, 1.6], rows, size=14, colors=colors)
    d.text(s, 0.6, 5.0, 12, 1, [(f"{pct(rt['unmodified_flagged'])} of {rt['n']} unmodified WLDD creators get flagged. Pods discount nothing: they are real accounts, so they shape the decision instead.", 15, TEXT, False)])

    s = d.slide("The report the team reads mid-negotiation")
    if screenshot and screenshot.exists():
        s.shapes.add_picture(str(screenshot), Inches(0.6), Inches(1.4), width=Inches(8.4))
        d.text(s, 9.4, 1.5, 3.4, 4.8, [("Price, range and decision first.", 16, TEXT, True),
                                       ("Below it on the page: the waterfall with its 6 comparable WLDD deals, a quote checker, the five evidence sections, and lines to copy into the chat.", 14, MUTED, False)])
    else:
        d.text(s, 0.6, 2.0, 12, 2, [("Live demo: paste an unseen creator on /.", 22, TEXT, False)])

    s = d.slide("Made for the negotiation, not just the verdict")
    d.table(s, 0.6, 1.5, [3.2, 8.9], [
        ["Tool", "What it does"],
        ["Quote check", "Below, within or above range; the gap; a counter-offer; 3 data-backed points"],
        ["Negotiation lines", "Open, target and walk-away prices with copyable lines"],
        ["Batch shortlist", "Up to 50 creators ranked by cost per 1,000 views, Avoid last, export to CSV"],
        ["Rate card", "₹ per 1,000 views by category, and a calculator from views wanted to budget"],
        ["Client one-pager", "Decision, waterfall and red flags on A4"],
        ["Possible competitor", "A brand in the product's category in the last 60 days, on the grid or tagging the creator: check exclusivity"],
    ], size=15)

    s = d.slide("Pages without a face", "Judging 6: strategy for other page types")
    d.table(s, 0.6, 1.5, [3.0, 9.1], [
        ["Page type", "How the value and price change"],
        ["Faceless and meme pages", "The page's delivery record replaces creator trust; guaranteed views with a free repost; repost and owner-network detection, cross-posted views counted once"],
        ["UGC creators", "Production fee by format, distribution by this model (often near zero), usage rights per month; content-only vs content-plus-post quotes split them"],
        ["Instagram IPs", "Retention: series lift, episode drop-off, returning commenters; season packages priced on the trend"],
        ["Across all", "Delivered views, account sampling, comparables and authenticity carry over; check new prices by backtests and shadow pricing"],
    ], size=15)

    s = d.slide("What it can't do yet, said plainly")
    d.text(s, 0.6, 1.5, 12, 4.5, [
        ("Follower spikes are a proxy: Instagram shares no follower history, so we read the newest followers. History builds from our first snapshot.", 16, TEXT, False),
        ("Deal prices were agreed at different dates; only today's stats exist. That noise sets an accuracy floor.", 16, TEXT, False),
        ("Hidden-ad detection is probabilistic; reels it can't call stay out of the paid-vs-own comparison.", 16, TEXT, False),
        ("The face check sees any face; it only turns away clearly faceless pages.", 16, TEXT, False),
        ("Next: post-campaign checks of predicted against delivered views, recalibrated monthly.", 16, ACCENT, False),
    ], gap=12)

    out.parent.mkdir(parents=True, exist_ok=True)
    d.prs.save(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--models-dir", default=str(REPO / "data" / "models"))
    ap.add_argument("--screenshot", default=str(REPO / "data" / "pitch" / "report.png"))
    ap.add_argument("--out", default=str(REPO / "data" / "pitch" / "TruRate.pptx"))
    a = ap.parse_args()
    models = Path(a.models_dir) if Path(a.models_dir).is_absolute() else REPO / a.models_dir
    build_deck(json.loads((models / "model_report.json").read_text()), json.loads((models / "redteam.json").read_text()), Path(a.screenshot), Path(a.out))
    print(f"Wrote {a.out}")
