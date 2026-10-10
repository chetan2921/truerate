import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

from truerate import cli
from truerate.instagram import (
    BASE_URL,
    Hiker,
    HikerError,
    collect,
    mark_pinned,
    parse_about,
    parse_accounts,
    parse_comments,
    parse_profile,
    parse_reels,
    parse_tagged,
)

# Recorded from public account komalpandeyofficial (not a WLDD deal), trimmed, every other account renamed.
FIXTURES = Path(__file__).parent / "fixtures"
ROUTES = {
    "/v1/user/by/username": "profile",
    "/gql/user/about": "about",
    "/v1/user/clips/chunk": "clips",
    "/v1/media/comments/chunk": "comments",
    "/v1/media/likers": "likers",
    "/v1/user/followers/chunk": "followers",
    "/v2/user/suggested/profiles": "suggested",
    "/v2/user/tag/medias": "tagged",
}


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


def fake_hiker(store, calls=None, status=200, private=False, missing=(), disabled=()):
    def handler(request):
        if calls is not None:
            calls.append(request.url.path)
        if status != 200:
            return httpx.Response(status, json={"error": "Top up your account", "exc_type": "InsufficientFunds"})
        if request.url.path in missing:  # comments off, hidden followers and the like
            return httpx.Response(404, json={"detail": "Entries not found", "exc_type": "NotFoundError"})
        if request.url.path in disabled:
            return httpx.Response(403, json={"detail": "Comments disabled by author", "exc_type": "CommentsDisabled"})
        if request.url.path == "/v1/user/clips/chunk" and "end_cursor" in request.url.params:
            return httpx.Response(200, json=[[], None])
        body = fixture(ROUTES[request.url.path])
        if private and request.url.path == "/v1/user/by/username":
            body["is_private"] = True
        return httpx.Response(200, json=body)

    return Hiker("test-key", store, httpx.Client(base_url=BASE_URL, transport=httpx.MockTransport(handler)))


def test_parse_profile_and_about():
    p = parse_profile(fixture("profile"))
    assert p["pk"] == "1203962496" and p["username"] == "komalpandeyofficial"
    assert (p["followers"], p["following"], p["posts"]) == (2061112, 2567, 3413)
    assert p["is_verified"] and not p["is_private"] and p["has_pic"]
    assert parse_about(fixture("about")) == {"country": "India", "joined": "March 2014", "former_usernames": 0}


def test_parse_reels_reads_counts_ads_and_collabs():
    reels = parse_reels(fixture("clips")[0])
    assert len(reels) == 12
    first = reels[0]
    assert first["id"] == "3999681092547569165" and first["code"] == "DeBuMMwJOYN"
    assert (first["views"], first["likes"], first["comments"]) == (1224661, 45915, 574)
    assert first["taken_at"] == "2026-10-03T09:23:09Z" and first["paid"] is False and first["counts_hidden"] is False
    by_code = {r["code"]: r for r in reels}
    assert by_code["DcIhhfPNfcU"]["coauthors"] == ["californiaalmonds_india"]
    assert "#ad" in by_code["DcssQOCNN-n"]["caption"]


def test_parse_reels_reads_tagged_accounts():
    item = fixture("clips")[0][0] | {"usertags": [{"user": {"pk": 1, "username": "brand.x"}, "x": 0.5, "y": 0.5}]}
    assert parse_reels([item])[0]["tags"] == ["brand.x"]


def test_mark_pinned_flags_reels_older_than_a_later_one():
    # The recorded page opens with reels from 10-03, 09-19 and 09-11, then 09-25: the 09-19 and 09-11 reels are pinned.
    pinned = [r["pinned"] for r in mark_pinned(parse_reels(fixture("clips")[0]))]
    assert pinned[:4] == [False, True, True, False] and not any(pinned[4:])


def test_parse_comments_and_accounts():
    comments = parse_comments(fixture("comments")[0])
    assert len(comments) == 15
    assert comments[0]["text"].startswith("layer the belts") and comments[0]["at"] == "2026-10-03T13:04:29Z"
    assert comments[0]["likes"] == 70 and set(comments[0]["user"]) == {"pk", "username", "full_name", "is_private", "is_verified", "has_pic"}
    likers = parse_accounts(fixture("likers"))
    assert len(likers) == 30 and sum(not a["has_pic"] for a in likers) == 5
    assert sum(not a["has_pic"] for a in parse_accounts(fixture("followers")[0])) == 2
    assert len(parse_accounts(fixture("suggested")["users"])) == 10


def test_hiker_saves_each_raw_response_once_on_disk(tmp_path):
    calls = []
    assert fake_hiker(tmp_path, calls).profile("komalpandeyofficial")["followers"] == 2061112
    # a new client on the same folder, as on the next run, reads the file instead of calling HikerAPI
    assert fake_hiker(tmp_path, calls).profile("komalpandeyofficial")["followers"] == 2061112
    assert calls == ["/v1/user/by/username"]
    saved = list(tmp_path.rglob("*.json.gz"))
    # raw, so a parser fix later needs no new request
    assert len(saved) == 1 and json.loads(gzip.decompress(saved[0].read_bytes())) == fixture("profile")


def test_hiker_raises_with_the_status_and_saves_nothing(tmp_path):
    with pytest.raises(HikerError) as err:
        fake_hiker(tmp_path, status=402).profile("anyone")
    assert err.value.status == 402 and "Top up" in str(err.value)
    assert not list(tmp_path.rglob("*.json.gz"))


def test_collect_builds_a_snapshot(tmp_path):
    snap = collect(fake_hiker(tmp_path), "komalpandeyofficial")
    assert snap["handle"] == "komalpandeyofficial" and snap["followers"] == 2061112
    data = snap["data"]
    assert len(data["reels"]) == 12 and data["about"]["country"] == "India"
    # comments on the 10 newest unpinned reels, likers on the 3 newest
    assert len(data["comments"]) == 10 and len(data["likers"]) == 3
    assert "3999681092547569165" in data["likers"] and len(data["likers"]["3999681092547569165"]) == 30
    assert len(data["followers"]) == 48 and len(data["suggested"]) == 10


def test_collect_stops_at_the_profile_for_a_private_account(tmp_path):
    calls = []
    snap = collect(fake_hiker(tmp_path, calls, private=True), "someone")
    assert calls == ["/v1/user/by/username"] and set(snap["data"]) == {"profile"}


def test_collect_benchmark_skips_creators_fetched_in_the_last_day(db, tmp_path, monkeypatch):
    db.deals.insert_many([{"handle": "fresh"}, {"handle": "stale"}])
    db.snapshots.insert_one({"handle": "fresh", "fetched_at": datetime.now(timezone.utc) - timedelta(hours=2)})
    db.snapshots.insert_one({"handle": "stale", "fetched_at": datetime.now(timezone.utc) - timedelta(hours=30)})
    monkeypatch.setattr(cli, "get_db", lambda: db)
    monkeypatch.setattr(cli, "make_hiker", lambda: fake_hiker(tmp_path))
    result = CliRunner().invoke(cli.app, ["collect-benchmark"])
    assert result.exit_code == 0, result.output
    assert "Collected 1, skipped 1 fetched in the last 24 h, failed 0" in result.output
    assert db.snapshots.count_documents({"handle": "stale"}) == 2


def test_collect_benchmark_stops_when_credit_runs_out(db, tmp_path, monkeypatch):
    db.deals.insert_many([{"handle": "a"}, {"handle": "b"}])
    monkeypatch.setattr(cli, "get_db", lambda: db)
    monkeypatch.setattr(cli, "make_hiker", lambda: fake_hiker(tmp_path, status=402))
    result = CliRunner().invoke(cli.app, ["collect-benchmark"])
    assert result.exit_code == 1
    assert result.output.count("402") == 1


def test_collect_benchmark_runs_creators_in_parallel_and_survives_one_failure(db, tmp_path, monkeypatch):
    db.deals.insert_many([{"handle": h} for h in ("a", "b", "c", "d")])
    good = fake_hiker(tmp_path)

    class Flaky:
        """Times out on creator c only, as a network hiccup would."""

        def __getattr__(self, name):
            return getattr(good, name)

        def profile(self, handle):
            if handle == "c":
                raise httpx.ReadTimeout("timed out")
            return good.profile(handle)

    monkeypatch.setattr(cli, "get_db", lambda: db)
    monkeypatch.setattr(cli, "make_hiker", lambda: Flaky())
    result = CliRunner().invoke(cli.app, ["collect-benchmark", "--workers", "4"])
    assert result.exit_code == 0, result.output
    assert "Collected 3, skipped 0 fetched in the last 24 h, failed 1" in result.output and "c: timed out" in result.output
    assert db.snapshots.count_documents({}) == 3


def test_collect_treats_hidden_lists_as_empty(tmp_path):
    hiker = fake_hiker(tmp_path, missing={"/v1/media/comments/chunk", "/v1/user/followers/chunk", "/v1/media/likers", "/v2/user/suggested/profiles"})
    data = collect(hiker, "komalpandeyofficial")["data"]
    assert len(data["reels"]) == 12 and data["followers"] == [] and data["suggested"] == []
    assert all(cs == [] for cs in data["comments"].values()) and all(ls == [] for ls in data["likers"].values())


def test_collect_survives_a_missing_about(tmp_path):
    data = collect(fake_hiker(tmp_path, missing={"/gql/user/about"}), "komalpandeyofficial")["data"]
    assert data["about"] == {"country": "", "joined": "", "former_usernames": 0} and len(data["reels"]) == 12


def test_collect_treats_disabled_comments_as_empty(tmp_path):
    data = collect(fake_hiker(tmp_path, disabled={"/v1/media/comments/chunk"}), "komalpandeyofficial")["data"]
    assert all(cs == [] for cs in data["comments"].values()) and len(data["likers"]) == 3


def test_parse_reels_marks_reposts_with_the_original_author():
    item = fixture("clips")[0][0] | {"clips_metadata": {"originality_info": {"original_media": {"pk": 1, "shortcode": "X", "user": {"username": "original.author"}}}}}
    assert parse_reels([item])[0]["repost_of"] == "original.author"
    assert parse_reels(fixture("clips")[0])[0]["repost_of"] is None


def test_parse_tagged_posts_by_other_accounts():
    tagged = parse_tagged(fixture("tagged")["response"]["items"])
    assert len(tagged) == 7 and tagged[0]["owner"] == "maaatii.official" and tagged[0]["code"] == "DeTYVR1yGef"
    assert tagged[0]["taken_at"] == "2026-10-10T06:01:26Z" and tagged[0]["caption"].startswith("💙 Elegance")


def test_collect_keeps_tagged_posts_by_others_only(tmp_path):
    data = collect(fake_hiker(tmp_path), "komalpandeyofficial")["data"]
    assert len(data["tagged"]) == 6 and "komalpandeyofficial" not in {t["owner"] for t in data["tagged"]}


def test_collect_benchmark_fresh_hours_zero_collects_again(db, tmp_path, monkeypatch):
    db.deals.insert_one({"handle": "fresh"})
    db.snapshots.insert_one({"handle": "fresh", "fetched_at": datetime.now(timezone.utc) - timedelta(hours=1)})
    monkeypatch.setattr(cli, "get_db", lambda: db)
    monkeypatch.setattr(cli, "make_hiker", lambda: fake_hiker(tmp_path))
    result = CliRunner().invoke(cli.app, ["collect-benchmark", "--fresh-hours", "0"])
    assert "Collected 1, skipped 0" in result.output and db.snapshots.count_documents({"handle": "fresh"}) == 2


def test_collect_fetches_the_per_reel_lists_in_parallel_with_the_same_result(tmp_path):
    one = collect(fake_hiker(tmp_path / "a"), "komalpandeyofficial", workers=1)["data"]
    many = collect(fake_hiker(tmp_path / "b"), "komalpandeyofficial", workers=8)["data"]
    assert one == many


def test_comments_start_while_older_reel_pages_are_still_loading(tmp_path):
    import threading

    comments_seen = threading.Event()
    comments_before_last_page = []
    clips = fixture("clips")[0]
    # Page 2: the same reels a year older, under new ids, so the pages never overlap.
    older = [c | {"pk": c["pk"] + "2", "id": c["id"] + "2", "code": c["code"] + "2", "taken_at": c["taken_at"].replace("2026", "2025")} for c in clips]

    def handler(request):
        path, params = request.url.path, request.url.params
        if path == "/v1/media/comments/chunk":
            comments_seen.set()
        if path == "/v1/user/clips/chunk":
            cursor = params.get("end_cursor")
            if cursor == "page3":  # the last page waits briefly: comments for the first page's reels should already be on their way
                comments_before_last_page.append(comments_seen.wait(timeout=3))
                return httpx.Response(200, json=[[], None])
            return httpx.Response(200, json=[clips, "page2"] if cursor is None else [older, "page3"])
        return httpx.Response(200, json=fixture(ROUTES[path]))

    snap = collect(Hiker("test-key", tmp_path, httpx.Client(base_url=BASE_URL, transport=httpx.MockTransport(handler))), "komalpandeyofficial", workers=8)
    assert comments_before_last_page == [True]
    recent = [r for r in snap["data"]["reels"] if not r["pinned"]]
    assert list(snap["data"]["comments"]) == [r["id"] for r in recent[:10]] and list(snap["data"]["likers"]) == [r["id"] for r in recent[:3]]
