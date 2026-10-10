import io
import wave

import av
import numpy as np
from test_signals import FakeLLM, make_reel

from truerate.audio import MAX_SECONDS, RATE, audio_from_video
from truerate.signals import label_spoken, spoken_candidates


def make_mp4(seconds: float, rate: int = 44_100) -> bytes:
    """A small MP4 holding only an AAC tone, built here so no real reel goes into the repo."""
    buf = io.BytesIO()
    with av.open(buf, "w", format="mp4") as out:
        stream = out.add_stream("aac", rate=rate)
        stream.layout = "mono"
        t = np.arange(int(seconds * rate)) / rate
        tone = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        for i in range(0, len(tone), 1024):
            frame = av.AudioFrame.from_ndarray(tone[i : i + 1024].reshape(1, -1), format="fltp", layout="mono")
            frame.sample_rate = rate
            for packet in stream.encode(frame):
                out.mux(packet)
        for packet in stream.encode(None):
            out.mux(packet)
    return buf.getvalue()


def wav_info(data: bytes) -> tuple[int, int, float]:
    with wave.open(io.BytesIO(data)) as w:
        return w.getframerate(), w.getnchannels(), w.getnframes() / w.getframerate()


def test_audio_from_video_gives_16khz_mono_wav():
    rate, channels, seconds = wav_info(audio_from_video(make_mp4(3)))
    assert (rate, channels) == (RATE, 1) and 2.8 <= seconds <= 3.2


def test_audio_from_video_keeps_at_most_90_seconds():
    assert wav_info(audio_from_video(make_mp4(MAX_SECONDS + 15)))[2] <= MAX_SECONDS


def test_spoken_candidates_are_the_newest_reels_the_rules_dont_already_call_ads():
    reels = [make_reel(f"09-{30 - i:02d}", 1000, code=f"R{i}", paid=i == 1) for i in range(8)]
    assert [r["code"] for r in spoken_candidates(reels)] == ["R0", "R2", "R3", "R4"]


def test_label_spoken_keeps_only_spoken_ads_with_brand_and_quote():
    llm = FakeLLM({"reels": [{"code": "R0", "ad": True, "brand": "zomato", "quote": "use my code ASHA for 20% off"},
                             {"code": "R2", "ad": False, "brand": "", "quote": ""}]})
    spoken = label_spoken(llm, {"R0": b"wav0", "R2": b"wav2"})
    assert spoken == {"R0": {"brand": "zomato", "quote": "use my code ASHA for 20% off"}}
    assert llm.audio[0] == [b"wav0", b"wav2"] and "R0, R2" in llm.prompts[0]
    assert label_spoken(llm, {}) == {}
