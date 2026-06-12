"""
daily_pipeline.py
-----------------
1. Run run_pipeline.py  → fetch tomorrow's ocean data
2. Load model           → predict fishing zones
3. Save to Supabase     → zone_predictions table
"""

import subprocess
import sys
import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from supabase import create_client

# ============================================================
# ── CONFIG ───────────────────────────────────────────────────
# ============================================================

# ✅ Paths are now relative — works on any machine / GitHub Actions
BASE = os.path.dirname(os.path.abspath(__file__))

RUN_PIPELINE_PATH  = os.path.join(BASE, "run.py")
MODEL_PATH         = os.path.join(BASE, "model-ai", "fishing_model.pkl")
FEATURE_NAMES_PATH = os.path.join(BASE, "model-ai", "feature_names.pkl")
CSV_PATH           = os.path.join(BASE, "get_data", "ocean_data", "dakhla_ai_features_full.csv")

# ✅ Secrets come from environment variables (GitHub Actions Secrets)
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

THRESHOLD = 0.23

# ============================================================
# ── Terminal colors ──────────────────────────────────────────
# ============================================================

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

TARGET_DATE = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

# ============================================================
# STEP 1 — Run pipeline (fetch ocean data)
# ============================================================

print(f"\n{BOLD}{'='*55}{RESET}")
print(f"  Daily Fishing Pipeline — {TARGET_DATE}")
print(f"{BOLD}{'='*55}{RESET}")

print(f"\n{BOLD}▶ STEP 1 — Fetching ocean data...{RESET}")

result = subprocess.run(
    [sys.executable, RUN_PIPELINE_PATH, "--date", TARGET_DATE],
    cwd=os.path.dirname(RUN_PIPELINE_PATH)
)

if result.returncode != 0:
    print(f"{RED}✗ Pipeline failed. Check ocean data scripts.{RESET}")
    sys.exit(1)

print(f"{GREEN}✓ Ocean data fetched successfully{RESET}")

# ============================================================
# STEP 2 — Load model and predict
# ============================================================

print(f"\n{BOLD}▶ STEP 2 — Running AI predictions...{RESET}")

model         = joblib.load(MODEL_PATH)
feature_names = joblib.load(FEATURE_NAMES_PATH)

df = pd.read_csv(CSV_PATH)

# fill missing values
df = df.fillna(df.median(numeric_only=True))

X = df[feature_names]

df['probability'] = model.predict_proba(X)[:, 1]
df['prediction']  = (df['probability'] >= THRESHOLD).astype(int)

print(f"{GREEN}✓ Predictions done — {len(df)} zones{RESET}")
print(f"   Fish present : {df['prediction'].sum()}")
print(f"   Fish absent  : {(df['prediction'] == 0).sum()}")

# ============================================================
# STEP 3 — Map probability to density
# ============================================================

def get_density(prob):
    if prob >= 0.80:
        return "high"
    elif prob >= 0.50:
        return "moderate"
    elif prob >= 0.30:
        return "low"
    else:
        return "critical"

df['density']    = df['probability'].apply(get_density)
df['confidence'] = (df['probability'] * 100).round().astype(int)

# ============================================================
# STEP 4 — Save to Supabase
# ============================================================

print(f"\n{BOLD}▶ STEP 3 — Saving to Supabase...{RESET}")

db = create_client(SUPABASE_URL, SUPABASE_KEY)

zones_res = db.table("fishing_zones").select("id, lat, lng").execute()
zones     = zones_res.data

if not zones:
    print(f"{RED}✗ No zones found in Supabase.{RESET}")
    sys.exit(1)

def find_nearest_zone(lat, lng, zones):
    min_dist = float("inf")
    nearest  = None
    for z in zones:
        dist = (z["lat"] - lat) ** 2 + (z["lng"] - lng) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest  = z
    return nearest

success = 0
errors  = 0

for _, row in df.iterrows():
    zone = find_nearest_zone(row["Latitude"], row["Longitude"], zones)

    if zone is None:
        errors += 1
        continue

    record = {
        "zone_id"        : zone["id"],
        "date"           : TARGET_DATE,
        "density"        : row["density"],
        "confidence"     : int(row["confidence"]),
        "sst_value"      : round(float(row["sst"]),         4) if "sst"         in row else None,
        "chl_value"      : round(float(row["chlorophyll"]), 4) if "chlorophyll" in row else None,
        "ssh_value"      : round(float(row["ssh"]),         4) if "ssh"         in row else None,
        "salinity_value" : round(float(row["salinity"]),    4) if "salinity"    in row else None,
        "presence"       : int(row["prediction"]),
    }

    res = db.table("zone_predictions").upsert(
        record,
        on_conflict="zone_id,date"
    ).execute()

    if res.data:
        success += 1
    else:
        errors += 1

# ============================================================
# SUMMARY
# ============================================================

print(f"\n{BOLD}{'='*55}{RESET}")
print(f"  Pipeline Summary")
print(f"{BOLD}{'='*55}{RESET}")
print(f"  {GREEN}✓{RESET}  Ocean data   fetched")
print(f"  {GREEN}✓{RESET}  Predictions  done")
print(f"  {GREEN}✓{RESET}  Supabase     {success} records saved")

if errors:
    print(f"  {YELLOW}⚠{RESET}  {errors} records failed")

print(f"\n{GREEN}{BOLD}✅ Pipeline completed — {TARGET_DATE}{RESET}\n")