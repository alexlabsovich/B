import httpx

import config


async def generate_post(prompt: str) -> str:
    """Отправляет запрос в OpenRouter (модель inclusionai/ling-3.0-flash-fin:free)."""
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.OPENROUTER_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — помощник по созданию контента для Telegram-канала. "
                    "Пиши готовый пост на русском языке, без лишних пояснений от себя "
                    "и без markdown-заголовков, если это не требуется явно."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"].strip()
