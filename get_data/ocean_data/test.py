import pandas as pd
import joblib

feature_names = joblib.load("feature_names.pkl")
df = pd.read_csv("./dakhla_ai_features_full.csv")

print("Feature names from model:", feature_names)
print("\nColumns in CSV:", df.columns.tolist())
print("\nData sample:")
print(df[feature_names].head(3))
print("\nData stats:")
print(df[feature_names].describe())
