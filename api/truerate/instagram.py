import gzip
import hashlib
import json
import random
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import httpx

BASE_URL = "https://api.hikerapi.com"
# Instagram's grey default avatar; an account showing it has no profile picture.
DEFAULT_PIC = "573323465_1219825463302212_7278921664109726296_n"


class HikerError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _has_pic(url: str | None) -> bool:
    return bool(url) and DEFAULT_PIC not in url


def parse_profile(raw: dict) -> dict:
    return {
        "pk": str(raw["pk"]),
        "username": raw["username"],
        "full_name": raw.get("full_name") or "",
        "followers": raw["follower_count"],
        "following": raw["following_count"],
        "posts": raw["media_count"],
        "bio": raw.get("biography") or "",
        "external_url": raw.get("external_url") or "",
        "category": raw.get("category_name") or raw.get("category") or "",
        "is_private": raw["is_private"],
        "is_verified": raw["is_verified"],
        "has_pic": _has_pic(raw.get("profile_pic_url")),
    }


def parse_about(raw: dict) -> dict:
    return {"country": raw.get("country") or "", "joined": raw.get("date") or "", "former_usernames": int(raw.get("former_usernames") or 0)}


def parse_accounts(users: list[dict]) -> list[dict]:
    return [
        {
            "pk": str(u["pk"]),
            "username": u["username"],
            "full_name": u.get("full_name") or "",
            "is_private": bool(u.get("is_private")),
            "is_verified": bool(u.get("is_verified")),
            "has_pic": _has_pic(u.get("profile_pic_url")),
        }
        for u in users
    ]


def parse_reels(items: list[dict]) -> list[dict]:
    return [
        {
            "id": str(it["pk"]),
            "code": it["code"],
            "taken_at": it["taken_at"],
            "views": it.get("play_count") or 0,
            "likes": it.get("like_count") or 0,
            "comments": it.get("comment_count") or 0,
            "caption": it.get("caption_text") or "",
            "paid": bool(it.get("is_paid_partnership")),
            "sponsors": [u["username"] for u in it.get("sponsor_tags") or []],
            "coauthors": [u["username"] for u in it.get("coauthor_producers") or []],
            "tags": [t["user"]["username"] for t in it.get("usertags") or []],
            "thumbnail": it.get("thumbnail_url") or "",
            "duration": it.get("video_duration") or 0,
            "counts_hidden": bool(it.get("like_and_view_counts_disabled")),
        }
        for it in items
    ]


def mark_pinned(reels: list[dict]) -> list[dict]:
    """Instagram lists pinned reels first, so a reel older than one listed after it is pinned."""
    newest_after = ""
    for r in reversed(reels):
        r["pinned"] = r["taken_at"] < newest_after
        newest_after = max(newest_after, r["taken_at"])
    return reels


def parse_comments(items: list[dict]) -> list[dict]:
    return [
        {"id": str(c["pk"]), "text": c.get("text") or "", "at": c["created_at_utc"], "likes": c.get("like_count") or 0, "user": parse_accounts([c["user"]])[0]}
        for c in items
    ]


class Hiker:
    """HikerAPI client. Every raw response is saved once as a gzipped file under `store` and kept, so each call is
    paid for once. Raw, not parsed, so a parser change needs no new request."""

    def __init__(self, key: str, store: Path, http: httpx.Client | None = None):
        self.store = store
        self.http = http or httpx.Client(base_url=BASE_URL, headers={"x-access-key": key}, timeout=60)

    def _file(self, path: str, params: dict) -> Path:
        query = urlencode(sorted(params.items()))
        readable = re.sub(r"[^A-Za-z0-9._=-]+", "_", query)[:80]
        return self.store / path.strip("/").replace("/", "_") / f"{readable}-{hashlib.sha1(query.encode()).hexdigest()[:10]}.json.gz"

    def _get(self, path: str, parse, **params):
        file = self._file(path, params)
        if file.exists():
            return parse(json.loads(gzip.decompress(file.read_bytes())))
        for attempt in range(3):
            r = self.http.get(path, params=params)
            if r.status_code != 429:
                break
            time.sleep(1 + attempt)
        if r.status_code != 200:
            raise HikerError(r.status_code, f"HikerAPI {r.status_code} on {path}: {r.text[:200]}")
        raw = r.json()
        file.parent.mkdir(parents=True, exist_ok=True)
        # A unique temp name, then an atomic rename: no half-written file after a crash, and two threads saving
        # the same response never trip over each other.
        tmp = file.with_name(f"{file.name}.{uuid.uuid4().hex}.tmp")
        tmp.write_bytes(gzip.compress(r.content))
        tmp.replace(file)
        return parse(raw)

    def profile(self, username: str) -> dict:
        return self._get("/v1/user/by/username", parse_profile, username=username)

    def about(self, pk: str) -> dict:
        return self._get("/gql/user/about", parse_about, id=pk)

    def reels(self, pk: str, pages: int = 3) -> list[dict]:
        reels, cursor = [], None
        for _ in range(pages):
            params = {"user_id": pk} | ({"end_cursor": cursor} if cursor else {})
            page = self._get("/v1/user/clips/chunk", lambda raw: {"reels": parse_reels(raw[0]), "cursor": raw[1]}, **params)
            reels += page["reels"]
            cursor = page["cursor"]
            if not cursor or not page["reels"]:
                break
        return mark_pinned(reels)

    def comments(self, media_id: str) -> list[dict]:
        return self._get("/v1/media/comments/chunk", lambda raw: parse_comments(raw[0]), id=media_id)

    def likers(self, media_id: str, n: int = 200) -> list[dict]:
        # One call returns ~2,000 likers; a seeded sample of 200 keeps Mongo small.
        def parse(raw):
            accounts = parse_accounts(raw)
            return random.Random(media_id).sample(accounts, min(n, len(accounts)))

        return self._get("/v1/media/likers", parse, id=media_id)

    def followers(self, pk: str) -> list[dict]:
        return self._get("/v1/user/followers/chunk", lambda raw: parse_accounts(raw[0]), user_id=pk)

    def suggested(self, pk: str) -> list[dict]:
        return self._get("/v2/user/suggested/profiles", lambda raw: parse_accounts(raw["users"]), user_id=pk)


def collect(hiker: Hiker, handle: str, comment_reels: int = 10, liker_reels: int = 3) -> dict:
    """One snapshot of a creator: about 20 requests. A private account stops after the profile."""
    profile = hiker.profile(handle)
    data = {"profile": profile}
    snap = {"handle": handle, "fetched_at": datetime.now(timezone.utc), "followers": profile["followers"], "data": data}
    if profile["is_private"]:
        return snap
    pk = profile["pk"]
    reels = hiker.reels(pk)
    recent = [r for r in reels if not r["pinned"]]
    data |= {
        "about": _or_empty(hiker.about, pk, {"country": "", "joined": "", "former_usernames": 0}),
        "reels": reels,
        "comments": {r["id"]: _or_empty(hiker.comments, r["id"]) for r in recent[:comment_reels]},
        "likers": {r["id"]: _or_empty(hiker.likers, r["id"]) for r in recent[:liker_reels]},
        "followers": _or_empty(hiker.followers, pk),
        "suggested": _or_empty(hiker.suggested, pk),
    }
    return snap


def _or_empty(fetch, key: str, empty=None):
    """HikerAPI answers 404 for comments turned off, hidden followers, an account it can't describe and the like.
    Those count as empty (`[]` unless given), not as a failed creator."""
    try:
        return fetch(key)
    except HikerError as e:
        if e.status == 404:
            return [] if empty is None else empty
        raise


def fetch_covers(reels: list[dict], limit: int = 6) -> dict[str, bytes]:
    """Cover images by reel code, from Instagram's CDN (not HikerAPI, so no credit). Failures are skipped."""
    covers = {}
    with httpx.Client(timeout=10, follow_redirects=True) as http:
        for r in reels[:limit]:
            try:
                resp = http.get(r["thumbnail"])
            except httpx.HTTPError:
                continue
            if resp.status_code == 200:
                covers[r["code"]] = resp.content
    return covers
