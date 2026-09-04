"""
STEP 2: Train the AI model.

Reads data/traffic.csv (created by 1_generate_data.py, or swap in your
real CICIDS2017 CSV -- just make sure it has a "label" column).

Trains a Random Forest classifier to recognize each traffic type from
its numeric features, then saves the trained model to disk so the
streaming detector (step 3) can load it without retraining every time.

Run this file second. It creates: model.pkl
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def main():
    df = pd.read_csv("data/traffic.csv")

    # Features = everything except the label and timestamp (timestamp isn't
    # a numeric pattern the model should learn from -- it's just metadata)
    feature_cols = [c for c in df.columns if c not in ("label", "timestamp")]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Model performance on held-out test data:\n")
    print(classification_report(y_test, y_pred))

    # Save both the model and the feature column order (needed later so
    # new incoming rows are formatted exactly the way the model expects)
    joblib.dump({"model": model, "feature_cols": feature_cols}, "model.pkl")
    print("\nSaved trained model to model.pkl")

if __name__ == "__main__":
    main()