import json

from google import genai
from google.genai import types


class Gemini:
    """Gemini with JSON replies. Never pass it a deal price."""

    def __init__(self, key: str, model: str):
        # Keep the client on the object: the SDK closes its connection once the client is garbage-collected.
        self.client = genai.Client(api_key=key)
        self.model = model

    def json(self, prompt: str, schema: dict, images: list[bytes] = (), audio: list[bytes] = ()) -> dict:
        config = types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema)
        contents = ([prompt] + [types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in images]
                    + [types.Part.from_bytes(data=wav, mime_type="audio/wav") for wav in audio])
        return json.loads(self.client.models.generate_content(model=self.model, contents=contents, config=config).text)
