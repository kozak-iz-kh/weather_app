from weather.open_meteo import fetch_weather
from ai.claude import generate_forecast
from bot.telegram import send_message

weather = fetch_weather()
text = generate_forecast(weather, [])
send_message(text)
