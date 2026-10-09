from pathlib import Path
from typing import Annotated

import typer

from truerate.config import REPO_ROOT
from truerate.db import ensure_indexes, get_db, import_deals

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
