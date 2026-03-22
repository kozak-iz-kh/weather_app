import os
import requests


def send_to_chat(chat_id: int, text: str) -> bool:
    """Send a message to a specific chat_id."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[Telegram] BOT_TOKEN not configured.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"[Telegram] Failed to send to {chat_id}: {e}")
        return False


def send_to_all(text: str) -> None:
    """Broadcast text to all subscribers."""
    from bot.subscribers import get_all
    subscribers = get_all()
    if not subscribers:
        print("[Telegram] No subscribers. Nothing sent.")
        return
    print(f"[Telegram] Broadcasting to {len(subscribers)} subscriber(s)...")
    for chat_id in subscribers:
        send_to_chat(chat_id, text)


def send_message(text: str) -> bool:
    """Legacy: send to TELEGRAM_CHAT_ID from env."""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("[Telegram] CHAT_ID not configured.")
        return False
    return send_to_chat(int(chat_id), text)
