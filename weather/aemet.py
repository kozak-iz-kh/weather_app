import os
import requests


# Valencia province area code for AEMET warnings
VALENCIA_AREA_CODE = "61"


def fetch_warnings() -> list[str]:
    """
    Fetch active weather warnings for Valencia from AEMET OpenData.
    Returns a list of warning description strings, or [] if unavailable.
    Never raises — AEMET is treated as non-critical.
    """
    api_key = os.getenv("AEMET_API_KEY")
    if not api_key:
        print("[AEMET] No API key configured, skipping warnings.")
        return []

    try:
        # Step 1: get the datos URL (API key as query param — AEMET standard)
        url = f"https://opendata.aemet.es/opendata/api/avisos_cap/ultimoelaborado/area/{VALENCIA_AREA_CODE}"
        params = {"api_key": api_key}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()

        if not resp.content:
            print("[AEMET] Empty response — no active warnings.")
            return []

        datos_url = resp.json().get("datos")
        if not datos_url:
            print("[AEMET] No datos URL in response.")
            return []

        # Step 2: fetch actual warning data
        data_resp = requests.get(datos_url, params=params, timeout=10)
        data_resp.raise_for_status()

        if not data_resp.content:
            print("[AEMET] No active warnings.")
            return []

        warnings_data = data_resp.json()
        return _parse_warnings(warnings_data)

    except Exception as e:
        print(f"[AEMET] Warning fetch failed: {e}")
        return []


def _parse_warnings(data) -> list[str]:
    """Extract active warning descriptions from AEMET response."""
    warnings = []

    if not isinstance(data, list):
        data = [data]

    for item in data:
        # AEMET CAP format: look for info blocks with severity
        info_list = item.get("info", [])
        if not isinstance(info_list, list):
            info_list = [info_list]

        for info in info_list:
            severity = info.get("severity", "")
            event = info.get("event", "")
            description = info.get("description", "")

            if severity and severity.lower() not in ("minor", "unknown"):
                text = f"{severity}: {event}"
                if description:
                    text += f" — {description[:100]}"
                warnings.append(text)

    return warnings
