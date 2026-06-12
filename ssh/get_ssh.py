import copernicusmarine
import xarray as xr
import os
from datetime import datetime, timedelta

MIN_LON = -16.55
MAX_LON = -16.20
MIN_LAT = 23.55
MAX_LAT = 24.05

TARGET_DATE = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")


OUTPUT_DIR  = "./ocean_data"
OUTPUT_FILE = "ssh_forecast_tomorrow.nc"


def fetch_ssh_forecast():
    print(f"Requesting SSH forecast data for {TARGET_DATE}...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed old file: {file_path}")

    copernicusmarine.subset(
        dataset_id="cmems_mod_glo_phy_anfc_0.083deg_P1D-m",
        variables=["zos"],          # zos = SSH (Sea Surface Height above geoid)
        minimum_longitude=MIN_LON,
        maximum_longitude=MAX_LON,
        minimum_latitude=MIN_LAT,
        maximum_latitude=MAX_LAT,
        start_datetime=f"{TARGET_DATE} 00:00:00",
        end_datetime=f"{TARGET_DATE} 23:59:59",
        output_filename=OUTPUT_FILE,
        output_directory=OUTPUT_DIR,
    )
    print(f"Download complete! Saved to {OUTPUT_DIR}/{OUTPUT_FILE}")


def read_and_preview_data():
    file_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    if not os.path.exists(file_path):
        print("File not found. Run fetch_ssh_forecast() first.")
        return

    print("\n--- Preprocessing SSH Data ---")
    ds  = xr.open_dataset(file_path)
    ssh = ds["zos"]

    print(ssh)
    print(f"\nMin SSH : {float(ssh.min()):.4f} m")
    print(f"Max SSH : {float(ssh.max()):.4f} m")
    print(f"Mean SSH: {float(ssh.mean()):.4f} m")

    ds.close()


if __name__ == "__main__":
    fetch_ssh_forecast()
    read_and_preview_data()
