import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]
# MODELS_DIR=data/models_dev points the API at synthetic models while building screens (api/scripts/seed_dev.py).
MODELS_DIR = Path(os.environ.get("MODELS_DIR") or REPO_ROOT / "data" / "models")
if not MODELS_DIR.is_absolute():
    MODELS_DIR = REPO_ROOT / MODELS_DIR
# Every HikerAPI response, saved once and kept (truerate.instagram.Hiker).
HIKER_DIR = REPO_ROOT / "data" / "hikerapi"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")

    mongodb_uri: str = ""
    mongodb_db: str = "truerate"
    hikerapi_key: str = ""
    llm_api_key: str = ""
    llm_model: str = "gemini-3.8-flash"
    data_dir: Path = REPO_ROOT / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
