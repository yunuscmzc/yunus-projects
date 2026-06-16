import pandas as pd
import numpy as np
from datetime import datetime
from forecast_helper import get_production_data,get_historical_weather,get_weather_forecast
import statsmodels.api as sm

date_to_be_forecasted = str(datetime.now()+pd.DateOffset(1))[:10]
last_datetime_to_be_forecasted = pd.to_datetime(date_to_be_forecasted)+pd.DateOffset(days=1,hours=-1)

current_date = datetime.now().date()
production_data = get_production_data()

start_date = "2025-04-01"
plant_coordinates = [
    [37.7908, 33.5847],  # Konya
    [37.1674, 38.7955],  # Urfa
    [36.8000, 34.6400],  # Mersin
    [38.5000, 43.3800],  # Van
    [39.5700, 32.5300],  # Ankara
]
weather_forecast_models=["ecmwf_ifs025"]
weather_variables = [
    "shortwave_radiation",
    "temperature_2m", 
    "et0_fao_evapotranspiration",
    "cloud_cover",
    "direct_normal_irradiance",
    "relative_humidity_2m",
]

meteo_data_historical = get_historical_weather(start_date=start_date,
                                    variables=weather_variables,
                                    coordinates=plant_coordinates,
                                    get_forecast_data=False,
                                    models=weather_forecast_models)

meteo_data_future = get_weather_forecast(forecast_days=10,
                                         past_days=25,
                                         variables=weather_variables,
                                         coordinates=plant_coordinates,
                                         models=weather_forecast_models,)

meteo_data_historical = meteo_data_historical.dropna()
meteo_data_future = meteo_data_future.dropna()
meteo_data_historical.insert(0,"type","historical")
meteo_data_future.insert(0,"type","future")
meteo_data_all = pd.concat([meteo_data_historical,meteo_data_future],axis=0)
meteo_data_all["priorty"] = meteo_data_all.groupby("dt")["type"].rank(ascending=False)
meteo_data_all = meteo_data_all[meteo_data_all["priorty"] == 1]
meteo_data_all = meteo_data_all.sort_values("dt")
meteo_data_all = meteo_data_all.drop(["type","priorty"],axis=1)


df_dates = pd.date_range(start_date,last_datetime_to_be_forecasted,freq="1h")
df_dates = df_dates.tz_localize("Europe/Istanbul")

df = pd.DataFrame()
df["dt"] = df_dates

df = df.merge(production_data,how="left")
df = df.merge(meteo_data_all,how="left")

df["trend"] = np.arange(len(df)) / len(df)
df["sun_rt_lag_7days"] = df["sun_rt"].shift(7*24)

df["hour"] = df["dt"].dt.hour
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
df["dni_x_hour_0"] = df["location_000 direct_normal_irradiance"] * df["hour_sin"]
df["dni_x_hour_2"] = df["location_002 direct_normal_irradiance"] * df["hour_sin"]
df["humid_x_hour_0"] = df["location_000 relative_humidity_2m"] * df["hour_cos"]
df["humid_x_hour_2"] = df["location_002 relative_humidity_2m"] * df["hour_cos"]
df["hour^2"] = (df["hour"] - 12) ** 2
df["hour^2_cos"] = df["hour^2"] * df["hour_cos"]

df = df.drop(columns=["hour"])
df = df.drop(columns=["location_001 relative_humidity_2m"])
df = df.drop(columns=["location_004 temperature_2m"])
df = df.drop(columns=["location_002 et0_fao_evapotranspiration"])
df = df.drop(columns=["location_000 cloud_cover"])

train_X = df.dropna().drop(["dt","sun_rt"],axis=1)
train_y = df.dropna()["sun_rt"]
train_X = sm.add_constant(train_X)


model = sm.OLS(train_y, train_X)
results = model.fit()

next_day_X = df.iloc[-24:].drop(["dt","sun_rt"],axis=1)
next_day_X = sm.add_constant(next_day_X)
next_day_X = next_day_X.reindex(columns=train_X.columns, fill_value=0)

next_day_pred = results.predict(next_day_X)
next_day_pred = np.maximum(next_day_pred,0)

test_hours = df["dt"].iloc[-len(next_day_pred):].dt.hour.values
next_day_pred[(test_hours >= 19) | (test_hours <= 5)] = 0

print(next_day_pred.tolist())
