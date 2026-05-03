"""
intent.py
---------
Loads the trained intent model and exposes a single predict() function.
Used by main.py (FastAPI) to classify incoming user messages.

Usage (standalone test):
    python backend/intent.py
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH     = "models/intent_model"
LABEL_MAP_FILE = f"{MODEL_PATH}/label_map.json"
MAX_LEN        = 64

# ── Load once at import time (not on every request) ───────────────────────────
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

with open(LABEL_MAP_FILE, "r") as f:
    label_map = json.load(f)
label_map = {int(k): v for k, v in label_map.items()}

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model     = model.to(device)
model.eval()

print(f"[intent.py] Model loaded on {device}")
print(f"[intent.py] Intents: {list(label_map.values())}")


# ── Main predict function ─────────────────────────────────────────────────────
def predict(text: str) -> dict:
    """
    Predict the intent of a given text string.

    Returns:
        {
            "intent":     "recharge",
            "confidence": 94.3,          # percentage 0-100
            "all_scores": {              # scores for every intent
                "recharge":      94.3,
                "balance":        2.1,
                ...
            }
        }
    """
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_LEN,
    ).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits

    probs      = torch.softmax(logits, dim=1)[0].cpu().numpy()
    pred_id    = int(probs.argmax())
    confidence = float(probs[pred_id]) * 100

    all_scores = {
        label_map[i]: round(float(p) * 100, 2)
        for i, p in enumerate(probs)
    }

    return {
        "intent":     label_map[pred_id],
        "confidence": round(confidence, 1),
        "all_scores": all_scores,
    }


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_inputs = [
        "Recharge my number",
        "Mera balance kitna hai",
        "Internet slow aagide",
        "Nanna SIM ge balance haaki",
        "Airtel ku port pannanum",
        "Data khatam bro",
        "Complaint karna hai",
        "28 din ka plan kya hai",
        "Who are you",
        "Signal illa",
        "Bhai net chal nahi raha",
        "Mujhe recharge chahiye",
    ]

    print("\n" + "=" * 55)
    print("  INTENT PREDICTION TEST")
    print("=" * 55 + "\n")

    for text in test_inputs:
        result = predict(text)
        print(f"  Text      : {text}")
        print(f"  Intent    : {result['intent']}")
        print(f"  Confidence: {result['confidence']}%")
        print()
