import base64
import json
from pathlib import Path

import httpx

from truerate.phyllo import INSTAGRAM, PRODUCTS, Phyllo, summarize_verified

# Recorded from Phyllo's sandbox: its dummy creator, contact fields removed.
FIX = Path(__file__).parent / "fixtures"


def fx(name):
    return json.loads((FIX / f"phyllo_{name}.json").read_text())


def fake_phyllo(exists=False, connected=True, calls=None):
    def handler(request):
        if calls is not None:
            calls.append((request.method, request.url.path, dict(request.url.params), request.content and json.loads(request.content)))
        path = request.url.path
        if path == "/v1/users" and request.method == "POST":
            if exists:
                return httpx.Response(400, json={"error": {"code": "user_exists_with_external_id"}})
            return httpx.Response(201, json={"id": "user-1", "external_id": "asha.cooks"})
        if path == "/v1/users/external_id/asha.cooks":
            return httpx.Response(200, json={"id": "user-1", "external_id": "asha.cooks"})
        if path == "/v1/sdk-tokens":
            return httpx.Response(201, json={"sdk_token": "token-1", "expires_at": "2026-10-17T00:00:00"})
        if path == "/v1/accounts":
            data = fx("accounts")
            if not connected:
                data["data"] = []
            return httpx.Response(200, json=data)
        return httpx.Response(200, json=fx({"/v1/profiles": "profile", "/v1/audience": "audience", "/v1/social/contents": "contents"}[path]))

    return Phyllo("client-id", "client-secret", "sandbox", httpx.Client(base_url="https://api.sandbox.getphyllo.com", transport=httpx.MockTransport(handler)))


def test_summarize_verified_from_sandbox_data():
    v = summarize_verified(fx("accounts")["data"][0], fx("profile")["data"][0], fx("audience"), fx("contents")["data"])
    assert v["followers"] == 78_976 and v["posts"] == 2 and v["sponsored"] == 0
    assert v["countries"][0] == {"code": "US", "share": 0.5} and v["cities"][0] == {"name": "Austin", "share": 0.5}
    assert v["gender_age"][0] == {"gender": "MALE", "age_range": "18-24", "share": 0.4}
    assert v["median_reach"] == 8212 and v["median_views"] == 67 and v["reach_per_follower"] == round(8212 / 78_976, 4)
    assert v["india_share"] == 0.0


def test_user_is_created_once_then_found_by_handle():
    calls = []
    assert fake_phyllo(calls=calls).user_id("asha.cooks") == "user-1"
    assert calls[0][3] == {"name": "asha.cooks", "external_id": "asha.cooks"}
    assert fake_phyllo(exists=True).user_id("asha.cooks") == "user-1"


def test_sdk_token_asks_for_identity_and_engagement_with_audiences():
    calls = []
    assert fake_phyllo(calls=calls).sdk_token("user-1") == "token-1"
    assert calls[0][1] == "/v1/sdk-tokens" and calls[0][3] == {"user_id": "user-1", "products": PRODUCTS}


def test_verified_reads_the_connected_instagram_account_or_nothing():
    calls = []
    v = fake_phyllo(calls=calls).verified("user-1")
    assert v["followers"] == 78_976 and v["username"]
    assert calls[0][2] == {"user_id": "user-1", "work_platform_id": INSTAGRAM}
    assert fake_phyllo(connected=False).verified("user-1") is None


def test_client_uses_basic_auth():
    p = Phyllo("client-id", "client-secret", "staging")
    assert p.http.base_url == "https://api.staging.getphyllo.com"
    assert p.http.auth._auth_header == "Basic " + base64.b64encode(b"client-id:client-secret").decode()
