import os
import time
import calendar
import numpy as np
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from eptr2 import EPTR2
from dotenv import load_dotenv

STUDENT_ID = 2021402078
np.random.seed(STUDENT_ID % 2**31)

START_DATE = "2022-01-01"
END_DATE   = "2026-03-31"

LOCATIONS = {
    "konya":     {"latitude": 37.87, "longitude": 32.48},
    "gaziantep": {"latitude": 37.07, "longitude": 37.38},
    "izmir":     {"latitude": 38.42, "longitude": 27.14},
}

os.makedirs("data", exist_ok=True)


def make_monthly_ranges(start_year, start_month, end_year, end_month):
    ranges = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        first_day = f"{year}-{month:02d}-01"
        last_day  = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        ranges.append((first_day, last_day))
        month += 1
        if month > 12:
            month = 1
            year += 1
    return ranges


def download_epias_solar():
    load_dotenv()
    username = os.getenv("EPTR_USERNAME")
    password = os.getenv("EPTR_PASSWORD")
    if not username or not password:
        raise ValueError("EPİAŞ credentials not found in .env file.")

    eptr = EPTR2(username=username, password=password, recycle_tgt=True)
    date_ranges = make_monthly_ranges(2022, 1, 2026, 3)
    print(f"  Total months to download: {len(date_ranges)}")

    frames = []
    for i, (start, end) in enumerate(date_ranges):
        print(f"  [{i+1}/{len(date_ranges)}] {start} -> {end} ...", end=" ", flush=True)
        try:
            result = eptr.call("ren-rt-gen", start_date=start, end_date=end)
            frames.append(result)
            print("OK")
            time.sleep(0.5)
        except Exception as e:
            print(f"FAILED: {e}")
            time.sleep(3)

    if not frames:
        raise RuntimeError("No EPİAŞ data downloaded.")

    df = pd.concat(frames, ignore_index=True)
    print(f"\n  Columns: {df.columns.tolist()}")
    return df


def clean_epias_solar(df):
    df.columns = [c.strip() for c in df.columns]

    dt_col = None
    for c in ["date", "Tarih", "tarih", "Date", "datetime", "Saat"]:
        if c in df.columns:
            dt_col = c
            break
    if dt_col is None:
        dt_col = df.columns[0]
    print(f"  Datetime column: '{dt_col}'")
    df["datetime"] = pd.to_datetime(df[dt_col], dayfirst=True, errors="coerce")

    solar_col = None
    for c in ["Güneş", "Gunes", "gunes", "solar", "Solar", "güneş", "GÜNEŞ", "Sun", "sun"]:
        if c in df.columns:
            solar_col = c
            break
    if solar_col is None:
        print("  All columns:", df.columns.tolist())
        raise ValueError("Cannot find solar column — see above.")
    print(f"  Solar column: '{solar_col}'")

    df["solar_mwh"] = pd.to_numeric(df[solar_col], errors="coerce")
    df["datetime"] = df["datetime"].dt.tz_convert("Europe/Istanbul") if df["datetime"].dt.tz is not None else df["datetime"].dt.tz_localize("Etc/GMT-3")
    df = df[["datetime", "solar_mwh"]].drop_duplicates("datetime").sort_values("datetime").reset_index(drop=True)
    df["solar_mwh"] = df["solar_mwh"].clip(lower=0)
    print(f"  Cleaned: {len(df):,} rows | {df['datetime'].min()} -> {df['datetime'].max()}")
    return df


WEATHER_VARIABLES = ["shortwave_radiation", "temperature_2m", "cloud_cover",
                     "direct_radiation", "precipitation", "wind_speed_10m"]


def download_weather_one_location(name, lat, lon):
    cache_session = requests_cache.CachedSession(".cache_openmeteo", expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.3)
    om = openmeteo_requests.Client(session=retry_session)

    params = {"latitude": lat, "longitude": lon, "start_date": START_DATE,
              "end_date": END_DATE, "hourly": WEATHER_VARIABLES,
              "timezone": "Europe/Istanbul", "wind_speed_unit": "ms"}

    print(f"  Weather: {name} ...", end=" ", flush=True)
    response = om.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)[0]
    hourly   = response.Hourly()
    times    = pd.date_range(
        start=pd.Timestamp(hourly.Time(), unit="s", tz="Europe/Istanbul"),
        end=pd.Timestamp(hourly.TimeEnd(), unit="s", tz="Europe/Istanbul"),
        freq=pd.Timedelta(seconds=hourly.Interval()), inclusive="left")

    data = {"datetime": times}
    for i, var in enumerate(WEATHER_VARIABLES):
        data[f"{name}_{var}"] = hourly.Variables(i).ValuesAsNumpy()
    df = pd.DataFrame(data)
    print(f"OK ({len(df):,} rows)")
    return df


def download_all_weather():
    dfs = []
    for name, coords in LOCATIONS.items():
        coords2 = {"lat": coords["latitude"], "lon": coords["longitude"]}
        dfs.append(download_weather_one_location(name, **coords2))
        time.sleep(1)
    merged = dfs[0]
    for d in dfs[1:]:
        merged = pd.merge(merged, d, on="datetime", how="outer")
    print(f"  Weather merged: {merged.shape}")
    return merged.sort_values("datetime").reset_index(drop=True)


def merge_and_enrich(solar, weather):
    solar["datetime"] = solar["datetime"].dt.tz_convert("Europe/Istanbul")
    weather["datetime"] = pd.to_datetime(weather["datetime"])
    if weather["datetime"].dt.tz is None:
        weather["datetime"] = weather["datetime"].dt.tz_localize("Europe/Istanbul")
    else:
        weather["datetime"] = weather["datetime"].dt.tz_convert("Europe/Istanbul")

    df = pd.merge(solar, weather, on="datetime", how="inner")

    df["date"]        = df["datetime"].dt.date
    df["year"]        = df["datetime"].dt.year
    df["month"]       = df["datetime"].dt.month
    df["day"]         = df["datetime"].dt.day
    df["hour"]        = df["datetime"].dt.hour
    df["day_of_year"] = df["datetime"].dt.dayofyear
    df["week"]        = df["datetime"].dt.isocalendar().week.astype(int)
    df["weekday"]     = df["datetime"].dt.weekday

    for var in ["shortwave_radiation", "cloud_cover", "temperature_2m",
                "direct_radiation", "precipitation", "wind_speed_10m"]:
        cols = [c for c in df.columns if c.endswith(var)]
        if cols:
            df[f"avg_{var}"] = df[cols].mean(axis=1)

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing):
        print("  Forward-filling gaps...")
        df = df.sort_values("datetime").ffill(limit=2).dropna(subset=["solar_mwh"])
    else:
        print("  No missing values.")

    df = df.sort_values("datetime").reset_index(drop=True)
    print(f"  Final: {df.shape[0]:,} rows x {df.shape[1]} cols")
    return df


if __name__ == "__main__":
    print("=" * 60)
    print("HW3 Data Download — Yunus Emre Camizci (2021402078)")
    print("=" * 60)

    # Step 1: EPİAŞ — skip if already saved
    if os.path.exists("data/epias_solar.csv"):
        print("\n[1/3] EPİAŞ file already exists — loading from disk...")
        solar = pd.read_csv("data/epias_solar.csv", parse_dates=["datetime"])
        if solar["datetime"].dt.tz is None:
            solar["datetime"] = solar["datetime"].dt.tz_localize("Europe/Istanbul")
    else:
        print("\n[1/3] Downloading EPİAŞ solar generation...")
        solar = clean_epias_solar(download_epias_solar())
        solar.to_csv("data/epias_solar.csv", index=False)
        print("  Saved -> data/epias_solar.csv")

    # Step 2: Weather
    print("\n[2/3] Open-Meteo weather...")
    weather = download_all_weather()
    weather.to_csv("data/weather.csv", index=False)
    print("  Saved -> data/weather.csv")

    # Step 3: Merge
    print("\n[3/3] Merging...")
    df = merge_and_enrich(solar, weather)
    df.to_csv("data/solar_dataset.csv", index=False)
    print("  Saved -> data/solar_dataset.csv")

    print(f"\nAll done! Shape: {df.shape}")
