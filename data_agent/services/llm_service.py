import httpx
import pandas as pd
from fastapi import HTTPException

from config import MODEL_NAME, OLLAMA_URL


def _build_prompts(df: pd.DataFrame, question: str) -> tuple[str, str]:
    sample = df.head(40).fillna("").to_markdown(index=False)
    profile_lines = []
    for col in df.columns[:30]:
        series = df[col]
        profile_lines.append(
            f"- {col}: dtype={series.dtype}, nulls={int(series.isna().sum())}, unique={int(series.nunique(dropna=True))}"
        )
    system_prompt = (
        "Ты AI-аналитик данных для начинающих разработчиков. "
        "Работай только с предоставленным sample и профилем. "
        "Если данных недостаточно для уверенного вывода - скажи это явно. "
        "Ответ давай по-русски, структурированно: вывод, обоснование, что проверить дополнительно."
    )
    user_prompt = (
        f"Профиль колонок:\n{chr(10).join(profile_lines)}\n\n"
        f"Пример данных:\n{sample}\n\n"
        f"Вопрос пользователя: {question}"
    )
    return system_prompt, user_prompt


async def ask_insight(df: pd.DataFrame, question: str) -> dict[str, str]:
    system_prompt, user_prompt = _build_prompts(df, question)
    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ошибка обращения к LLM: {str(exc)}") from exc

    answer = data.get("message", {}).get("content", "").strip()
    if not answer:
        raise HTTPException(status_code=500, detail="Модель не вернула ответ.")
    return {"model": MODEL_NAME, "answer": answer}
