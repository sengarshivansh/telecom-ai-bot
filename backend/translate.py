"""
translate.py
------------
Handles language detection and translation.
  - Detects language of incoming text
  - Translates any language → English (for intent classification)
  - Translates English response → user's language (for output)

Usage (standalone test):
    python backend/translate.py

Used by main.py via:
    from backend.translate import detect_language, to_english, to_language
"""

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Makes langdetect results consistent (not random)
DetectorFactory.seed = 42

# ── Supported languages ───────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
}

print("[translate.py] Translate module ready.")


# ── Language Detection ────────────────────────────────────────────────────────
def detect_language(text: str) -> dict:
    """
    Detect the language of input text using langdetect.

    Returns:
        {
            "code": "hi",
            "name": "Hindi"
        }
    """
    try:
        code = detect(text)
        code = code.split("-")[0]  # normalize variants like zh-cn

        if code not in SUPPORTED_LANGUAGES:
            code = "en"

        return {
            "code": code,
            "name": SUPPORTED_LANGUAGES.get(code, "English")
        }

    except Exception as e:
        print(f"[translate.py] Detection error: {e}")
        return {"code": "en", "name": "English"}


# ── Translate to English ──────────────────────────────────────────────────────
def to_english(text: str, source_lang: str = "auto") -> str:
    """
    Translate any text to English.
    """
    if source_lang == "en":
        return text

    try:
        translated = GoogleTranslator(
            source=source_lang if source_lang != "auto" else "auto",
            target="en"
        ).translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"[translate.py] to_english error: {e}")
        return text


# ── Translate English → target language ──────────────────────────────────────
def to_language(text: str, target_lang: str) -> str:
    """
    Translate English text to the target language.
    """
    if target_lang == "en":
        return text

    if target_lang not in SUPPORTED_LANGUAGES:
        print(f"[translate.py] Unsupported: {target_lang}, returning English")
        return text

    try:
        translated = GoogleTranslator(
            source="en",
            target=target_lang
        ).translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"[translate.py] to_language error: {e}")
        return text


# ── Full pipeline helper ──────────────────────────────────────────────────────
def process_input(text: str, language_code: str = None) -> dict:
    """
    Full input pipeline:
      1. Use provided language OR detect it
      2. Translate to English
    """
    if language_code and language_code in SUPPORTED_LANGUAGES:
        # User selected language from frontend — use it directly
        lang_info = {
            "code": language_code,
            "name": SUPPORTED_LANGUAGES[language_code]
        }
    else:
        # Fallback to auto-detection
        lang_info = detect_language(text)

    english_text = to_english(text, source_lang=lang_info["code"])

    return {
        "original_text": text,
        "english_text":  english_text,
        "language_code": lang_info["code"],
        "language_name": lang_info["name"],
    }


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        ("Recharge my number",       "en"),
        ("Mera balance kitna hai",   "hi"),
        ("Internet slow aagide",     "kn"),
        ("En balance enna",          "ta"),
        ("Naa data enta undi",       "te"),
        ("Data khatam bro",          "hi"),
        ("Complaint karna hai",      "hi"),
        ("Network illai",            "ta"),
    ]

    print("\n" + "=" * 60)
    print("  LANGUAGE DETECTION + TRANSLATION TEST")
    print("=" * 60)

    for text, expected in test_cases:
        result = process_input(text)
        match  = "✅" if result["language_code"] == expected else "⚠️ "
        print(f"\n  Input    : {result['original_text']}")
        print(f"  Detected : {result['language_name']} ({result['language_code']}) {match}")
        print(f"  English  : {result['english_text']}")

    print()
    print("=" * 60)
    print("  RESPONSE TRANSLATION TEST")
    print("=" * 60)

    response = "Your current balance is Rs 45. Validity: 5 days remaining."
    print(f"\n  English : {response}\n")

    for code, name in SUPPORTED_LANGUAGES.items():
        if code == "en":
            continue
        translated = to_language(response, code)
        print(f"  {name:<10}: {translated}")

    print()