import httpx
import pytest

from truerate.llm import Gemini


class Reply:
    text = '{"category": "Food"}'


def flaky(failures):
    """generate_content that drops the connection `failures` times, then answers."""
    calls = []

    def generate_content(**kwargs):
        calls.append(kwargs)
        if len(calls) <= failures:
            raise httpx.RemoteProtocolError("Server disconnected without sending a response.")
        return Reply()

    return generate_content, calls


def test_a_dropped_gemini_connection_is_retried(monkeypatch):
    from truerate import llm as llm_module

    waits = []
    monkeypatch.setattr(llm_module.time, "sleep", waits.append)
    llm = Gemini("test-key", "gemini-test")
    generate, calls = flaky(failures=2)
    monkeypatch.setattr(llm.client.models, "generate_content", generate)
    assert llm.json("niche?", {"type": "OBJECT"}) == {"category": "Food"} and len(calls) == 3
    assert waits == [5, 15]  # spaced out, so a demand spike (Gemini's 503) has time to pass


def test_gemini_gives_up_after_three_dropped_connections(monkeypatch):
    from truerate import llm as llm_module

    monkeypatch.setattr(llm_module.time, "sleep", lambda s: None)
    llm = Gemini("test-key", "gemini-test")
    generate, calls = flaky(failures=3)
    monkeypatch.setattr(llm.client.models, "generate_content", generate)
    with pytest.raises(httpx.RemoteProtocolError):
        llm.json("niche?", {"type": "OBJECT"})
    assert len(calls) == 3


def test_gemini_asks_for_low_thinking(monkeypatch):
    llm = Gemini("test-key", "gemini-test")
    generate, calls = flaky(failures=0)
    monkeypatch.setattr(llm.client.models, "generate_content", generate)
    llm.json("niche?", {"type": "OBJECT"})
    assert calls[0]["config"].thinking_config.thinking_level.name == "LOW"


def quota(delay_s: str | None):
    """A Gemini 429 as the free tier sends it: the per-minute quota is used up, retry after `delay_s`."""
    from google.genai import errors

    details = [{"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": delay_s}] if delay_s else []
    return errors.ClientError(429, {"error": {"code": 429, "message": "You exceeded your current quota", "status": "RESOURCE_EXHAUSTED", "details": details}})


def test_a_per_minute_quota_is_waited_out_then_retried(monkeypatch):
    from truerate import llm as llm_module

    waits, calls = [], []

    def generate_content(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise quota("34s")
        return Reply()

    monkeypatch.setattr(llm_module.time, "sleep", waits.append)
    llm = Gemini("test-key", "gemini-test")
    monkeypatch.setattr(llm.client.models, "generate_content", generate_content)
    assert llm.json("niche?", {"type": "OBJECT"}) == {"category": "Food"}
    assert len(calls) == 2 and waits == [35.0]  # the delay Gemini asked for, plus a second


def test_a_long_or_unstated_quota_wait_fails_at_once(monkeypatch):
    from google.genai import errors

    from truerate import llm as llm_module

    monkeypatch.setattr(llm_module.time, "sleep", lambda s: pytest.fail("must not wait"))
    for err in (quota("3600s"), quota(None)):  # a daily limit, or no retry advice: waiting won't help
        llm = Gemini("test-key", "gemini-test")
        monkeypatch.setattr(llm.client.models, "generate_content", lambda **k: (_ for _ in ()).throw(err))
        with pytest.raises(errors.ClientError):
            llm.json("niche?", {"type": "OBJECT"})
