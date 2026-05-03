"""
evaluate_model.py
-----------------
Evaluates the trained intent model on test.csv.
Run from project root:
    python backend/evaluate_model.py
"""

import json
import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# ── Paths ────────────────────────────────────────────────────────────────────
MODEL_PATH     = "models/intent_model"
TEST_CSV       = "dataset/test.csv"
LABEL_MAP_FILE = f"{MODEL_PATH}/label_map.json"

# ── Load label map ────────────────────────────────────────────────────────────
with open(LABEL_MAP_FILE, "r") as f:
    label_map = json.load(f)                    # {"0": "balance", "1": "complaint", ...}
label_map = {int(k): v for k, v in label_map.items()}
num_labels = len(label_map)
# Reverse map: "balance" -> 0
label_to_id = {v: k for k, v in label_map.items()}

print(f"Labels loaded: {list(label_map.values())}\n")

# ── Load model + tokenizer ────────────────────────────────────────────────────
device    = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model     = model.to(device)
model.eval()

print(f"Model loaded from: {MODEL_PATH}")
print(f"Running on: {device}\n")

# ── Load test data ────────────────────────────────────────────────────────────
test_df = pd.read_csv(TEST_CSV)
print(f"Test samples: {len(test_df)}\n")

# ── Predict ───────────────────────────────────────────────────────────────────
def predict_batch(texts, batch_size=32):
    all_preds = []
    all_confs = []
    for i in range(0, len(texts), batch_size):
        batch = list(texts[i : i + batch_size])
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=64,
        ).to(device)
        with torch.no_grad():
            logits = model(**inputs).logits
        preds = torch.argmax(logits, dim=1).cpu().numpy()
        confs = torch.softmax(logits, dim=1).max(dim=1).values.cpu().numpy()
        all_preds.extend(preds)
        all_confs.extend(confs)
    return np.array(all_preds), np.array(all_confs)


preds, confs = predict_batch(test_df["text"])
true_labels  = test_df["label"].map(label_to_id).values

# ── Overall metrics ───────────────────────────────────────────────────────────
acc = accuracy_score(true_labels, preds)
f1  = f1_score(true_labels, preds, average="weighted")

print("=" * 55)
print("  OVERALL RESULTS")
print("=" * 55)
print(f"  Accuracy (overall)  : {acc * 100:.2f}%")
print(f"  Weighted F1 Score   : {f1:.4f}")
print(f"  Avg Confidence      : {confs.mean() * 100:.1f}%")
print("=" * 55)

# ── Per-intent breakdown ──────────────────────────────────────────────────────
target_names = [label_map[i] for i in range(num_labels)]

print("\nPER-INTENT BREAKDOWN:\n")
print(classification_report(true_labels, preds, target_names=target_names, digits=3))

# ── Confusion matrix ──────────────────────────────────────────────────────────
cm = confusion_matrix(true_labels, preds)
print("\nCONFUSION MATRIX:")
print(f"{'':>15}", end="")
for name in target_names:
    print(f"{name[:8]:>10}", end="")
print()
for i, row in enumerate(cm):
    print(f"{target_names[i]:>15}", end="")
    for val in row:
        print(f"{val:>10}", end="")
    print()

# ── Low confidence predictions ────────────────────────────────────────────────
LOW_CONF_THRESHOLD = 0.70
low_conf_mask = confs < LOW_CONF_THRESHOLD
low_conf_count = low_conf_mask.sum()

print(f"\nLOW CONFIDENCE PREDICTIONS (< {LOW_CONF_THRESHOLD * 100:.0f}%):")
print(f"  {low_conf_count} out of {len(preds)} predictions")

if low_conf_count > 0:
    print("\n  Samples with low confidence:")
    low_conf_df = test_df[low_conf_mask].copy()
    low_conf_df["predicted"] = [label_map[p] for p in preds[low_conf_mask]]
    low_conf_df["confidence"] = confs[low_conf_mask]
    for _, row in low_conf_df.iterrows():
        print(f"    Text      : {row['text']}")
        print(f"    True      : {row['label']}")
        print(f"    Predicted : {row['predicted']}")
        print(f"    Confidence: {row['confidence'] * 100:.1f}%")
        print()

# ── Quick live test ───────────────────────────────────────────────────────────
print("=" * 55)
print("  QUICK LIVE TEST (sample sentences)")
print("=" * 55)

test_sentences = [
    ("Recharge my number",            "recharge"),
    ("Mera balance kitna hai",         "balance"),
    ("Internet slow aagide",           "network_issue"),
    ("199 ka pack lagao",              "recharge"),
    ("Naa number port cheyyali",       "port_number"),
    ("Data khatam ho gaya bro",        "data_usage"),
    ("Complaint karna hai",            "complaint"),
    ("Plan tori",                      "plan_info"),
    ("Who are you",                    "unknown"),
    ("Signal illa",                    "network_issue"),
    ("Nanna balance eshtu ide",        "balance"),
    ("Airtel ku port pannanum",        "port_number"),
]

correct = 0
for text, expected in test_sentences:
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, max_length=64, padding=True).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
    pred_id    = torch.argmax(logits, dim=1).item()
    confidence = torch.softmax(logits, dim=1).max().item()
    predicted  = label_map[pred_id]
    match      = "✅" if predicted == expected else "❌"
    if predicted == expected:
        correct += 1
    print(f"  {match} '{text}'")
    print(f"     Expected : {expected}")
    print(f"     Got      : {predicted}  ({confidence * 100:.1f}%)")
    print()

print(f"Live test accuracy: {correct}/{len(test_sentences)} = {correct/len(test_sentences)*100:.1f}%")
