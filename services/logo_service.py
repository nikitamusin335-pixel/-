import httpx
import random
import re
from typing import Optional
from fastapi import HTTPException

from config import OLLAMA_URL, MODEL_NAME, BUSINESS_STYLES, INDUSTRY_KEYWORDS


async def generate_logo_description(
    business_name: str,
    industry: str,
    style: str,
    slogan: Optional[str] = None,
    additional_info: Optional[str] = None
) -> str:
    """Generate creative logo description using LLM"""
    
    style_info = BUSINESS_STYLES.get(style, {})
    keywords = INDUSTRY_KEYWORDS.get(industry, [])
    
    system_prompt = """Ты профессиональный дизайнер логотипов с 20-летним опытом. 
    Создавай подробные, визуальные описания логотипов, которые можно реализовать в SVG.
    Используй конкретные геометрические формы, цвета и композиции.
    Описание должно быть на русском языке, точным и практичным для отрисовки."""
    
    user_prompt = f"""
    Создай подробное описание логотипа для компании:
    
    НАЗВАНИЕ: {business_name}
    ИНДУСТРИЯ: {industry}
    СТИЛЬ: {style} - {style_info.get('description', '')}
    СЛОГАН: {slogan if slogan else 'Нет'}
    ДОП. ИНФО: {additional_info if additional_info else 'Нет'}
    
    Ключевые слова для вдохновения: {', '.join(keywords[:5])}
    
    Цветовая палитра стиля: {', '.join(style_info.get('colors', ['#000000']))}
    Рекомендуемые формы: {', '.join(style_info.get('shapes', []))}
    
    Опиши логотип в следующем формате:
    1. Основная форма и композиция
    2. Цветовое решение (используй HEX коды)
    3. Элементы и символы
    4. Шрифт (если есть текст)
    5. Общее настроение
    
    Будь конкретен: "золотой треугольник 120px высотой" вместо "красивый элемент".
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
            return data.get("message", {}).get("content", "Креативный современный логотип")
    except Exception as e:
        # Fallback to template-based generation
        return generate_fallback_description(business_name, industry, style, style_info, keywords)


def generate_fallback_description(business_name: str, industry: str, style: str, style_info: dict, keywords: list) -> str:
    """Fallback logo description generator"""
    colors = style_info.get('colors', ['#2C3E50', '#3498DB'])
    shapes = style_info.get('shapes', ['circle', 'square'])
    
    shape = random.choice(shapes)
    primary_color = colors[0]
    secondary_color = colors[1] if len(colors) > 1 else colors[0]
    
    descriptions = {
        "modern_tech": f"Геометрический логотип в форме {shape}, собранный из фрагментов как пазл. Основной цвет {primary_color}, акцент {secondary_color}. Символизирует инновации и технологии.",
        "luxury_premium": f"Элегантный {shape} с золотым ободком ({secondary_color}) на темном фоне ({primary_color})." + (" Изысканная монограмма названия." if business_name else ""),
        "creative_art": f"Абстрактная композиция из {shape} и волнообразных линий. Яркие цвета: {primary_color} и {secondary_color}. Ощущение свободы и творчества.",
        "eco_nature": f"Органичная форма {shape}, напоминающая лист или дерево. Зеленые оттенки от {primary_color} до {secondary_color}. Природная гармония.",
        "corporate_business": f"Строгий {shape} в деловом стиле. Синий цвет {primary_color} символизирует надежность. Четкие линии, профессиональный вид.",
        "startup_energetic": f"Динамичный {shape} с градиентом от {primary_color} к {secondary_color}. Энергия, движение, инновационный подход."
    }
    
    return descriptions.get(style, descriptions["modern_tech"])


async def generate_svg_logo(
    business_name: str,
    industry: str,
    style_style: str,
    logo_description: str,
    slogan: Optional[str] = None
) -> str:
    """Generate SVG code based on description"""
    
    system_prompt = """Ты эксперт по SVG. Создавай валидный, красивый SVG код для логотипов.
    Используй viewBox="0 0 500 500".
    Код должен быть самодостаточным, с правильными тегами.
    Добавь градиенты, тени для профессионального вида.
    Не используй внешние шрифты, только стандартные.
    Ответ должен содержать ТОЛЬКО SVG код, без пояснений."""
    
    user_prompt = f"""
    Создай SVG логотип по описанию:
    
    {logo_description}
    
    НАЗВАНИЕ: {business_name}
    ИНДУСТРИЯ: {industry}
    СТИЛЬ: {style_style}
    {f"СЛОГАН: {slogan}" if slogan else ""}
    
    Требования:
    - Размер: 500x500px
    - Используй градиенты
    - Добавь легкую тень или свечение
    - Текст должен быть хорошо читаем
    - Код должен быть валидным SVG
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
            svg_code = data.get("message", {}).get("content", "")
            
            # Extract SVG from markdown if needed
            svg_match = re.search(r'```svg\n(.*?)\n```', svg_code, re.DOTALL)
            if svg_match:
                svg_code = svg_match.group(1)
            elif not svg_code.strip().startswith('<svg'):
                svg_code = generate_fallback_svg(business_name, style_style)
            
            return svg_code
    except Exception as e:
        return generate_fallback_svg(business_name, style_style)


def generate_fallback_svg(business_name: str, style: str) -> str:
    """Generate fallback SVG logo"""
    colors = {
        "modern_tech": {"primary": "#3498DB", "secondary": "#2C3E50"},
        "luxury_premium": {"primary": "#D4AF37", "secondary": "#1A1A1A"},
        "creative_art": {"primary": "#FF6B35", "secondary": "#FFD166"},
        "eco_nature": {"primary": "#2D6A4F", "secondary": "#52B788"},
        "corporate_business": {"primary": "#003B6F", "secondary": "#0F4C81"},
        "startup_energetic": {"primary": "#4158D0", "secondary": "#C850C0"}
    }
    
    pal = colors.get(style, colors["modern_tech"])
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{pal['primary']};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{pal['secondary']};stop-opacity:1" />
        </linearGradient>
        <filter id="shadow">
            <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.3"/>
        </filter>
    </defs>
    
    <rect width="500" height="500" fill="#f8f9fa" rx="20"/>
    
    <g transform="translate(250, 220)" filter="url(#shadow)">
        <circle cx="0" cy="0" r="80" fill="url(#grad)" opacity="0.9"/>
        <text x="0" y="10" text-anchor="middle" fill="white" font-size="48" font-weight="bold" font-family="Arial, sans-serif">
            {business_name[0].upper() if business_name else 'L'}
        </text>
    </g>
    
    <text x="250" y="330" text-anchor="middle" fill="{pal['secondary']}" font-size="24" font-weight="bold" font-family="Arial, sans-serif">
        {business_name[:20]}
    </text>
    
    {f'<text x="250" y="360" text-anchor="middle" fill="#666" font-size="14" font-family="Arial, sans-serif">•••</text>' if style != "corporate_business" else ''}
</svg>'''