import xarray as xr
import pandas as pd
import os
import numpy as np

# ── Paths to the four files ─────────────────────────
SST_FILE = "./../sst/ocean_data/sst_forecast_tomorrow.nc"
CHL_FILE = "./../chl/ocean_data/chl_forecast_tomorrow.nc"
SSH_FILE = "./../ssh/ocean_data/ssh_forecast_tomorrow.nc"
SSS_FILE = "./../sss/ocean_data/sss_forecast_tomorrow.nc"


def prepare_ai_dataset():
    print("1. Opening the four ocean datasets...")
    sst_ds = xr.open_dataset(SST_FILE)
    chl_ds = xr.open_dataset(CHL_FILE)
    ssh_ds = xr.open_dataset(SSH_FILE)
    sss_ds = xr.open_dataset(SSS_FILE)

    # Extracting the variables
    sst = sst_ds['thetao']
    chl = chl_ds['chl']
    ssh = ssh_ds['zos']
    sss = sss_ds['so']

    print("2. Standardizing dimensions (dropping 'depth' to avoid merge errors)...")
    if 'depth' in sst.coords: sst = sst.drop_vars('depth')
    if 'depth' in sss.coords: sss = sss.drop_vars('depth')
    if 'depth' in chl.coords: chl = chl.drop_vars('depth')
    if 'depth' in ssh.coords: ssh = ssh.drop_vars('depth')
    
    print("3. Running Linear Interpolation for Chlorophyll...")
    # Using 'linear' safely now that the CHL bounding box is expanded
    chl_aligned = chl.interp(
        latitude=sst.latitude,
        longitude=sst.longitude,
        method="linear",
        kwargs={"fill_value": "extrapolate"}
    )

    print("4. Merging variables intelligently via xarray (ensuring perfect alignment)...")
    ds_combined = xr.Dataset({
        'SST': sst,
        'SSS': sss,
        'SSH': ssh,
        'CHL': chl_aligned
    })

    print("5. Converting to the final feature table...")
    # Converting to pandas DataFrame once, eliminating fractional coordinate mismatches
    df_final = ds_combined.to_dataframe().dropna().reset_index()

    # Reordering and renaming columns for the AI model
    df_final = df_final[['longitude', 'latitude', 'SST', 'CHL', 'SSH', 'SSS']]
    df_final.columns = [
        'Longitude', 
        'Latitude', 
        'sst', 
        'chlorophyll', 
        'ssh', 
        'salinity'
    ]

    print("\n=======================================================")
    print("Final Combined Table (AI Features):")
    print("=======================================================")
    print(df_final)

    # Create the directory if it does not exist
    csv_path = "./ocean_data/dakhla_ai_features_full.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    hour = 6
    df_final['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    df_final['hour_cos'] = np.cos(2 * np.pi * hour / 24)
    # Save the dataset
    df_final.to_csv(csv_path, index=False)
    print(f"\n-> CSV file saved successfully at: {csv_path}")

if __name__ == "__main__":
    prepare_ai_dataset()
