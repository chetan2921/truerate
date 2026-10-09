import numpy as np

from truerate.signals import AUDIENCE_SIGNALS, audience_signals, band_norms, comment_signals, genuine_share, train_fake_model, verdict


VOCAB = {}


def fake_embed(texts):
    """Stands in for MiniLM: the same lowercased text gives the same vector, anything else is unrelated."""
    vecs = np.zeros((len(texts), 512))
    for i, t in enumerate(texts):
        vecs[i, VOCAB.setdefault(t.lower().strip(" !."), len(VOCAB))] = 1
    return vecs


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
