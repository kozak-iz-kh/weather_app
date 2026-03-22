import os
import threading
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

load_dotenv()

from weather.open_meteo import fetch_weather
# from weather.aemet import fetch_warnings
from ai.claude import generate_forecast
from bot.telegram import send_to_all
from bot.polling import run_polling


def run_daily_forecast():
    print(f"[{datetime.now()}] Running daily forecast...")
    try:
        weather = fetch_weather()
        warnings = []  # fetch_warnings() — AEMET вимкнено
        text = generate_forecast(weather, warnings)
        send_to_all(text)
        print(f"[{datetime.now()}] Done.")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")


if __name__ == "__main__":
    poll_thread = threading.Thread(target=run_polling, daemon=True, name="TelegramPoller")
    poll_thread.start()

    scheduler = BlockingScheduler(timezone="Europe/Madrid")
    scheduler.add_job(run_daily_forecast, CronTrigger(hour=9, minute=30))

    print(f"[{datetime.now()}] Scheduler started. Daily forecast at 09:30 Europe/Madrid.")

    # Uncomment the line below to send a test message immediately on startup:
    run_daily_forecast()

    scheduler.start()
