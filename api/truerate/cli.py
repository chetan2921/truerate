from pathlib import Path
from typing import Annotated

import joblib
import typer

from truerate.config import REPO_ROOT
from truerate.db import ensure_indexes, get_db, import_deals
from truerate.signals import load_kaggle, train_fake_model

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """TrueRate data, model and validation commands."""


@app.command("import-deals")
def import_deals_cmd(csv_path: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "creators.csv") -> None:
    db = get_db()
    ensure_indexes(db)
    counts = import_deals(db, csv_path)
    typer.echo(f"Imported {counts['deals']} deals ({counts['holdout']} held out)")


@app.command("build-fake-model")
def build_fake_model_cmd(
    kaggle_dir: Annotated[Path, typer.Argument()] = REPO_ROOT / "data" / "external" / "instagram_fake",
    out: Path = REPO_ROOT / "data" / "models" / "fake_accounts.joblib",
) -> None:
    model = train_fake_model(*load_kaggle(kaggle_dir / "train.csv"))
    X_test, y_test = load_kaggle(kaggle_dir / "test.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out)
    typer.echo(f"Fake-account model: {model.score(X_test, y_test):.0%} on {len(y_test)} held-out Kaggle accounts. Saved {out}")
