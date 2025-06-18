# tts/resemble_tts.py
import os
import json
import asyncio
import websockets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RESEMBLE_API_KEY    = os.getenv("RESEMBLE_API_KEY")
RESEMBLE_STREAM_URL = os.getenv("RESEMBLE_STREAM_ENDPOINT")

# Validate config
if not (RESEMBLE_API_KEY and RESEMBLE_STREAM_URL):
    raise RuntimeError("Missing RESEMBLE_API_KEY or RESEMBLE_STREAM_ENDPOINT in .env")

async def stream_tts_bytes(
    text: str,
    voice_uuid: str,
    language: str = "en"   # e.g., "en" or "ja"
):
    """
    Connects to Resemble WebSocket and yields MP3 chunks for the specified voice.
    """
    headers = {"Authorization": f"Token {RESEMBLE_API_KEY}"}
    async with websockets.connect(RESEMBLE_STREAM_URL, extra_headers=headers) as ws:
        # Request MP3 containers with chosen voice and locale
        request = {
            "voice_uuid":     voice_uuid,
            "data":           text,
            "binary_response": True,
            "output_format":   "mp3",    # supports mp3 or wav only
            "sample_rate":     48000,
            "precision":       "PCM_16",
            "language":        language
        }
        await ws.send(json.dumps(request))
        print(f"🔁 Streaming TTS ({language}) from voice {voice_uuid}...")

        while True:
            frame = await ws.recv()
            if isinstance(frame, (bytes, bytearray)):
                # Each frame is a complete MP3 packet
                yield frame
            else:
                meta = json.loads(frame)
                if meta.get("type") == "audio_end":
                    break
                if meta.get("type") == "error":
                    raise RuntimeError(f"TTS Error: {meta.get('message')}")
