import os
import anthropic


# WMO weathercode → human-readable Ukrainian description
WMO_CODES = {
    0: "ясно",
    1: "переважно ясно", 2: "частково хмарно", 3: "похмуро",
    45: "туман", 48: "туман з інеєм",
    51: "легка мряка", 53: "мряка", 55: "сильна мряка",
    61: "невеликий дощ", 63: "дощ", 65: "сильний дощ",
    71: "невеликий сніг", 73: "сніг", 75: "сильний сніг",
    80: "невеликі зливи", 81: "зливи", 82: "сильні зливи",
    95: "гроза", 96: "гроза з градом", 99: "сильна гроза з градом",
}


def generate_forecast(weather: dict, warnings: list[str]) -> str:
    """Generate a Ukrainian weather overview using Claude."""
    city = os.getenv("CITY_NAME", "Valencia")
    weather_desc = WMO_CODES.get(weather["weathercode"], f"код {weather['weathercode']}")

    warnings_block = (
        "Офіційні попередження AEMET:\n" + "\n".join(f"• {w}" for w in warnings)
        if warnings
        else ""
    )

    cloud = weather["cloud"]
    prompt = f"""Прогноз погоди на сьогодні для міста {city}, Іспанія:
- Загальний стан (WMO): {weather_desc}
- Хмарність (реальні %): вранці {cloud['morning']}%, вдень {cloud['afternoon']}%, ввечері {cloud['evening']}%
- Температура: від {weather['temp_min']}°C до {weather['temp_max']}°C
- Відчувається як: від {weather['feels_min']}°C до {weather['feels_max']}°C
- Максимальний вітер: {weather['windspeed']} км/год
- Опади за день: {weather['precipitation']} мм (ймовірність {weather['precipitation_probability']}%)
- Максимальний UV-індекс: {weather['uv_index']}
- Температура моря: {weather['sea_temp']}°C
{warnings_block}
Напиши короткий дружній щоденний прогноз погоди (4-6 речень) українською мовою. \
При описі хмарності спирайся на реальні відсотки, а не на загальний WMO-стан — наприклад, 10% це фактично ясно, 70% це похмуро. \
Опиши що чекати протягом усього дня — вранці, вдень, ввечері якщо є що відзначити. \
Якщо є попередження — згадай їх на початку. \
Тон — доброзичливий, як від друга, що живе у Валенсії. Не починай з "Привіт"."""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
