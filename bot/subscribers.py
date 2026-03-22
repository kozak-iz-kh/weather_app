import json
import os
import threading

SUBSCRIBERS_FILE = "subscribers.json"
_lock = threading.Lock()


def _load() -> set:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return set(json.load(f))
    except (json.JSONDecodeError, ValueError):
        return set()


def _save(ids: set) -> None:
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(ids), f)


def add(chat_id: int) -> bool:
    """Add subscriber. Returns True if newly added, False if already subscribed."""
    with _lock:
        ids = _load()
        if chat_id in ids:
            return False
        ids.add(chat_id)
        _save(ids)
        return True


def remove(chat_id: int) -> bool:
    """Remove subscriber. Returns True if removed, False if not found."""
    with _lock:
        ids = _load()
        if chat_id not in ids:
            return False
        ids.discard(chat_id)
        _save(ids)
        return True


def get_all() -> list:
    """Return list of all subscriber chat IDs."""
    with _lock:
        return list(_load())
