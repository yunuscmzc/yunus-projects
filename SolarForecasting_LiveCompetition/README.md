# Live Next-Day Solar Power Forecasting

A real-time forecasting system that predicts the **next 24 hours of solar power production** for Turkish solar plants. Built for a live forecasting competition where predictions were submitted daily and scored against actual measured production.

Each run pulls fresh weather forecasts, blends them with the latest historical weather and production data, fits a regression model, and outputs an hourly forecast for the following day.

## How It Works

1. **Weather data** — fetches hourly forecasts and historical weather from the [Open-Meteo API](https://open-meteo.com/) for **5 Turkish solar plant locations** (Konya, Urfa, Mersin, Van, Ankara). Variables include shortwave radiation, temperature, cloud cover, direct normal irradiance, relative humidity, and evapotranspiration.
2. **Production data** — pulls the latest measured solar production from a live data source.
3. **Feature engineering** — builds predictive features from the raw weather data:
   - Cyclical hour encoding (`hour_sin`, `hour_cos`) to capture the daily solar cycle
   - Interaction terms (irradiance × hour, humidity × hour) to model time-dependent weather effects
   - A 7-day production lag and a quadratic hour term
   - A linear trend component
4. **Model** — fits an Ordinary Least Squares (OLS) regression, then predicts the next 24 hours and clamps physically-impossible values (negative production and nighttime hours) to zero.

## Files

| File | Description |
|------|-------------|
| `forecast.py` | **Main forecasting pipeline** — data assembly, feature engineering, model fitting, and next-day prediction. |
| `forecast_helper.py` / `forecast_helper.r` | API-access helper functions for fetching weather and production data (course-provided scaffolding). |

> **Attribution:** The forecasting model, feature engineering, and methodology in `forecast.py` are my own work. The `forecast_helper` files are instructor-provided utilities for accessing the data APIs. The project was conducted within a 5-person group, but the modeling and code here are mine.

## Setup

```bash
pip install pandas numpy statsmodels openmeteo-requests requests-cache retry-requests
```

## Usage

```bash
python forecast.py
```

This prints the predicted hourly solar production (24 values) for the next day.

## Tech Stack

- **Python** — pandas, NumPy, statsmodels (OLS)
- **R** — equivalent helper implementation (httr, dplyr, lubridate)
- **Open-Meteo API** — live and historical weather data
