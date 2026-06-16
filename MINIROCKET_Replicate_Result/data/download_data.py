#!/usr/bin/env python3
"""
Download UCR Time Series Archive datasets used in the MINIROCKET replication.
Datasets are saved to data/UCR/<dataset_name>/.

Usage:
    python data/download_data.py
"""

import os
import urllib.request
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "UCR")

DATASETS = [
    "ItalyPowerDemand",
    "SyntheticControl",
    "Wafer",
    "FaceAll",
    "ECG200",
    "Plane",
    "Beef",
    "Coffee",
    "OliveOil",
    "Trace",
]

UCR_BASE_URL = "https://www.timeseriesclassification.com/Downloads/{}.zip"


def download_dataset(name, out_dir):
    url         = UCR_BASE_URL.format(name)
    zip_path    = os.path.join(out_dir, f"{name}.zip")
    dataset_dir = os.path.join(out_dir, name)

    if os.path.isdir(dataset_dir):
        print(f"  [skip] {name} already exists")
        return True

    print(f"  Downloading {name} ...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            with open(zip_path, "wb") as f:
                f.write(response.read())
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(out_dir)
        os.remove(zip_path)
        print("done")
        return True
    except Exception as e:
        print(f"FAILED ({e})")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return False


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Saving datasets to: {DATA_DIR}\n")
    ok, fail = [], []
    for ds in DATASETS:
        (ok if download_dataset(ds, DATA_DIR) else fail).append(ds)
    print(f"\nDownloaded: {len(ok)}/{len(DATASETS)}")
    if fail:
        print(f"Failed: {fail}")
        print("Manual download: https://www.timeseriesclassification.com/")


if __name__ == "__main__":
    main()
