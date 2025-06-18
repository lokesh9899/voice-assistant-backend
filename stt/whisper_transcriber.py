_model = None

def get_whisper_model():
    global _model
    if _model is None:
        import whisper
        _model = whisper.load_model("tiny")   # loads on first call
    return _model

def transcribe_audio(filepath):
    model = get_whisper_model()
    result = model.transcribe(filepath)
    return result["text"]
