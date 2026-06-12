import pandas as pd
import numpy as np
import pickle
import joblib

# ── Load model and feature names ──
model = joblib.load("fishing_model.pkl")
feature_names = joblib.load("feature_names.pkl")

# ── Load CSV ──
df = pd.read_csv("./dakhla_ai_features_full.csv")

# ── Select features in correct order ──
X = df[feature_names]

# ── Predict ──
df['probability'] = model.predict_proba(X)[:, 1]
df['prediction']  = (df['probability'] >= 0.24).astype(int)

# ── Save results ──
df[['Latitude', 'Longitude', 'probability', 'prediction']].to_csv(
    "predictions.csv", index=False
)

print("✅ Done! predictions.csv saved")
print(df[['Latitude', 'Longitude', 'probability', 'prediction']].head(10))
