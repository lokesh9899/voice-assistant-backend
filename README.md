# Stream-Voice-AI Backend

**Description**
A FastAPI backend that provides:
- Speech-to-Text (STT) with Whisper and VAD
- LLM inference via OpenRouter (Google Gemma 12B/27B)
- Text-to-Speech (TTS) WebSocket streaming with ResembleAI
- SSML tags for real time experience

## Prerequisites
- Python 3.10
- pipenv or venv
- FFmpeg (for audio processing)

## Installation
1. Navigate to the backend directory:
   ```bash
   cd streaming-voice/backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .\.venv\Scripts\activate    # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables
Create a `.env` file in the `backend` directory with the following keys:
```env
OPENROUTER_API_KEY=sk-...
RESEMBLE_API_KEY=...
ENG_UUID=...
JAP_UUID=...
```

## Running Locally
Start the FastAPI server with Uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints
- `POST /transcribe` — Upload audio file for transcription
- `WebSocket /ws/audio` — Bi-directional streaming for audio, transcription, and TTS

## Docker
Build and run with Docker:
```bash
docker build -t stream-voice-backend .
docker run -p 8000:8000 --env-file .env stream-voice-backend
```

## Project Structure
```
backend/
├── main.py             # FastAPI app and routes
├── stt/                # Whisper/WhisperX & VAD modules
├── llm/                # LLM request handlers (OpenRouter)
├── tts/                # FishAudio & ResembleAI streaming modules
├── requirements.txt    # Python dependencies
├── .env                # Environment variables
└── Dockerfile          # Docker config
```

## Testing
Add your tests in a `tests/` directory and run:
```bash
pytest
```

## Deployment
Deployed to Railway

---
