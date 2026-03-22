import os
import requests


def fetch_weather() -> dict:
    """Fetch daily weather forecast for Valencia from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": os.getenv("LATITUDE", "39.4699"),
        "longitude": os.getenv("LONGITUDE", "-0.3763"),
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
        "timezone": "Europe/Madrid",
        "forecast_days": 1,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()["daily"]

    return {
        "temp_max": data["temperature_2m_max"][0],
        "temp_min": data["temperature_2m_min"][0],
        "feels_max": data["apparent_temperature_max"][0],
        "feels_min": data["apparent_temperature_min"][0],
        "precipitation": data["precipitation_sum"][0],
        "precipitation_probability": data["precipitation_probability_max"][0],
        "weathercode": data["weathercode"][0],
        "windspeed": data["windspeed_10m_max"][0],
        "uv_index": data["uv_index_max"][0],
    }
