import joblib
from typer.testing import CliRunner

from truerate import cli
from truerate.signals import KAGGLE_LIGHT, account_features, fake_share, load_kaggle, train_fake_model

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
    assert fake_share(model, []) is None


def test_build_fake_model_command(tmp_path):
    write_kaggle(tmp_path / "train.csv")
    write_kaggle(tmp_path / "test.csv", n=5)
    out = tmp_path / "models" / "fake_accounts.joblib"
    result = CliRunner().invoke(cli.app, ["build-fake-model", str(tmp_path), "--out", str(out)])
    assert result.exit_code == 0, result.output
    assert "100% on 10 held-out Kaggle accounts" in result.output
    assert fake_share(joblib.load(out), [{"username": "x9999999", "full_name": "", "has_pic": False, "is_private": False}]) == 1.0
