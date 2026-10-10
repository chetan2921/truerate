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
    llm = Gemini("test-key", "gemini-test")
    generate, calls = flaky(failures=2)
    monkeypatch.setattr(llm.client.models, "generate_content", generate)
    assert llm.json("niche?", {"type": "OBJECT"}) == {"category": "Food"} and len(calls) == 3


def test_gemini_gives_up_after_three_dropped_connections(monkeypatch):
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
