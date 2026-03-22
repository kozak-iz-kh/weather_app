import os
import time
import requests

from bot.subscribers import add, remove
from bot.telegram import send_to_chat


def _get_updates(token: str, offset: int, timeout: int = 30) -> list:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        resp = requests.get(
            url,
            params={"offset": offset, "timeout": timeout},
            timeout=timeout + 5,
        )
        resp.raise_for_status()
        return resp.json().get("result", [])
    except Exception as e:
        print(f"[Polling] getUpdates error: {e}")
        time.sleep(5)
        return []


def _handle_update(update: dict, token: str) -> None:
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return

    if text.startswith("/start"):
        if add(chat_id):
            send_to_chat(chat_id, "✅ Ти підписаний на щоденний прогноз погоди Валенсії! Повідомлення надходитиме щодня о 9:30.")
        else:
            send_to_chat(chat_id, "Ти вже підписаний. Прогноз надходить щодня о 9:30 🌤")

    elif text.startswith("/stop"):
        if remove(chat_id):
            send_to_chat(chat_id, "❌ Ти відписаний від прогнозу погоди.")
        else:
            send_to_chat(chat_id, "Ти не підписаний на прогноз.")


def run_polling() -> None:
    """Blocking loop. Run this in a daemon thread."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[Polling] TELEGRAM_BOT_TOKEN not set. Polling disabled.")
        return

    print("[Polling] Starting getUpdates loop...")
    offset = 0

    while True:
        updates = _get_updates(token, offset)
        for update in updates:
            _handle_update(update, token)
            offset = update["update_id"] + 1
