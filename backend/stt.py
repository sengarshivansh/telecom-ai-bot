"""
stt.py
------
Speech-to-Text module using OpenAI Whisper.
Supports two modes:
  1. File mode   — transcribe an existing .wav / .mp3 file
  2. Mic mode    — record from microphone then transcribe

Usage (standalone test):
    python backend/stt.py --file audio/sample.wav
    python backend/stt.py --mic
    python backend/stt.py --mic --duration 8

Used by main.py via:
    from backend.stt import transcribe_file, transcribe_mic
"""

import argparse
import os
import tempfile
import wave

import whisper

# ── Config ────────────────────────────────────────────────────────────────────
WHISPER_MODEL   = "base"        # tiny | base | small | medium
DEFAULT_DURATION = 5            # seconds for mic recording
SAMPLE_RATE      = 16000        # Hz — Whisper expects 16kHz
AUDIO_DIR        = "audio"      # folder for temp audio files

# Supported Indian + English language codes (Whisper uses these)
SUPPORTED_LANGS = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "bn": "Bengali",
}

# ── Load Whisper model once ───────────────────────────────────────────────────
print(f"[stt.py] Loading Whisper '{WHISPER_MODEL}' model...")
_model = whisper.load_model(WHISPER_MODEL)
print(f"[stt.py] Whisper ready.")


# ── Core transcription function ───────────────────────────────────────────────
def transcribe_file(audio_path: str) -> dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to .wav or .mp3 file

    Returns:
        {
            "text":     "Mera balance kitna hai",
            "language": "hi",
            "language_name": "Hindi"
        }
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[stt.py] Transcribing: {audio_path}")
    result = _model.transcribe(audio_path, task="transcribe")

    detected_lang = result.get("language", "en")
    lang_name     = SUPPORTED_LANGS.get(detected_lang, detected_lang.upper())
    text          = result["text"].strip()

    return {
        "text":          text,
        "language":      detected_lang,
        "language_name": lang_name,
    }


# ── Mic recording function ────────────────────────────────────────────────────
def transcribe_mic(duration: int = DEFAULT_DURATION) -> dict:
    """
    Record from microphone for `duration` seconds, then transcribe.

    Returns same dict as transcribe_file().
    Requires: pip install sounddevice
    """
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError:
        raise ImportError(
            "sounddevice not installed. Run: pip install sounddevice"
        )

    print(f"\n[stt.py] 🎙️  Recording for {duration} seconds... Speak now!")
    print("         " + "█" * duration)

    # Record audio
    audio_data = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()  # Wait until recording is finished
    print("[stt.py] ✅ Recording complete. Transcribing...")

    # Save to temp .wav file
    os.makedirs(AUDIO_DIR, exist_ok=True)
    temp_path = os.path.join(AUDIO_DIR, "mic_input.wav")

    # Write wav file
    import scipy.io.wavfile as wav
    wav.write(temp_path, SAMPLE_RATE, (audio_data * 32767).astype("int16"))

    # Transcribe the saved file
    return transcribe_file(temp_path)


# ── Language display helper ───────────────────────────────────────────────────
def format_result(result: dict) -> str:
    """Pretty print transcription result."""
    return (
        f"\n  📝 Text     : {result['text']}"
        f"\n  🌐 Language : {result['language_name']} ({result['language']})"
    )


# ── CLI entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Telecom AI — Speech to Text")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="Path to audio file (.wav/.mp3)")
    group.add_argument("--mic",  action="store_true", help="Record from microphone")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION,
                        help=f"Mic recording duration in seconds (default: {DEFAULT_DURATION})")
    args = parser.parse_args()

    print("\n" + "=" * 55)
    print("  SPEECH TO TEXT — Multilingual Telecom AI")
    print("=" * 55)

    if args.file:
        # ── File mode ──
        result = transcribe_file(args.file)
        print(format_result(result))

    elif args.mic:
        # ── Mic mode ──
        result = transcribe_mic(duration=args.duration)
        print(format_result(result))

    # ── Pass to intent classifier ──
    print("\n  Passing to intent classifier...")
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from backend.intent import predict
        intent_result = predict(result["text"])
        print(f"  🎯 Intent     : {intent_result['intent']}")
        print(f"  📊 Confidence : {intent_result['confidence']}%")
    except Exception as e:
        print(f"  Error: {e}")

    print()
