import os
import whisper

# Global Whisper model (lazy-loaded)
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        print("🔈 Loading Whisper model...")
        _model = whisper.load_model("base")  # "base", "small", "medium", "large"
    return _model

def transcribe_audio(filepath: str) -> str:
    """
    Transcribes a given audio file using Whisper.
    Cleans up the file after transcription.
    """
    try:
        model = get_whisper_model()

        # Use fp16=False if running on CPU to avoid warning
        result = model.transcribe(filepath, fp16=False)
        text = result.get("text", "").strip()

        if not text:
            print("⚠️ Transcription returned empty text.")
            return "Sorry, I couldn't hear anything clearly."

        print(f"📝 Transcription complete: {text}")
        return text

    except Exception as e:
        print(f"❌ Whisper transcription failed: {e}")
        return "Sorry, something went wrong with transcription."

    finally:
        # Clean up the audio file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🧹 Deleted audio file: {filepath}")
        except Exception as cleanup_error:
            print(f"⚠️ Could not delete audio file: {cleanup_error}")
