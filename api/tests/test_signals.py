from datetime import datetime, timezone

import joblib
import numpy as np
from typer.testing import CliRunner

from truerate import cli
from truerate.signals import CATEGORIES, KAGGLE_LIGHT, account_features, category_from_niche, fake_share, label_niche, load_kaggle, reel_metrics, train_fake_model

KAGGLE_HEADER = "profile pic,nums/length username,fullname words,nums/length fullname,name==username,description length,external URL,private,#posts,#followers,#follows,fake"


def write_kaggle(path, n=20):
    # real-looking accounts have a picture and a two-word name; fakes have neither and a digit-heavy username
    rows = [KAGGLE_HEADER]
    for i in range(n):
        rows.append(f"1,0.0{i % 3},2,0,0,40,0,{i % 2},50,800,400,0")
        rows.append(f"0,0.{50 + i},0,0,0,0,0,0,0,5,900,1")
    path.write_text("\n".join(rows) + "\n")
    return path


def test_account_features_follow_kaggle_definitions():
    fake = {"username": "priya84729301", "full_name": "", "has_pic": False, "is_private": False}
    assert account_features(fake) == [0, 0.62, 0, 0, 0, 0]
    real = {"username": "Rahul.K", "full_name": "rahul.k", "has_pic": True, "is_private": True}
    assert account_features(real) == [1, 0, 1, 0, 1, 1]
    numbered = {"username": "a", "full_name": "Team 2024", "has_pic": True, "is_private": False}
    assert account_features(numbered) == [1, 0, 2, 0.44, 0, 0]


def test_load_kaggle_keeps_the_six_list_fields(tmp_path):
    X, y = load_kaggle(write_kaggle(tmp_path / "train.csv", n=2))
    assert len(KAGGLE_LIGHT) == 6
    assert X[0] == [1, 0.0, 2, 0, 0, 0] and y[:2] == [0, 1]


def test_fake_share_scores_accounts(tmp_path):
    model = train_fake_model(*load_kaggle(write_kaggle(tmp_path / "train.csv")))
    real = {"username": "meera.sings", "full_name": "Meera Iyer", "has_pic": True, "is_private": False}
    fake = {"username": "user83920174", "full_name": "", "has_pic": False, "is_private": False}
    assert fake_share(model, [real, real, real, fake]) == 0.25
    assert type(fake_share(model, [real, fake])) is float  # numpy floats can't go into Mongo
    assert fake_share(model, []) is None


def test_build_fake_model_command(tmp_path):
    write_kaggle(tmp_path / "train.csv")
    write_kaggle(tmp_path / "test.csv", n=5)
    out = tmp_path / "models" / "fake_accounts.joblib"
    result = CliRunner().invoke(cli.app, ["build-fake-model", str(tmp_path), "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert "100% on 10 held-out Kaggle accounts" in result.output
    assert fake_share(joblib.load(out), [{"username": "x9999999", "full_name": "", "has_pic": False, "is_private": False}]) == 1.0


GENRES = ["Lifestyle", "Entertainment", "Technology", "Storytelling", "Gadgets", "Fashion", "Education", "Beauty", "News and Media", "Travel", "Creative Sketches",
          "Filmmaker", "Finance", "Food", "Vlogger", "Comedy Sketches", "Fitness", "Gaming", "Music", "Dance", "Memes"]


def test_csv_genres_map_onto_7_categories():
    assert len(CATEGORIES) == 7
    assert all(category_from_niche([g]) in CATEGORIES for g in GENRES)
    assert category_from_niche(["Gadgets", "Technology"]) == "Tech and gadgets"
    assert category_from_niche(["Storytelling", "Lifestyle"]) == "Entertainment"
    assert category_from_niche([]) is None


def make_reel(day, views, paid=False, sponsors=(), coauthors=(), caption="", pinned=False):
    return {"taken_at": f"2026-{day}T10:00:00Z", "views": views, "likes": views // 10, "comments": views // 100, "paid": paid,
            "sponsors": list(sponsors), "coauthors": list(coauthors), "caption": caption, "pinned": pinned}


def test_reel_metrics_on_the_last_30_unpinned_reels():
    days = [f"09-{30 - i:02d}" if i < 30 else f"08-{31 - (i - 30):02d}" for i in range(35)]  # newest first
    views = [5000 if i in (3, 7) else 20000 for i in range(10)] + [10000] * 10 + [6000] * 3 + [30000] * 2 + [15000] * 5 + [1_000_000] * 5
    reels = [make_reel("01-01", 5_000_000, pinned=True)]
    for i, (day, v) in enumerate(zip(days, views)):
        reels.append(make_reel(day, v, paid=i == 20, sponsors=["brand"] if i == 21 else (), coauthors=["brand2"] if i == 22 else ["friend"] if i in (23, 24) else (),
                               caption="loving this #ad" if i == 22 else "#adventure time" if i == 25 else ""))
    m = reel_metrics({"followers": 100_000, "data": {"reels": reels}})
    assert (m["n_reels"], m["n_own"]) == (30, 25)
    assert (m["views"], m["views_p25"], m["views_p75"]) == (15000, 10000, 20000)
    assert m["views_per_follower"] == 0.15
    assert (m["engagement"], m["likes_per_view"], m["comments_per_1k"]) == (0.11, 0.1, 10)
    assert (m["hits_last_10"], m["trend"]) == (8, 2.0)
    assert (m["paid_n"], m["paid_ratio"], m["collab_n"], m["collab_ratio"]) == (3, 0.4, 2, 2.0)


class FakeLLM:
    def __init__(self, reply):
        self.reply, self.prompts = reply, []

    def json(self, prompt, schema):
        self.prompts.append(prompt)
        return self.reply


def test_label_niche_sends_bio_and_12_captions_only():
    llm = FakeLLM({"category": "Food"})
    captions = [f"caption {i}" for i in range(20)]
    assert label_niche(llm, "Home chef from Pune", captions) == "Food"
    prompt = llm.prompts[0]
    assert "Home chef from Pune" in prompt and "caption 11" in prompt and "caption 12" not in prompt


def snapshot(handle, n_reels=15, followers=50_000):
    reels = [make_reel(f"09-{30 - i:02d}", 10_000 + i * 1000, caption=f"recipe {i}") for i in range(n_reels)]
    liker = {"username": "meera", "full_name": "Meera Iyer", "has_pic": True, "is_private": False}
    data = {"profile": {"bio": f"{handle} bio"}, "reels": reels, "likers": {"r0": [liker] * 4}, "followers": [liker] * 2,
            "comments": {"r0": [{"text": "Recipe please", "user": {"username": "fan"}}]}, "about": {"former_usernames": 0}}
    return {"handle": handle, "fetched_at": datetime.now(timezone.utc), "followers": followers, "data": data}


def test_build_metrics_uses_wldd_niche_first_and_gemini_otherwise(db, monkeypatch):
    db.deals.insert_many([
        {"handle": "known", "tier": "medium", "niche": ["Gadgets"], "price": 41_000, "holdout": False},
        {"handle": "unknown", "tier": "medium", "niche": [], "price": 37_000, "holdout": False},
        {"handle": "thin", "tier": "small", "niche": [], "price": 5_000, "holdout": False},
        {"handle": "missing", "tier": "small", "niche": [], "price": 4_000, "holdout": True},
    ])
    db.snapshots.insert_many([snapshot("known"), snapshot("unknown"), snapshot("thin", n_reels=8)])
    llm = FakeLLM({"category": "Food"})
    monkeypatch.setattr(cli, "get_db", lambda: db)
    monkeypatch.setattr(cli, "make_llm", lambda: llm)
    monkeypatch.setattr(cli, "load_fake_model", lambda: train_fake_model([[1, 0, 2, 0, 0, 0]] * 5 + [[0, 0.6, 0, 0, 0, 0]] * 5, [0] * 5 + [1] * 5))
    monkeypatch.setattr(cli, "minilm_embed", lambda texts: np.eye(len(texts), 8))
    result = CliRunner().invoke(cli.app, ["build-metrics"])
    assert result.exit_code == 0, result.output
    assert "Built metrics for 2 creators; skipped 2 without a snapshot of 12+ reels" in result.output
    assert db.metrics.find_one({"_id": "known"})["category"] == "Tech and gadgets"
    unknown = db.metrics.find_one({"_id": "unknown"})
    assert (unknown["category"], unknown["category_source"], unknown["n_reels"]) == ("Food", "gemini", 15)
    assert (unknown["fake_likers"], unknown["n_likers"], unknown["n_comments"]) == (0.0, 4, 1)  # audience signals feed the band norms
    assert len(llm.prompts) == 1 and "37000" not in llm.prompts[0] and "37,000" not in llm.prompts[0]
    # a rebuild reuses the stored Gemini label instead of asking again
    CliRunner().invoke(cli.app, ["build-metrics"])
    assert len(llm.prompts) == 1
