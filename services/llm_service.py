import httpx
import re
from fastapi import HTTPException

from config import OLLAMA_URL, MODEL_NAME


async def refine_logo_concept(current_svg: str, feedback: str) -> str:
    """Refine logo based on user feedback"""
    
    system_prompt = """Ты дизайнер логотипов. Модифицируй SVG код согласно отзыву клиента.
    Сохраняй общую концепцию, но вноси правки.
    Возвращай ТОЛЬКО валидный SVG код."""
    
    user_prompt = f"""
    Текущий SVG логотип:
    {current_svg[:1500]}
    
    Отзыв клиента: {feedback}
    
    Внеси правки и верни улучшенную версию.
    """
    
    payload = {
        "model": MODEL_NAME,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            svg_code = data.get("message", {}).get("content", current_svg)
            
            # Extract SVG
            svg_match = re.search(r'```svg\n(.*?)\n```', svg_code, re.DOTALL)
            if svg_match:
                svg_code = svg_match.group(1)
            
            return svg_code
    except Exception as e:
        return current_svg