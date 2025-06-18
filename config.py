from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RESEMBLE_API_KEY = os.getenv("RESEMBLE_API_KEY")
RESEMBLE_EN_VOICE_ID = os.getenv("RESEMBLE_EN_VOICE_ID")
RESEMBLE_JP_VOICE_ID = os.getenv("RESEMBLE_JP_VOICE_ID")
RESEMBLE_STREAM_ENDPOINT = os.getenv("RESEMBLE_STREAM_ENDPOINT")
