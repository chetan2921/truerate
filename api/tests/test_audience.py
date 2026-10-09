import json

import numpy as np
from typer.testing import CliRunner

from truerate import cli

from truerate.signals import AUDIENCE_SIGNALS, FAKE_KINDS, audience_signals, commenter_mix, commenter_rings, face_share, band_norms, comment_signals, genuine_share, make_fake, redteam, train_fake_model, verdict


VOCAB = {}


def fake_embed(texts):
    """Stands in for MiniLM: the same lowercased text gives the same unit vector; different texts are nearly unrelated."""
    out = []
    for t in texts:
        key = t.lower().strip(" !.")
        if key not in VOCAB:
            v = np.random.default_rng(len(VOCAB)).normal(size=256)
            VOCAB[key] = v / np.linalg.norm(v)
        out.append(VOCAB[key])
    return np.array(out)


def comment(user, text):
    return {"text": text, "user": {"username": user}}


def test_comment_signals_find_generic_repeated_and_pod_comments():
    by_reel = {
        "r1": [comment("pod_a", "Great content"), comment("fan1", "Where is this cafe?"), comment("fan2", "🔥🔥"), comment("pod_b", "loved the edit at 0:12")],
        "r2": [comment("pod_a", "great content!"), comment("fan3", "Recipe please"), comment("pod_b", "Which camera is this")],
        "r3": [comment("pod_a", "nice"), comment("fan4", "My mom makes this too"), comment("pod_b", "the colours here")],
        "r4": [comment("fan5", "Finally a part 2")],
        "r5": [comment("fan6", "What song is this")],
    }
    s = comment_signals(by_reel, fake_embed)
    # generic: "Great content" ×2 and "nice" (templates), "🔥🔥" (emoji only) = 4 of 12
    assert s["n_comments"] == 12 and s["generic_comments"] == round(4 / 12, 4)
    # pod_a and pod_b each commented on 3 of the 5 reels (60%)
    assert s["repeat_commenters"] == 2


def creator(**overrides):
    base = {"fake_likers": 0.08, "likes_per_view": 0.05, "views_cv": 0.9, "likes_cv": 0.8, "fake_followers": 0.10,
            "views_per_follower": 0.4, "generic_comments": 0.2, "repeat_commenters": 0, "followers": 50_000}
    return base | overrides


def genuine_band(n=40, seed=3):
    rng = np.random.default_rng(seed)
    return [creator(fake_likers=float(rng.uniform(0.04, 0.12)), likes_per_view=float(rng.uniform(0.03, 0.07)), views_cv=float(rng.uniform(0.6, 1.4)),
                    likes_cv=float(rng.uniform(0.5, 1.3)), fake_followers=float(rng.uniform(0.05, 0.15)), views_per_follower=float(rng.uniform(0.2, 0.8)),
                    generic_comments=float(rng.uniform(0.1, 0.3)), repeat_commenters=int(rng.integers(0, 2))) for _ in range(n)]


def test_verdict_counts_failing_families_against_the_band():
    norms = band_norms(genuine_band())
    assert verdict(creator(), norms)["verdict"] == "Real audience"
    bot_likers = verdict(creator(fake_likers=0.45), norms)
    assert bot_likers["verdict"] == "Some fake activity" and bot_likers["failed_families"] == ["likes"]
    flag = bot_likers["flags"][0]
    assert flag["signal"] == "fake_likers" and flag["value"] == 0.45 and 0.04 < flag["median"] < 0.12
    assert verdict(creator(fake_likers=0.45, repeat_commenters=9, views_per_follower=0.05), norms)["verdict"] == "Mostly fake"


def test_a_small_gap_is_not_a_flag_even_outside_a_tight_band():
    norms = band_norms([creator(repeat_commenters=0) for _ in range(20)])
    assert verdict(creator(repeat_commenters=2), norms)["verdict"] == "Real audience"
    assert verdict(creator(repeat_commenters=3), norms)["verdict"] == "Some fake activity"


def test_genuine_share_removes_only_fake_engagement_above_the_band():
    norms = band_norms(genuine_band())
    median_fake = verdict(creator(), norms)["medians"]["fake_likers"]
    assert genuine_share(creator(fake_likers=0.40), norms) == round(1 - (0.40 - median_fake), 2)
    assert genuine_share(creator(fake_likers=0.02), norms) == 1.0
    # low likes per view counts only once it is flagged: a quarter of the band's likes per view means about 3/4 of views are suspect
    assert genuine_share(creator(likes_per_view=0.04), norms) == 1.0
    assert genuine_share(creator(likes_per_view=0.0125), norms) < 0.8


def test_every_signal_belongs_to_one_of_three_families():
    assert {family for family, *_ in AUDIENCE_SIGNALS.values()} == {"likes", "followers", "comments"}


def test_audience_signals_from_a_snapshot():
    model = train_fake_model([[1, 0, 2, 0, 0, 0]] * 20 + [[0, 0.6, 0, 0, 0, 0]] * 20, [0] * 20 + [1] * 20)
    real = {"username": "meera", "full_name": "Meera Iyer", "has_pic": True, "is_private": False}
    fake = {"username": "user839201", "full_name": "", "has_pic": False, "is_private": False}
    reels = [{"id": f"r{i}", "taken_at": f"2026-09-{20 - i:02d}T10:00:00Z", "views": 1000 * (i + 1), "likes": 50 * (i + 1), "pinned": False} for i in range(12)]
    snap = {"followers": 10_000, "data": {
        "reels": reels, "likers": {"r0": [real] * 3 + [fake], "r1": [real] * 4}, "followers": [fake, fake, real, real],
        "comments": {"r0": [comment("fan", "Recipe please")]}, "about": {"former_usernames": 2},
    }}
    s = audience_signals(snap, {"likes_per_view": 0.05, "views_per_follower": 0.65}, model, fake_embed)
    assert (s["fake_likers"], s["n_likers"], s["fake_followers"], s["n_followers"]) == (0.125, 8, 0.5, 4)
    assert (s["likes_per_view"], s["views_per_follower"], s["former_usernames"]) == (0.05, 0.65, 2)
    assert 0.5 < s["views_cv"] < 0.6 and s["likes_cv"] == s["views_cv"]


def genuine_snapshot(i, rng):
    """A believable creator: spiky views, real-looking likers and followers with a few bots, specific comments."""
    def person(tag):
        return {"username": f"{tag}.fan", "full_name": "Asha Rao", "has_pic": True, "is_private": False}

    bot = {"username": "user83920174", "full_name": "", "has_pic": False, "is_private": False}
    followers = int(rng.uniform(25_000, 90_000))
    lpv = rng.uniform(0.03, 0.07)
    reels = []
    for j in range(30):
        views = int(followers * 0.4 * rng.lognormal(0, 0.8))
        reels.append({"id": f"c{i}r{j}", "code": f"C{i}R{j}", "taken_at": f"2026-09-{30 - j:02d}T10:00:00Z", "views": views, "likes": int(views * lpv * rng.lognormal(0, 0.2)),
                      "comments": 10, "pinned": False, "paid": False, "sponsors": [], "coauthors": [], "caption": ""})
    likers = {r["id"]: [bot if k % 10 == 0 else person(f"l{k}") for k in range(200)] for r in reels[:3]}
    comments = {r["id"]: [comment(f"c{i}fan{j}_{k}", f"question {i}-{j}-{k} about this reel") for k in range(8)] for j, r in enumerate(reels[:10])}
    return {"handle": f"creator{i}", "followers": followers, "data": {
        "profile": {"followers": followers}, "reels": reels, "likers": likers, "comments": comments,
        "followers": [bot if k % 7 == 0 else person(f"f{k}") for k in range(25)], "about": {"former_usernames": 0},
    }}


def test_redteam_catches_the_four_main_fakes_and_reports_the_smart_one():
    rng = np.random.default_rng(5)
    snaps = [genuine_snapshot(i, rng) for i in range(30)]
    model = train_fake_model([[1, 0, 2, 0, 0, 0]] * 20 + [[0, 0.67, 0, 0, 0, 0]] * 20, [0] * 20 + [1] * 20)
    report = redteam(snaps, model, fake_embed)
    assert report["n"] == 30 and set(report["caught"]) == set(FAKE_KINDS)
    for kind in ("flat_views", "bot_likers", "pod_comments", "bought_followers"):
        assert report["caught"][kind] >= 0.8, (kind, report["caught"][kind])
    assert 0 <= report["caught"]["smart_fake"] <= 1
    assert report["unmodified_flagged"] <= 0.2
    assert report["genuine_share"]["bot_likers"] < 0.8 <= report["genuine_share"]["pod_comments"]


def test_make_fake_leaves_the_original_alone():
    snap = genuine_snapshot(0, np.random.default_rng(1))
    before = snap["data"]["reels"][0]["views"]
    fake = make_fake(snap, "bought_followers", np.random.default_rng(2))
    assert fake["followers"] == snap["followers"] * 3 and snap["data"]["reels"][0]["views"] == before


def test_redteam_command_uses_the_latest_snapshot_of_each_creator_with_metrics(db, tmp_path, monkeypatch):
    rng = np.random.default_rng(5)
    for i in range(12):
        snap = genuine_snapshot(i, rng)
        db.snapshots.insert_one(snap)
        db.metrics.insert_one({"_id": snap["handle"]})
    monkeypatch.setattr(cli, "get_db", lambda: db)
    monkeypatch.setattr(cli, "load_fake_model", lambda: train_fake_model([[1, 0, 2, 0, 0, 0]] * 5 + [[0, 0.67, 0, 0, 0, 0]] * 5, [0] * 5 + [1] * 5))
    monkeypatch.setattr(cli, "minilm_embed", fake_embed)
    result = CliRunner().invoke(cli.app, ["redteam", "--out-dir", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Red-team on 12 WLDD creators" in result.output and "bot_likers" in result.output
    assert json.loads((tmp_path / "redteam.json").read_text())["n"] == 12


def test_commenter_mix_sorts_top_commenters_into_fake_brand_creator_and_person():
    model = train_fake_model([[1, 0, 2, 0, 0, 0]] * 20 + [[0, 0.67, 0, 0, 0, 0]] * 20, [0] * 20 + [1] * 20)

    def user(name, verified=False, bot=False):
        return {"username": name, "full_name": "" if bot else "Asha Rao", "has_pic": not bot, "is_private": False, "is_verified": verified}

    comments = {
        "r1": [comment_by(user("asha.fan"), "so good"), comment_by(user("bigcreator", verified=True), "collab soon?"), comment_by(user("user83920174", bot=True), "nice")],
        "r2": [comment_by(user("asha.fan"), "again!"), comment_by(user("shopbrand"), "DM us"), comment_by(user("ravi.k"), "where is this")],
    }
    labels = {"kinds": {"shopbrand": "brand", "ravi.k": "person"}, "languages": [{"language": "Hinglish", "share": 0.7}]}
    mix = commenter_mix({"data": {"comments": comments}}, model, labels)
    assert mix == {"top": 5, "fake": 1, "brands": 1, "creators": 1, "people": 2, "languages": [{"language": "Hinglish", "share": 0.7}]}


def comment_by(user, text):
    return {"text": text, "user": user}


def test_face_share_is_the_share_of_covers_with_a_face():
    covers = {"a": b"face", "b": b"face", "c": b"food", "d": b"text"}
    assert face_share(covers, lambda img: img == b"face") == 0.5
    assert face_share({}, lambda img: True) is None


def test_commenter_rings_group_creators_who_share_commenters():
    pod = {"p1", "p2", "p3", "p4"}
    commenters = {"a": pod | {"a1"}, "b": pod | {"b1"}, "c": pod | {"c1"}, "d": {"p1", "d1", "d2"}, "e": {"e1"}}
    assert commenter_rings(commenters) == {"a": 2, "b": 2, "c": 2, "d": 0, "e": 0}


def test_signals_without_norms_are_skipped():
    norms = band_norms(genuine_band())  # these creators carry no ring_size
    assert "ring_size" not in norms["medium"]
    assert verdict(creator(ring_size=5), norms)["verdict"] == "Real audience"
