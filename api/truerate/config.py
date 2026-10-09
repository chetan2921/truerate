from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


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
