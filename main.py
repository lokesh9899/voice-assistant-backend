import os
import datetime
import json

from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware

from stt.whisper_transcriber import transcribe_audio
from llm.openrouter_client import build_prompt, get_llm_response
from tts.resemble_tts import stream_tts_bytes

# Load Resemble voice UUIDs from environment
EN_VOICE_UUID = os.getenv("RESEMBLE_VOICE_UUID_EN")
JP_VOICE_UUID = os.getenv("RESEMBLE_VOICE_UUID_JP")
if not (EN_VOICE_UUID and JP_VOICE_UUID):
    raise RuntimeError("Missing RESEMBLE_VOICE_UUID_EN or RESEMBLE_VOICE_UUID_JP in environment")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "voice-assistant-backend is running"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.websocket("/ws/converse")
async def ws_converse(ws: WebSocket, lang: str = Query("english")):
    await ws.accept()
    print(f"✅ WebSocket accepted for language: {lang}")

    os.makedirs("audio", exist_ok=True)
    filename = f"audio/{datetime.datetime.now():%Y%m%d_%H%M%S}.webm"

    try:
        # Step 1: Receive audio from frontend
        with open(filename, "wb") as f:
            while True:
                msg = await ws.receive()
                if msg.get("type") == "websocket.disconnect":
                    print("🛑 Client disconnected.")
                    return
                if "bytes" in msg:
                    f.write(msg["bytes"])
                elif "text" in msg:
                    data = json.loads(msg["text"])
                    if data.get("type") == "end":
                        print("📩 Received end of audio stream.")
                        break

        # Step 2: Transcribe speech
        user_text = transcribe_audio(filename)
        print(f"🎤 User said: {user_text}")
        await ws.send_json({"type": "user_transcript", "text": user_text})

        # Step 3: Generate LLM reply
        prompt = build_prompt(user_text, prompt_type=lang)
        reply = get_llm_response(prompt)
        print(f"🤖 Assistant reply: {reply}")
        await ws.send_json({"type": "assistant_text", "text": reply})

        # Step 4: Stream TTS
        voice_uuid = JP_VOICE_UUID if lang == "japanese" else EN_VOICE_UUID
        locale_code = "ja" if lang == "japanese" else "en"

        try:
            async for chunk in stream_tts_bytes(reply, voice_uuid, language=locale_code):
                await ws.send_bytes(chunk)
        except Exception as e:
            print(f"🔴 TTS streaming error: {e}")
            await ws.send_json({"type": "error", "text": f"TTS failed: {str(e)}"})

    except Exception as e:
        print(f"❌ Unhandled server error: {e}")
        await ws.send_json({"type": "error", "text": f"Server error: {str(e)}"})
        await ws.close(code=1011)

    finally:
        print("🧹 WebSocket connection closed cleanly")
        await ws.close(code=1000)
