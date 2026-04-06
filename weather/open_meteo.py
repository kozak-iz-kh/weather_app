import os
import requests


def _avg(values: list) -> int:
    return round(sum(values) / len(values)) if values else 0


def fetch_weather() -> dict:
    """Fetch daily weather forecast for Valencia from Open-Meteo API."""
    lat = os.getenv("LATITUDE", "39.4699")
    lon = os.getenv("LONGITUDE", "-0.3763")

    # --- forecast API (daily + hourly cloud cover in one request) ---
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join([
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "weathercode",
                "windspeed_10m_max",
                "uv_index_max",
            ]),
            "hourly": "cloudcover",
            "timezone": "Europe/Madrid",
            "forecast_days": 1,
        },
        timeout=10,
    )
    response.raise_for_status()
    body = response.json()
    daily = body["daily"]

    # hourly cloudcover: 24 values for today (index 0–23, local time)
    cc = body["hourly"]["cloudcover"]
    cloud = {
        "morning":   _avg(cc[6:12]),   # 06:00–11:00
        "afternoon": _avg(cc[12:18]),  # 12:00–17:00
        "evening":   _avg(cc[18:22]),  # 18:00–21:00
    }

    # --- marine API for sea surface temperature (hourly, take midday value) ---
    marine = requests.get(
        "https://marine-api.open-meteo.com/v1/marine",
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "sea_surface_temperature",
            "timezone": "Europe/Madrid",
            "forecast_days": 1,
        },
        timeout=10,
    )
    marine.raise_for_status()
    sea_temp = marine.json()["hourly"]["sea_surface_temperature"][12]  # midday

    return {
        "temp_max": daily["temperature_2m_max"][0],
        "temp_min": daily["temperature_2m_min"][0],
        "feels_max": daily["apparent_temperature_max"][0],
        "feels_min": daily["apparent_temperature_min"][0],
        "precipitation": daily["precipitation_sum"][0],
        "precipitation_probability": daily["precipitation_probability_max"][0],
        "weathercode": daily["weathercode"][0],
        "windspeed": daily["windspeed_10m_max"][0],
        "uv_index": daily["uv_index_max"][0],
        "cloud": cloud,
        "sea_temp": sea_temp,
    }
