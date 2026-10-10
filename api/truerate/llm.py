import json

import httpx
from google import genai
from google.genai import errors, types

ATTEMPTS = 3


class Gemini:
    """Gemini with JSON replies. Never pass it a deal price."""

    def __init__(self, key: str, model: str):
        # Keep the client on the object: the SDK closes its connection once the client is garbage-collected.
        self.client = genai.Client(api_key=key)
        self.model = model

    def json(self, prompt: str, schema: dict, images: list[bytes] = (), audio: list[bytes] = ()) -> dict:
        # Low thinking: 9-12 s instead of 22-36 s for the labelling call, and labels agree with the default as closely as two
        # default runs agree with each other (same hidden ads bar one borderline reel; topics 85-97%; account kinds 88-100%).
        config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema,
                                             thinking_config=types.ThinkingConfig(thinking_level="low"))
        contents = ([prompt] + [types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in images]
                    + [types.Part.from_bytes(data=wav, mime_type="audio/wav") for wav in audio])
        for attempt in range(ATTEMPTS):
            try:
                return json.loads(self.client.models.generate_content(model=self.model, contents=contents, config=config).text)
            except (httpx.TransportError, errors.ServerError):
                # A dropped connection or a Gemini 5xx is usually gone on the next try; one live analysis failed on it.
                if attempt == ATTEMPTS - 1:
                    raise

    def search(self, prompt: str) -> dict:
        """A Google-grounded answer and the pages behind it: {"text", "sources": [{"title", "url"}]}."""
        config = types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])
        for attempt in range(ATTEMPTS):
            try:
                r = self.client.models.generate_content(model=self.model, contents=prompt, config=config)
                break
            except (httpx.TransportError, errors.ServerError):
                if attempt == ATTEMPTS - 1:
                    raise
        meta = r.candidates[0].grounding_metadata if r.candidates else None
        sources = {}
        for chunk in (meta.grounding_chunks or []) if meta else []:
            if chunk.web and chunk.web.uri:
                sources.setdefault(chunk.web.title or chunk.web.domain or "source", chunk.web.uri)
        return {"text": r.text or "", "sources": [{"title": t, "url": u} for t, u in sources.items()]}
