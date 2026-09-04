"""
STEP 3: Simulate a live one-way traffic stream and detect threats.

This mimics the "unidirectional ingest" from your problem statement:
we read traffic rows one at a time (as if they were arriving live off
a data diode), score each one with the trained model, and write out a
structured alert record whenever something suspicious is found.

Run this file third (after training). It creates: alerts.jsonl
(one JSON alert per line, appended as they're generated -- this file
is what the dashboard in step 4 reads and displays live.)
"""

import json
import time
import joblib
import pandas as pd

ALERTS_FILE = "alerts.jsonl"
SLEEP_BETWEEN_ROWS = 0.05  # seconds; simulates packets/flows arriving over time

def load_model():
    bundle = joblib.load("model.pkl")
    return bundle["model"], bundle["feature_cols"]

def build_evidence(row, feature_cols):
    """
    Pick the most unusual-looking fields to show as 'why this was flagged'.
    Simple approach for a prototype: just surface the raw feature values,
    since a security analyst reading the alert needs to see the numbers.
    """
    return {col: round(float(row[col]), 2) for col in feature_cols}

def main():
    model, feature_cols = load_model()
    df = pd.read_csv("data/traffic.csv")

    # Clear old alerts file so each run starts fresh
    open(ALERTS_FILE, "w").close()

    print(f"Streaming {len(df)} flows... press Ctrl+C to stop early.\n")

    for i, row in df.iterrows():
        features = row[feature_cols].to_frame().T  # single-row dataframe, correct shape for the model
        pred = model.predict(features)[0]
        confidence = float(model.predict_proba(features).max())

        if pred != "BENIGN":
            alert = {
                "timestamp": str(row["timestamp"]),
                "flow_id": int(i),
                "threat_class": pred,
                "confidence": round(confidence, 3),
                "evidence": build_evidence(row, feature_cols),
            }
            with open(ALERTS_FILE, "a") as f:
                f.write(json.dumps(alert) + "\n")
            print(f"[ALERT] flow={i} type={pred} confidence={confidence:.2f}")

        time.sleep(SLEEP_BETWEEN_ROWS)

    print("\nDone. All alerts saved to alerts.jsonl")

if __name__ == "__main__":
    main()