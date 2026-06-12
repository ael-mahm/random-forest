import copernicusmarine
import xarray as xr
import os
from datetime import datetime, timedelta

MIN_LON = -16.55
MAX_LON = -16.20
MIN_LAT = 23.55
MAX_LAT = 24.05

# 2. Target date for the forecast
TARGET_DATE = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")

# 3. Define output settings
OUTPUT_DIR = "./ocean_data"
OUTPUT_FILE = "sst_forecast_tomorrow.nc"

def fetch_sst_forecast():
    print(f"Requesting SST forecast data for {TARGET_DATE}...")
    
    # Create directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Manually handle overwriting
    file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed old file: {file_path}")

    # 2. Use the Copernicus subset tool
    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m", 
        variables=["thetao"],  
        minimum_longitude=MIN_LON,
        maximum_longitude=MAX_LON,
        minimum_latitude=MIN_LAT,
        maximum_latitude=MAX_LAT,
        start_datetime=f"{TARGET_DATE} 00:00:00",
        end_datetime=f"{TARGET_DATE} 23:59:59",
        minimum_depth=0.0,     # <-- UPDATED: Start from absolute 0
        maximum_depth=1.0,     # <-- UPDATED: Go down to 1 meter
        output_filename=OUTPUT_FILE,
        output_directory=OUTPUT_DIR
    )
    
    print(f"Download complete! Saved to {OUTPUT_DIR}/{OUTPUT_FILE}")

def read_and_preview_data():
    """Reads the downloaded NetCDF file and extracts the SST values."""
    file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    
    if os.path.exists(file_path):
        print("\n--- Preprocessing Data ---")
        # Load the dataset using xarray
        dataset = xr.open_dataset(file_path)
        
        # Extract the temperature variable
        sst_data = dataset['thetao']
        
        print(sst_data)
        
        dataset.close()
    else:
        print("File not found. Please run the download function first.")

if __name__ == "__main__":
    fetch_sst_forecast()
    read_and_preview_data()
