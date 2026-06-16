# Solar Power Forecasting with Generalized Additive Models

Hourly solar generation forecasting for Turkey using **Generalized Additive Models (GAMs)**. The dataset covers January 2022 – March 2026 (37,224 hourly observations) with weather predictors from three Turkish locations (Konya, Gaziantep, Izmir) sourced from the Open-Meteo Historical Weather API.

## Topics Covered

- Exploratory analysis of solar generation patterns (daily/seasonal cycles)
- Feature engineering from weather data (shortwave radiation, temperature, cloud cover)
- GAM fitting with spline terms and interaction effects
- Forecast evaluation: RMSE, MAE, and visual inspection of residuals
- Train/test split: train before 2026-01-01, test Jan–Mar 2026

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
quarto render GAMs_SolarForecasting.qmd
```
