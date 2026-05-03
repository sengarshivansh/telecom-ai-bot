"""
response.py
-----------
Generates telecom-specific responses for each intent.
Also handles Text-to-Speech (TTS) output using gTTS.

Usage (standalone test):
    python backend/response.py

Used by main.py via:
    from backend.response import get_response, speak
"""

import os
import random
from gtts import gTTS

# ── Config ────────────────────────────────────────────────────────────────────
AUDIO_DIR        = "audio"
TTS_OUTPUT_FILE  = os.path.join(AUDIO_DIR, "response.mp3")

# ── Telecom Response Templates ────────────────────────────────────────────────
# Multiple responses per intent so it doesn't feel repetitive
RESPONSES = {
    "recharge": [
        "Here are our popular recharge plans: ₹199 for 28 days with 1.5GB/day, ₹299 for 56 days with 2GB/day, and ₹499 for 84 days with 2GB/day. All plans include unlimited calls. Which plan would you like?",
        "We have great recharge options! ₹149 for 24 days, ₹199 for 28 days, ₹299 for 56 days. Shall I proceed with a recharge?",
        "Popular plans available: ₹99 for 14 days, ₹199 for 28 days, ₹399 for 56 days. All include unlimited calls and data. Which one suits you?",
    ],

    "balance": [
        "Your current account balance is ₹45.20. Your plan is valid for 5 more days. Would you like to recharge?",
        "Account balance: ₹82.50. Your current plan expires in 12 days. Is there anything else I can help you with?",
        "Your balance is ₹120.00 and your data plan has 3 days remaining. Would you like to check your data usage?",
    ],

    "network_issue": [
        "I'm sorry to hear about the network issue. I've logged a complaint with ticket ID TK-2045. Our team will resolve this within 24 hours. You'll receive an SMS update.",
        "Network issues in your area have been reported. Our engineers are working on it. Estimated resolution: 2-4 hours. Ticket ID: TK-3182.",
        "I understand the inconvenience. A complaint has been registered — Ticket ID: TK-4051. You can track it on our app. Expected resolution: within 4 hours.",
    ],

    "plan_info": [
        "Our best plans: ₹199 (28 days, 1.5GB/day), ₹299 (56 days, 2GB/day), ₹499 (84 days, 2GB/day). All include unlimited calls and 100 SMS/day. Which plan interests you?",
        "Top plans this month: ₹149 Basic — 1GB/day for 24 days. ₹299 Popular — 2GB/day for 56 days. ₹599 Premium — 3GB/day for 84 days. All with unlimited calls!",
        "For heavy users: ₹499 gives 2GB/day for 84 days. For light users: ₹199 gives 1.5GB/day for 28 days. Need help choosing?",
    ],

    "data_usage": [
        "You have used 18.5GB out of 28GB this month. 9.5GB remaining. Your plan expires in 8 days. Want to add an extra data pack?",
        "Data usage today: 1.2GB used, 0.8GB remaining for today. Total this month: 22GB used out of 30GB. Plan valid for 6 more days.",
        "Your data balance: 4.5GB remaining. Daily limit: 2GB. You've used 1.3GB today. Plan expires in 3 days — would you like to recharge?",
    ],

    "complaint": [
        "Your complaint has been registered successfully. Ticket ID: TK-5092. Our support team will contact you within 24 hours. You can track your complaint on our app or website.",
        "I've logged your complaint. Ticket ID: TK-6033. Expected resolution time: 4-8 hours. You'll receive SMS updates. Is there anything else I can help with?",
        "Complaint registered! Ticket ID: TK-7018. Our team will call you back within 2 hours. For urgent issues, you can also visit your nearest store.",
    ],

    "port_number": [
        "To port your number, SMS 'PORT <your 10-digit number>' to 1900. You'll receive a porting code valid for 4 days. The process takes 3-7 working days. Shall I guide you through it?",
        "Number porting is easy! Step 1: SMS PORT to 1900. Step 2: Receive your UPC code. Step 3: Submit it to your new operator. The switch happens within 7 days.",
        "For MNP (Mobile Number Portability): Send 'PORT XXXXXXXXXX' to 1900. You'll get a unique porting code. Take it to any Airtel/Jio/BSNL store to complete the switch.",
    ],

    "unknown": [
        "I'm sorry, I didn't quite understand that. I can help you with recharge, balance check, data usage, network issues, plan information, complaints, or number porting. What would you like help with?",
        "I couldn't understand your request. Could you please rephrase? I can assist with: recharge, balance, data usage, network problems, plans, complaints, or porting.",
        "I'm not sure what you're asking. I'm here to help with telecom services — recharge, balance, plans, data, network issues, or complaints. How can I assist you?",
    ],
}

# ── gTTS language codes ───────────────────────────────────────────────────────
# gTTS uses slightly different codes than our app
GTTS_LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "kn": "kn",
    "ta": "ta",
    "te": "te",
    "bn": "bn",
}


# ── Get response text ─────────────────────────────────────────────────────────
def get_response(intent: str) -> str:
    """
    Returns a response string for the given intent.
    Randomly picks from multiple templates to avoid repetition.

    Args:
        intent: One of the 8 intent labels

    Returns:
        Response string in English
    """
    responses = RESPONSES.get(intent, RESPONSES["unknown"])
    return random.choice(responses)


# ── Text to Speech ────────────────────────────────────────────────────────────
def speak(text: str, lang: str = "en") -> str:
    """
    Convert text to speech and save as MP3.

    Args:
        text: Text to convert (in the target language)
        lang: Language code e.g. 'hi', 'kn', 'ta', 'te', 'en'

    Returns:
        Path to the saved MP3 file
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)

    gtts_lang = GTTS_LANG_MAP.get(lang, "en")

    try:
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(TTS_OUTPUT_FILE)
        print(f"[response.py] Audio saved: {TTS_OUTPUT_FILE}")
        return TTS_OUTPUT_FILE
    except Exception as e:
        print(f"[response.py] TTS error: {e}")
        return None


# ── Full response pipeline ────────────────────────────────────────────────────
def generate_full_response(intent: str, target_lang: str = "en") -> dict:
    """
    Full response pipeline:
      1. Get English response for intent
      2. Translate to user's language
      3. Generate TTS audio

    Args:
        intent:      Predicted intent label
        target_lang: User's language code

    Returns:
        {
            "english_response":   "Your balance is Rs 45...",
            "translated_response": "आपका बैलेंस 45 रुपये है...",
            "audio_path":          "audio/response.mp3",
            "language":            "hi"
        }
    """
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.translate import to_language

    # Step 1: Get English response
    english_response = get_response(intent)

    # Step 2: Translate to user's language
    translated = to_language(english_response, target_lang)

    # Step 3: Generate TTS
    audio_path = speak(translated, lang=target_lang)

    return {
        "english_response":    english_response,
        "translated_response": translated,
        "audio_path":          audio_path,
        "language":            target_lang,
    }


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        ("recharge",       "en"),
        ("balance",        "hi"),
        ("network_issue",  "kn"),
        ("plan_info",      "ta"),
        ("data_usage",     "te"),
        ("complaint",      "hi"),
        ("port_number",    "en"),
        ("unknown",        "hi"),
    ]

    print("\n" + "=" * 60)
    print("  RESPONSE ENGINE TEST — Multilingual Telecom AI")
    print("=" * 60)

    for intent, lang in test_cases:
        print(f"\n  Intent   : {intent}")
        print(f"  Language : {lang}")

        result = generate_full_response(intent, target_lang=lang)

        print(f"  English  : {result['english_response'][:80]}...")
        print(f"  Output   : {result['translated_response'][:80]}...")
        if result["audio_path"]:
            print(f"  Audio    : {result['audio_path']} ✅")
        else:
            print(f"  Audio    : Failed ⚠️")

    print()
    print("=" * 60)
    print("  All responses generated successfully!")
    print("=" * 60)
    print()
