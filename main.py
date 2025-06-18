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
    raise RuntimeError("Missing RESEMBLE_VOICE_UUID_EN or RESEMBLE_VOICE_UUID_JP in env")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/converse")
async def ws_converse(ws: WebSocket, lang: str = Query("english")):
    # Supported langs: "english" or "japanese"
    await ws.accept()

    # 1) Receive mic → .webm file until end signal
    os.makedirs("audio", exist_ok=True)
    filename = f"audio/{datetime.datetime.now():%Y%m%d_%H%M%S}.webm"
    with open(filename, "wb") as f:
        while True:
            msg = await ws.receive()
            if msg.get("type") == "websocket.disconnect":
                return
            if "bytes" in msg:
                f.write(msg["bytes"])
            elif "text" in msg:
                data = json.loads(msg["text"])
                if data.get("type") == "end":
                    break

    # 2) Transcribe with Whisper
    user_text = transcribe_audio(filename)
    await ws.send_json({"type": "user_transcript", "text": user_text})

    # 3) Build prompt and get LLM reply in chosen language
    prompt = build_prompt(user_text, prompt_type=lang)
    reply = get_llm_response(prompt)
    await ws.send_json({"type": "assistant_text", "text": reply})

    # 4) Stream TTS chunks using appropriate voice
    voice_uuid = JP_VOICE_UUID if lang == "japanese" else EN_VOICE_UUID
    locale_code = "ja" if lang == "japanese" else "en"
    async for chunk in stream_tts_bytes(reply, voice_uuid, language=locale_code):
        await ws.send_bytes(chunk)

    # 5) Close connection
    await ws.close()
