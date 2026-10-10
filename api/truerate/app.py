import json
import re
import threading
from contextlib import asynccontextmanager
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from typing import Literal

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from truerate.config import HIKER_DIR, MODELS_DIR, get_settings
from truerate.db import ensure_indexes, get_db
from truerate.instagram import Hiker, collect
from truerate.llm import Gemini
from truerate.pipeline import STEPS, Deps, analyze, check_quote
from truerate.pricing import rate_card, thin_categories
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


class Report(BaseModel):
    handle: str
    profile: Profile
    fetched_at: str
    category: str
    category_source: Literal["wldd", "gemini"]
    face_share: float | None
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
    position: Literal["below", "within", "above"]
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


class Batch(BaseModel):
    id: str
    inputs: Inputs
    created_at: datetime
    total: int
    done: int
    rows: list[BatchRow]


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


@app.get("/api/batches/{batch_id}")
def get_batch(batch_id: str) -> Batch:
    db = get_db()
    b = db.batches.find_one({"_id": batch_id})
    if not b:
        raise HTTPException(404, "No batch with that id.")
    rows = []
    for a in db.analyses.find({"batch_id": batch_id}):
        r = a.get("result") or {}
        p = r.get("price", {})
        rows.append(BatchRow(handle=a["handle"], analysis_id=a["_id"], status=a["status"], call=r.get("decision", {}).get("call"),
                             verdict=r.get("audience", {}).get("verdict"), fair=p.get("fair"), low=p.get("low"), high=p.get("high"),
                             cost_per_1k=p.get("delivery", {}).get("cost_per_1k"), expected_views=(p.get("delivery", {}).get("views") or [None, None])[1],
                             reason=a.get("reason") or a.get("error")))
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
    return Analysis(id=a.pop("_id"), steps=STEPS, **a)


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
    return QuoteCheck(**check_quote(a["result"], req.quote))


@app.get("/api/meta")
def meta() -> Meta:
    report = _read_json("model_report.json")
    return Meta(categories=list(CATEGORIES), products=[Product(name=n, category=c) for c, names in PRODUCTS.items() for n in names], range_coverage=report["holdout"]["coverage"] if report else None)


@app.get("/api/model-report")
def model_report() -> ModelReport:
    return ModelReport(validation=_read_json("model_report.json"), redteam=_read_json("redteam.json"))
