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
    language: str = "en"
):
    """
    Connect to Resemble TTS WebSocket and yield audio chunks (MP3 format).
    Gracefully handles connection and stream errors.
    """
    headers = {"Authorization": f"Token {RESEMBLE_API_KEY}"}

    try:
        async with websockets.connect(RESEMBLE_STREAM_URL, extra_headers=headers) as ws:
            request = {
                "voice_uuid":     voice_uuid,
                "data":           text,
                "binary_response": True,
                "output_format":   "mp3",
                "sample_rate":     48000,
                "precision":       "PCM_16",
                "language":        language
            }

            await ws.send(json.dumps(request))
            print(f"🔁 TTS streaming started (lang={language}, voice={voice_uuid})")

            while True:
                try:
                    frame = await ws.recv()
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"🔴 Resemble WS connection closed: {e}")
                    break

                if isinstance(frame, (bytes, bytearray)):
                    yield frame
                else:
                    meta = json.loads(frame)
                    if meta.get("type") == "audio_end":
                        print("✅ TTS streaming complete")
                        break
                    elif meta.get("type") == "error":
                        error_msg = meta.get("message", "Unknown TTS error")
                        print(f"❌ Resemble TTS error: {error_msg}")
                        raise RuntimeError(f"TTS Error: {error_msg}")

    except Exception as e:
        print(f"❌ Exception in stream_tts_bytes: {e}")
        raise RuntimeError(f"TTS connection or streaming failed: {e}")
