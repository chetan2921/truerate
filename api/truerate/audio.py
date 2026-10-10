"""Each reel's audio, for Gemini to listen for spoken ads ("use my code", a brand named out loud).

Instagram's audio-only track is xHE-AAC (USAC), which neither ffmpeg 7.1 nor Gemini decodes, so the audio comes out
of the reel's normal MP4 (plain AAC) and goes to Gemini as a short 16 kHz mono WAV.
"""

import io
import wave
from concurrent.futures import ThreadPoolExecutor

import av
import httpx
import numpy as np

RATE = 16_000
MAX_SECONDS = 90


def audio_from_video(data: bytes) -> bytes:
    """The first 90 s of a video's audio as a 16 kHz mono WAV."""
    chunks, total = [], 0
    with av.open(io.BytesIO(data)) as container:
        resampler = av.AudioResampler(format="s16", layout="mono", rate=RATE)
        for frame in container.decode(container.streams.audio[0]):
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray().reshape(-1))
                total += chunks[-1].size
            if total >= RATE * MAX_SECONDS:
                break
        for out in resampler.resample(None):
            chunks.append(out.to_ndarray().reshape(-1))
    pcm = np.concatenate(chunks)[: RATE * MAX_SECONDS].astype(np.int16) if chunks else np.zeros(0, np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def fetch_audio(reels: list[dict]) -> dict[str, bytes]:
    """WAV audio by reel code, downloaded in parallel. A reel that fails to download or decode is skipped."""

    def one(reel):
        try:
            resp = httpx.get(reel["video_url"], timeout=60, follow_redirects=True)
            resp.raise_for_status()
            return reel["code"], audio_from_video(resp.content)
        except Exception:  # an expired link or an odd file loses one reel, not the analysis
            return reel["code"], None

    with ThreadPoolExecutor(max_workers=4) as pool:
        return {code: wav for code, wav in pool.map(one, [r for r in reels if r.get("video_url")]) if wav}
