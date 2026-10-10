import json
import re
import threading
from contextlib import asynccontextmanager
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from typing import Literal

import httpx
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from truerate.brand import STEPS as BRAND_STEPS
from truerate.brand import BrandDeps, instagram_brand, run_brand, site_text
from truerate.config import HIKER_DIR, MODELS_DIR, get_settings
from truerate.db import ensure_indexes, get_db
from truerate.instagram import Hiker, HikerError, collect
from truerate.llm import Gemini
from truerate.outputs import outputs
from truerate.pipeline import STEPS, Deps, analyze, check_quote
from truerate.pricing import likely_band, rate_card, thin_categories
from truerate.signals import CATEGORIES, PRODUCTS, _face_detector, _person_detector, minilm_embed

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=_warm, daemon=True).start()
    threading.Thread(target=lambda: fail_interrupted(get_db()), daemon=True).start()
    yield


app = FastAPI(title="TruRate API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

EXECUTOR = ThreadPoolExecutor(max_workers=2)
MAX_BATCH = 50


def fail_interrupted(db) -> None:
    """Jobs run inside this process, so any analysis still "running" at startup was cut off by a stop or restart."""
    db.analyses.update_many({"status": "running"}, {"$set": {"status": "failed", "error": "The server stopped before this analysis finished. Run it again."}})


def submit(fn) -> None:
    EXECUTOR.submit(fn)


# ---- the report (api-surface contract: the web types are generated from these) ----


class Profile(BaseModel):
    full_name: str
    followers: int
    following: int
    posts: int
    bio: str
    is_verified: bool


class Decision(BaseModel):
    call: Literal["Go", "Negotiate", "Avoid"]
    reasons: list[str]


class WaterfallStep(BaseModel):
    step: str
    amount: int


class Comparable(BaseModel):
    handle: str
    price: float
    views: float
    followers: int
    category: str
    per_1k_views: int


class Delivery(BaseModel):
    views: list[int]
    likes: int
    comments: int
    cost_per_1k: int
    category_cost_per_1k: int | None


class MarketReference(BaseModel):
    tier: str
    low: int
    high: int
    source: str


class Price(BaseModel):
    market: int
    fair: int
    low: int
    high: int
    likely_low: int | None = None  # about half of real prices land in this band; filled in on read for older reports
    likely_high: int | None = None
    collab_factor: float
    genuine_share: float
    # Defaults keep reports stored before these fields existed readable.
    ridge_share: float = 1.0
    note: str | None = None
    market_reference: MarketReference | None = None
    waterfall: list[WaterfallStep]
    comparables: list[Comparable]
    delivery: Delivery


class Flag(BaseModel):
    signal: str
    family: str
    value: float
    median: float
    text: str


class Language(BaseModel):
    language: str
    share: float


class Mix(BaseModel):
    top: int
    fake: int
    brands: int
    creators: int
    people: int
    languages: list[Language]


class Audience(BaseModel):
    verdict: Literal["Real audience", "Some fake activity", "Mostly fake"]
    failed_families: list[str]
    flags: list[Flag]
    signals: dict[str, float | None]
    medians: dict[str, float]
    warnings: list[str]
    mix: Mix


class Engagement(BaseModel):
    rate: float
    band: Literal["small", "medium", "big"]
    band_median: float | None
    percentile: int | None


class ReelPoint(BaseModel):
    code: str
    taken_at: str
    views: int
    likes: int
    comments: int
    kind: Literal["own", "paid", "collab", "repost"]
    thumbnail: str


class FollowerPoint(BaseModel):
    at: str
    followers: int


class Ratio(BaseModel):
    n: int
    ratio: float | None


class PaidRatio(Ratio):
    typical_ratio: float


class Ad(BaseModel):
    code: str
    taken_at: str
    disclosed: bool
    brand: str | None
    topic: str | None
    spoken: str | None = None  # the promotional words Gemini heard in the reel, if it was a spoken ad


class BrandTag(BaseModel):
    code: str
    taken_at: str
    brand: str
    topic: str | None


class Placement(BaseModel):
    reels: list[ReelPoint]
    followers_history: list[FollowerPoint]
    typical_views: float
    bad_reel_views: float
    hits_last_10: int
    trend: float | None
    paid: PaidRatio
    collab: Ratio
    ads: list[Ad]
    brand_tags: list[BrandTag] = []
    n_reposts: int = 0


class Niche(BaseModel):
    category: str
    topics: dict[str, int]
    product: str | None
    fit: Literal["strong", "good", "some", "weak"] | None
    fit_share: float | None


class Competitor(BaseModel):
    brand: str | None
    days: int
    code: str
    category: str | None = None  # the WLDD category the ad was matched in; older analyses didn't store it


class Cheaper(BaseModel):
    handle: str
    per_1k_views: int
    views: float
    price: float


class Negotiation(BaseModel):
    start: int
    target: int
    walk_away: int
    lines: list[str]


class Source(BaseModel):
    title: str
    url: str


class WebRate(BaseModel):
    """What the web states a big creator charges per reel (only creators bigger than anyone WLDD has booked)."""
    found: bool
    low: int | None
    high: int | None
    summary: str
    sources: list[Source]


class Report(BaseModel):
    handle: str
    profile: Profile
    fetched_at: str
    category: str
    category_source: Literal["wldd", "gemini"]
    face_share: float | None
    web_rate: WebRate | None = None  # creators bigger than anyone WLDD has booked; older reports don't have it
    decision: Decision
    price: Price
    audience: Audience
    engagement: Engagement
    placement: Placement
    niche: Niche
    worth_reaching: str
    competitor: Competitor | None
    cheaper: list[Cheaper]
    suggested: list[str]
    negotiation: Negotiation


class Inputs(BaseModel):
    category: str | None = None
    quote: int | None = None
    budget: int | None = None


class AnalysisRequest(Inputs):
    handle: str


class Created(BaseModel):
    id: str


class Output(BaseModel):
    key: str
    status: Literal["good", "warn", "bad", "info"]
    title: str
    detail: str


class Analysis(BaseModel):
    id: str
    handle: str
    inputs: Inputs
    status: Literal["running", "done", "out_of_scope", "failed"]
    step: int
    steps: list[str]
    reason: str | None = None
    error: str | None = None
    result: Report | None = None
    outputs: list[Output] = []  # plain answers, worked out from the result on every read
    created_at: datetime
    finished_at: datetime | None = None


class AnalysisSummary(BaseModel):
    id: str
    handle: str
    status: str
    call: str | None
    fair: int | None
    low: int | None = None
    high: int | None = None
    verdict: str | None
    created_at: datetime


class QuoteRequest(BaseModel):
    quote: int


class QuoteCheck(BaseModel):
    quote: int
    position: Literal["below", "within", "high", "above"]  # high: inside the full range, above where most deals land
    difference: int
    counter_offer: int
    talking_points: list[str]


class BatchRequest(Inputs):
    handles: list[str]


class BatchRow(BaseModel):
    handle: str
    analysis_id: str
    status: str
    call: str | None
    verdict: str | None
    fair: int | None
    low: int | None
    high: int | None
    cost_per_1k: int | None
    expected_views: int | None
    reason: str | None
    likely_low: int | None = None
    likely_high: int | None = None
    views_low: int | None = None  # a weak and a strong sponsored reel
    views_high: int | None = None
    category_cost_per_1k: int | None = None  # what WLDD usually pays per 1,000 views in the creator's category
    followers: int | None = None
    category: str | None = None
    outputs: list[Output] = []


class Batch(BaseModel):
    id: str
    inputs: Inputs
    created_at: datetime
    total: int
    done: int
    rows: list[BatchRow]


class BatchSummary(BaseModel):
    id: str
    created_at: datetime
    handles: list[str]
    total: int
    done: int


class BrandRequest(BaseModel):
    brand: str  # an Instagram handle or link, a website, or a name
    product: str | None = None
    budget: int | None = None
    count: int = 10


class BrandAnswer(BaseModel):
    key: str
    status: Literal["good", "warn", "bad", "info"]
    title: str


class BrandPick(BaseModel):
    handle: str
    sources: list[str]  # where the creator came from: WLDD booked, Analysed before, Worked with the brand
    category: str | None
    verdict: str | None
    fair: int
    likely_low: int | None
    likely_high: int | None
    cost_per_1k: int | None
    category_cost_per_1k: int | None
    expected_views: int | None
    followers: int | None
    analysis_id: str | None
    score: float
    answers: list[BrandAnswer]
    reasons: list[str]


class BrandProfile(BaseModel):
    name: str
    category: str
    product: str
    audience: str
    tone: str
    price_tier: str
    rivals: list[str]
    source: Literal["instagram", "website", "name"]
    handle: str | None
    url: str | None


class BrandPlan(BaseModel):
    handles: list[str]
    cost: int
    views: int


class BrandResult(BaseModel):
    brand: BrandProfile
    picks: list[BrandPick]
    plan: BrandPlan | None
    to_price: list[str]  # accounts seen with the brand that have no analysis yet
    pool_size: int


class BrandRun(BaseModel):
    id: str
    request: BrandRequest
    status: Literal["running", "done", "failed"]
    step: int
    steps: list[str]
    result: BrandResult | None = None
    error: str | None = None
    created_at: datetime


class BrandSummary(BaseModel):
    id: str
    brand: str
    name: str | None
    status: str
    created_at: datetime


class Per1k(BaseModel):
    p25: int
    median: int
    p75: int


class CategoryRate(BaseModel):
    category: str
    n: int
    per_1k: Per1k
    typical_price: int
    typical_views: int


class ThinCategory(BaseModel):
    category: str
    n: int


class RateCard(BaseModel):
    categories: list[CategoryRate]
    thin: list[ThinCategory] = []  # too few deals for a rate; listed so no category silently disappears


class Product(BaseModel):
    name: str
    category: str


class Meta(BaseModel):
    categories: list[str]
    products: list[Product]
    range_coverage: float | None


class ModelReport(BaseModel):
    validation: dict | None
    redteam: dict | None


# ---- jobs ----

_HANDLE = re.compile(r"^(?:https?://)?(?:www\.)?(?:instagram\.com/)?@?([A-Za-z0-9._]{1,30})/?(?:\?.*)?$")


def parse_handle(text: str) -> str | None:
    m = _HANDLE.match(text.strip())
    return m.group(1).lower() if m else None


@lru_cache
def _models() -> tuple:
    return joblib.load(MODELS_DIR / "fake_accounts.joblib"), joblib.load(MODELS_DIR / "price.joblib")


def _with_likely(result: dict | None) -> dict | None:
    """Reports saved before the likely band existed get it from their own range, as a new report would."""
    p = (result or {}).get("price")
    if p and p.get("likely_low") is None:
        p["likely_low"], p["likely_high"] = likely_band(p["fair"], p["low"], p["high"])
    return result


def _warm() -> None:
    """Load the models at startup, so the first analysis doesn't pay for it. If one is missing, the first request
    reports it instead."""
    try:
        _models()
        minilm_embed(["warm up"])
        _face_detector()
        _person_detector()
    except Exception:
        pass


def make_deps(db) -> Deps:
    settings = get_settings()
    hiker = Hiker(settings.hikerapi_key, HIKER_DIR)
    fake_model, price_model = _models()
    return Deps(db=db, collect=lambda handle: collect(hiker, handle, workers=8), llm=Gemini(settings.llm_api_key, settings.llm_model),
                fake_model=fake_model, embed=minilm_embed, price_model=price_model)


def make_brand_deps(db) -> BrandDeps:
    settings = get_settings()
    hiker = Hiker(settings.hikerapi_key, HIKER_DIR)
    http = httpx.Client(headers={"user-agent": "Mozilla/5.0 (TruRate brand check)"})
    return BrandDeps(db=db, llm=Gemini(settings.llm_api_key, settings.llm_model), price_model=_models()[1],
                     fetch_instagram=lambda handle: instagram_brand(hiker, handle), fetch_site=lambda url: site_text(http, url))


def _run_brand(run_id: str, req: dict) -> None:
    db = get_db()

    def step(i: int) -> None:
        db.brands.update_one({"_id": run_id}, {"$set": {"step": i}})

    try:
        update = {"status": "done", "result": run_brand(make_brand_deps(db), req, step)}
    except HikerError as e:
        handle = req["brand"].strip().lstrip("@")
        message = f"Instagram has no account called @{handle}. Check the spelling, or try the brand's website." if e.status == 404 else str(e)
        update = {"status": "failed", "error": message}
    except Exception as e:  # any failure becomes a readable message with a Retry button in the web
        update = {"status": "failed", "error": str(e)}
    db.brands.update_one({"_id": run_id}, {"$set": update | {"finished_at": datetime.now(timezone.utc)}})


def _run(analysis_id: str, handle: str, inputs: dict) -> None:
    db = get_db()

    def step(i: int) -> None:
        db.analyses.update_one({"_id": analysis_id}, {"$set": {"step": i}})

    try:
        out = analyze(handle, inputs, make_deps(db), step)
        update = {"status": out["status"], "result": out.get("result"), "reason": out.get("reason")}
    except Exception as e:  # any failure becomes a readable message with a Retry button in the web
        update = {"status": "failed", "error": str(e)}
    db.analyses.update_one({"_id": analysis_id}, {"$set": update | {"finished_at": datetime.now(timezone.utc)}})


def _read_json(name: str) -> dict | None:
    path = MODELS_DIR / name
    return json.loads(path.read_text()) if path.exists() else None


# ---- routes ----


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/analyses", status_code=202)
def create_analysis(req: AnalysisRequest) -> Created:
    handle = parse_handle(req.handle)
    if not handle:
        raise HTTPException(422, "Enter an Instagram handle or profile link.")
    db = get_db()
    ensure_indexes(db)
    return Created(id=_start(db, handle, req.model_dump(exclude={"handle"})))


def _start(db, handle: str, inputs: dict, batch_id: str | None = None) -> str:
    analysis_id = uuid.uuid4().hex[:12]
    db.analyses.insert_one({"_id": analysis_id, "handle": handle, "inputs": inputs, "status": "running", "step": 0, "batch_id": batch_id,
                            "created_at": datetime.now(timezone.utc)})
    submit(lambda: _run(analysis_id, handle, inputs))
    return analysis_id


@app.post("/api/brands", status_code=202)
def create_brand_run(req: BrandRequest) -> Created:
    if not req.brand.strip():
        raise HTTPException(422, "Type the brand's Instagram handle, website or name.")
    db = get_db()
    run_id = uuid.uuid4().hex[:12]
    db.brands.insert_one({"_id": run_id, "request": req.model_dump(), "status": "running", "step": 0, "created_at": datetime.now(timezone.utc)})
    submit(lambda: _run_brand(run_id, req.model_dump()))
    return Created(id=run_id)


@app.get("/api/brands")
def list_brand_runs() -> list[BrandSummary]:
    return [BrandSummary(id=b["_id"], brand=b["request"]["brand"], name=((b.get("result") or {}).get("brand") or {}).get("name"), status=b["status"],
                         created_at=b["created_at"]) for b in get_db().brands.find().sort("created_at", -1).limit(10)]


@app.get("/api/brands/{run_id}")
def get_brand_run(run_id: str) -> BrandRun:
    b = get_db().brands.find_one({"_id": run_id})
    if not b:
        raise HTTPException(404, "No brand run with that id.")
    return BrandRun(id=b.pop("_id"), steps=BRAND_STEPS, **{k: v for k, v in b.items() if k != "finished_at"})


@app.post("/api/batches", status_code=202)
def create_batch(req: BatchRequest) -> Created:
    parsed = [parse_handle(h) for h in req.handles]
    bad = [h for h, p in zip(req.handles, parsed) if not p]
    if bad:
        raise HTTPException(422, f"Not Instagram handles: {', '.join(bad)}")
    handles = list(dict.fromkeys(parsed))
    if not handles or len(handles) > MAX_BATCH:
        raise HTTPException(422, f"Paste between 1 and {MAX_BATCH} handles.")
    db = get_db()
    ensure_indexes(db)
    batch_id = uuid.uuid4().hex[:12]
    inputs = req.model_dump(exclude={"handles"})
    db.batches.insert_one({"_id": batch_id, "inputs": inputs, "handles": handles, "created_at": datetime.now(timezone.utc)})
    for handle in handles:
        _start(db, handle, inputs, batch_id)
    return Created(id=batch_id)


@app.get("/api/batches")
def list_batches() -> list[BatchSummary]:
    """The 10 newest batches with their progress, so a running batch can be found again after leaving its page."""
    db = get_db()
    out = []
    for b in db.batches.find().sort("created_at", -1).limit(10):
        statuses = [a["status"] for a in db.analyses.find({"batch_id": b["_id"]}, {"status": 1})]
        out.append(BatchSummary(id=b["_id"], created_at=b["created_at"], handles=b["handles"], total=len(statuses), done=sum(x != "running" for x in statuses)))
    return out


@app.get("/api/batches/{batch_id}")
def get_batch(batch_id: str) -> Batch:
    db = get_db()
    b = db.batches.find_one({"_id": batch_id})
    if not b:
        raise HTTPException(404, "No batch with that id.")
    rows = []
    for a in db.analyses.find({"batch_id": batch_id}):
        r = _with_likely(a.get("result")) or {}
        p = r.get("price", {})
        d = p.get("delivery", {})
        views = d.get("views") or [None, None, None]
        rows.append(BatchRow(handle=a["handle"], analysis_id=a["_id"], status=a["status"], call=r.get("decision", {}).get("call"),
                             verdict=r.get("audience", {}).get("verdict"), fair=p.get("fair"), low=p.get("low"), high=p.get("high"),
                             cost_per_1k=d.get("cost_per_1k"), expected_views=views[1], reason=a.get("reason") or a.get("error"),
                             likely_low=p.get("likely_low"), likely_high=p.get("likely_high"),
                             views_low=views[0], views_high=views[2], category_cost_per_1k=d.get("category_cost_per_1k"),
                             followers=r.get("profile", {}).get("followers"), category=r.get("category"),
                             outputs=outputs(r, a.get("inputs") or {}) if a["status"] == "done" and r else []))
    # Cheapest views first, but never ahead of a creator we wouldn't book: Avoid goes after Go and Negotiate.
    rows.sort(key=lambda x: (x.cost_per_1k is None, x.call == "Avoid", x.cost_per_1k or 0, x.handle))
    return Batch(id=batch_id, inputs=b["inputs"], created_at=b["created_at"], total=len(rows), done=sum(x.status != "running" for x in rows), rows=rows)


@app.get("/api/rate-card")
def get_rate_card() -> RateCard:
    path = MODELS_DIR / "price.joblib"
    if not path.exists():
        raise HTTPException(503, "The price model isn't built yet. Run `truerate validate`.")
    model = joblib.load(path)
    return RateCard(categories=rate_card(model), thin=thin_categories(model))


@app.get("/api/analyses")
def list_analyses() -> list[AnalysisSummary]:
    out = []
    for a in get_db().analyses.find({"hidden": {"$ne": True}}).sort("created_at", -1).limit(50):
        r = a.get("result") or {}
        out.append(AnalysisSummary(id=a["_id"], handle=a["handle"], status=a["status"], call=r.get("decision", {}).get("call"),
                                   fair=r.get("price", {}).get("fair"), low=r.get("price", {}).get("low"), high=r.get("price", {}).get("high"), verdict=r.get("audience", {}).get("verdict"), created_at=a["created_at"]))
    return out


@app.get("/api/analyses/{analysis_id}")
def get_analysis(analysis_id: str) -> Analysis:
    a = get_db().analyses.find_one({"_id": analysis_id})
    if not a:
        raise HTTPException(404, "No analysis with that id.")
    _with_likely(a.get("result"))
    done = outputs(a["result"], a.get("inputs") or {}) if a.get("status") == "done" and a.get("result") else []
    return Analysis(id=a.pop("_id"), steps=STEPS, outputs=done, **a)


@app.delete("/api/analyses/{analysis_id}", status_code=204)
def hide_analysis(analysis_id: str) -> None:
    """Takes it off the recent list. The report itself stays, so a link someone was sent still opens."""
    if not get_db().analyses.update_one({"_id": analysis_id}, {"$set": {"hidden": True}}).matched_count:
        raise HTTPException(404, "No analysis with that id.")


@app.post("/api/analyses/{analysis_id}/quote")
def quote_check(analysis_id: str, req: QuoteRequest) -> QuoteCheck:
    a = get_db().analyses.find_one({"_id": analysis_id})
    if not a:
        raise HTTPException(404, "No analysis with that id.")
    if not a.get("result"):
        raise HTTPException(409, "This analysis has no price to check against.")
    return QuoteCheck(**check_quote(_with_likely(a["result"]), req.quote))


@app.get("/api/meta")
def meta() -> Meta:
    report = _read_json("model_report.json")
    return Meta(categories=list(CATEGORIES), products=[Product(name=n, category=c) for c, names in PRODUCTS.items() for n in names], range_coverage=report["holdout"]["coverage"] if report else None)


@app.get("/api/model-report")
def model_report() -> ModelReport:
    return ModelReport(validation=_read_json("model_report.json"), redteam=_read_json("redteam.json"))
