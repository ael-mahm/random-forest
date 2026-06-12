import copernicusmarine
import os
from datetime import datetime, timedelta

# 1. Dakhla region coordinates
MIN_LON = -16.85
MAX_LON = -15.90
MIN_LAT  = 23.25
MAX_LAT  = 24.35

TARGET_DATE = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
OUTPUT_DIR = "./ocean_data"
OUTPUT_FILE = "chl_forecast_tomorrow.nc"

def fetch_chl_forecast():

    print(f"Requesting Chlorophyll forecast data for {TARGET_DATE}...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed old file: {file_path}")

    # Use the global biogeochemical model
    copernicusmarine.subset(

        # Notice: using BGC instead of PHY
        dataset_id="cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m",

        variables=["chl"],   # 'chl' is the chlorophyll variable

        minimum_longitude=MIN_LON,
        maximum_longitude=MAX_LON,

        minimum_latitude=MIN_LAT,
        maximum_latitude=MAX_LAT,

        start_datetime=f"{TARGET_DATE} 00:00:00",
        end_datetime=f"{TARGET_DATE} 23:59:59",

        minimum_depth=0.0,   # Surface layer
        maximum_depth=1.0,

        output_filename=OUTPUT_FILE,
        output_directory=OUTPUT_DIR
    )

    print(f"Download complete! Saved to {OUTPUT_DIR}/{OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_chl_forecast()
