from fastapi.testclient import TestClient

from truerate.app import app
from truerate.config import Settings


def test_health():
    assert TestClient(app).get("/api/health").json() == {"ok": True}


def test_settings_read_env(monkeypatch):
    monkeypatch.setenv("MONGODB_DB", "truerate_test")
    assert Settings(_env_file=None).mongodb_db == "truerate_test"
