"""
main.py
-------
FastAPI backend for Multilingual Telecom AI Bot.
Connects stt.py + translate.py + intent.py + response.py
into a single API.

Endpoints:
    POST /chat/text   — accepts text input
    POST /chat/voice  — accepts audio file
    GET  /health      — health check
    GET  /intents     — list all supported intents

Usage:
    uvicorn backend.main:app --reload
    OR
    python backend/main.py
"""

import os
import sys
import shutil
import uvicorn

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Add project root to path ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Import all modules ────────────────────────────────────────────────────────
from backend.intent    import predict
from backend.translate import to_english, to_language, detect_language, SUPPORTED_LANGUAGES
from backend.response  import get_response, speak
from backend.stt       import transcribe_file

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "Multilingual Telecom AI Bot",
    description = "Conversational AI for Indian Telecom — supports English, Hindi, Kannada, Tamil, Telugu",
    version     = "1.0.0"
)

# ── CORS — allows React frontend to call this API ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # change to your frontend URL in production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Audio config ──────────────────────────────────────────────────────────────
AUDIO_DIR       = "audio"
UPLOAD_PATH     = os.path.join(AUDIO_DIR, "upload_input.wav")
RESPONSE_AUDIO  = os.path.join(AUDIO_DIR, "response.mp3")
os.makedirs(AUDIO_DIR, exist_ok=True)


# ── Request / Response models ─────────────────────────────────────────────────
class TextRequest(BaseModel):
    text: str
    language: str = "en"    # user's selected language from frontend dropdown

class BotResponse(BaseModel):
    input_text:         str
    english_text:       str
    intent:             str
    confidence:         float
    response_text:      str
    translated_response: str
    language:           str
    language_name:      str


# ── Full pipeline function ────────────────────────────────────────────────────
def run_pipeline(text: str, language: str = "en") -> dict:
    """
    Runs the full AI pipeline:
    1. Translate input to English
    2. Classify intent
    3. Generate response
    4. Translate response back to user's language
    5. Generate TTS audio
    """
    # Step 1 — Translate input to English
    if language != "en":
        english_text = to_english(text, source_lang=language)
    else:
        english_text = text

    # Step 2 — Classify intent
    intent_result = predict(english_text)
    intent        = intent_result["intent"]
    confidence    = intent_result["confidence"]

    # Step 3 — Get English response
    english_response = get_response(intent)

    # Step 4 — Translate response to user's language
    translated_response = to_language(english_response, language)

    # Step 5 — Generate TTS audio
    speak(translated_response, lang=language)

    return {
        "input_text":          text,
        "english_text":        english_text,
        "intent":              intent,
        "confidence":          confidence,
        "response_text":       english_response,
        "translated_response": translated_response,
        "language":            language,
        "language_name":       SUPPORTED_LANGUAGES.get(language, "English"),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Multilingual Telecom AI Bot is running!",
        "docs":    "Visit /docs for API documentation"
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/intents")
def list_intents():
    return {
        "intents": [
            "recharge",
            "balance",
            "network_issue",
            "plan_info",
            "data_usage",
            "complaint",
            "port_number",
            "unknown"
        ]
    }


@app.get("/languages")
def list_languages():
    return {"languages": SUPPORTED_LANGUAGES}


@app.post("/chat/text", response_model=BotResponse)
def chat_text(request: TextRequest):
    """
    Accept text input and return bot response.

    Request body:
        {
            "text": "Mera balance kitna hai",
            "language": "hi"
        }

    Response:
        {
            "input_text": "Mera balance kitna hai",
            "english_text": "What is my balance",
            "intent": "balance",
            "confidence": 82.5,
            "response_text": "Your current balance is Rs 45...",
            "translated_response": "आपका बैलेंस 45 रुपये है...",
            "language": "hi",
            "language_name": "Hindi"
        }
    """
    result = run_pipeline(request.text, request.language)
    return result


@app.post("/chat/voice")
async def chat_voice(
    file:     UploadFile = File(...),
    language: str        = Form(default="en")
):
    """
    Accept voice file and return bot response + audio.

    Form fields:
        file:     audio file (.wav or .mp3)
        language: user's language code (default: en)

    Returns JSON response + audio file path
    """
    # Save uploaded audio
    with open(UPLOAD_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Transcribe audio to text
    stt_result = transcribe_file(UPLOAD_PATH)
    text       = stt_result["text"]

    # If language not specified, use Whisper's detected language
    if language == "auto":
        language = stt_result.get("language", "en")

    # Run full pipeline
    result = run_pipeline(text, language)
    return result


@app.get("/audio/response")
def get_audio():
    """
    Returns the latest TTS response audio file.
    Frontend calls this after /chat/text or /chat/voice
    to play the bot's voice response.
    """
    if os.path.exists(RESPONSE_AUDIO):
        return FileResponse(
            RESPONSE_AUDIO,
            media_type = "audio/mpeg",
            filename   = "response.mp3"
        )
    return JSONResponse(
        status_code = 404,
        content     = {"error": "No audio response available yet"}
    )


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host    = "0.0.0.0",
        port    = 8000,
        reload  = True
    )
