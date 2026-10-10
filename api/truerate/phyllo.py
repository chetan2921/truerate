"""Phyllo: data a creator shares with consent, through Phyllo Connect. Real reach, verified followers, and audience
countries, cities, age and gender. TrueRate's public-data analysis stays the default; a creator who connects adds
verified numbers to their report.
"""

from statistics import median

import httpx

BASES = {"sandbox": "https://api.sandbox.getphyllo.com", "staging": "https://api.staging.getphyllo.com", "production": "https://api.getphyllo.com"}
INSTAGRAM = "9bb8913b-ddd9-430b-a66a-d74d846e6c66"  # Phyllo's work-platform id for Instagram
PRODUCTS = ["IDENTITY", "IDENTITY.AUDIENCE", "ENGAGEMENT", "ENGAGEMENT.AUDIENCE"]


class PhylloError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def _shares(items: list[dict], key: str, top: int = 5) -> list[dict]:
    """Phyllo gives percentages (50.0); TrueRate uses shares (0.5)."""
    return [{key: x[key], "share": round(x["value"] / 100, 4)} for x in sorted(items or [], key=lambda x: -x["value"])[:top]]


def summarize_verified(account: dict, profile: dict, audience: dict, contents: list[dict]) -> dict:
    followers = (profile.get("reputation") or {}).get("follower_count")
    engagement = [c.get("engagement") or {} for c in contents]
    reach = [(e.get("reach_organic_count") or 0) + (e.get("reach_paid_count") or 0) for e in engagement if e.get("reach_organic_count") is not None]
    views = [e["view_count"] for e in engagement if e.get("view_count") is not None]
    countries = _shares(audience.get("countries"), "code")
    return {
        "username": account.get("platform_username") or account.get("username") or "",
        "followers": followers,
        "countries": countries,
        "india_share": next((c["share"] for c in _shares(audience.get("countries"), "code", top=1000) if c["code"] == "IN"), 0.0),
        "cities": _shares(audience.get("cities"), "name"),
        "gender_age": [{"gender": g["gender"], "age_range": g["age_range"], "share": round(g["value"] / 100, 4)}
                       for g in sorted(audience.get("gender_age_distribution") or [], key=lambda g: -g["value"])],
        "posts": len(contents),
        "median_reach": round(median(reach)) if reach else None,
        "median_views": round(median(views)) if views else None,
        "reach_per_follower": round(median(reach) / followers, 4) if reach and followers else None,
        "sponsored": sum(1 for c in contents if c.get("sponsored")),
    }


class Phyllo:
    def __init__(self, client_id: str, client_secret: str, env: str = "sandbox", http: httpx.Client | None = None):
        self.env = env
        self.http = http or httpx.Client(base_url=BASES[env], auth=(client_id, client_secret), timeout=60)

    def _call(self, method: str, path: str, **kwargs) -> dict:
        r = self.http.request(method, path, **kwargs)
        if r.status_code >= 400:
            raise PhylloError(r.status_code, f"Phyllo {r.status_code} on {path}: {r.text[:200]}")
        return r.json()

    def user_id(self, handle: str) -> str:
        """The Phyllo user for this creator, created the first time and found by handle after that."""
        try:
            return self._call("POST", "/v1/users", json={"name": handle, "external_id": handle})["id"]
        except PhylloError as e:
            if e.status != 400:
                raise
            return self._call("GET", f"/v1/users/external_id/{handle}")["id"]

    def sdk_token(self, user_id: str) -> str:
        """For the creator's browser to open Phyllo Connect. Valid for a week."""
        return self._call("POST", "/v1/sdk-tokens", json={"user_id": user_id, "products": PRODUCTS})["sdk_token"]

    def verified(self, user_id: str) -> dict | None:
        """The creator's connected Instagram account, summarised. None until they connect one."""
        accounts = self._call("GET", "/v1/accounts", params={"user_id": user_id, "work_platform_id": INSTAGRAM})["data"]
        account = next((a for a in accounts if a.get("status") == "CONNECTED"), None)
        if not account:
            return None
        profile = self._call("GET", "/v1/profiles", params={"account_id": account["id"]})["data"][0]
        audience = self._call("GET", "/v1/audience", params={"account_id": account["id"]})
        contents = self._call("GET", "/v1/social/contents", params={"account_id": account["id"], "limit": 30})["data"]
        return summarize_verified(account, profile, audience, contents)
