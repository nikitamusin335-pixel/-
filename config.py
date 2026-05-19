import os
from pathlib import Path

# LLM Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:4b")

# Storage
LOGO_STORAGE_DIR = Path(os.getenv("LOGO_STORAGE_DIR", "generated_logos"))
LOGO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Business style presets
BUSINESS_STYLES = {
    "modern_tech": {
        "name": "Modern Tech",
        "description": "Минимализм, геометрия, холодные тона",
        "colors": ["#2C3E50", "#3498DB", "#1ABC9C"],
        "shapes": ["hexagon", "triangle", "circle"]
    },
    "luxury_premium": {
        "name": "Luxury Premium",
        "description": "Элегантность, золото, черный, классика",
        "colors": ["#1A1A1A", "#D4AF37", "#8B7355"],
        "shapes": ["shield", "diamond", "emblem"]
    },
    "creative_art": {
        "name": "Creative Art",
        "description": "Яркий, нестандартный, арт-хаус",
        "colors": ["#FF6B35", "#FFD166", "#06D6A0"],
        "shapes": ["splash", "wave", "abstract"]
    },
    "eco_nature": {
        "name": "Eco & Nature",
        "description": "Зеленый, органический, экологичный",
        "colors": ["#2D6A4F", "#40916C", "#52B788"],
        "shapes": ["leaf", "tree", "circle"]
    },
    "corporate_business": {
        "name": "Corporate Business",
        "description": "Строгий, надежный, синий",
        "colors": ["#003B6F", "#0F4C81", "#2C5F8A"],
        "shapes": ["square", "rectangle", "letter"]
    },
    "startup_energetic": {
        "name": "Startup Energetic",
        "description": "Дерзкий, модный, градиенты",
        "colors": ["#4158D0", "#C850C0", "#FFCC70"],
        "shapes": ["bolt", "spark", "dynamic"]
    }
}

# Industry keywords for better generation
INDUSTRY_KEYWORDS = {
    "tech": ["software", "hardware", "coding", "digital", "AI", "cloud", "data", "cyber"],
    "finance": ["money", "growth", "chart", "secure", "bank", "investment", "wealth"],
    "food": ["organic", "fresh", "restaurant", "cafe", "delicious", "natural"],
    "fashion": ["style", "design", "trendy", "elegant", "wearable", "luxury"],
    "health": ["wellness", "medical", "fitness", "vitality", "care", "life"],
    "education": ["learning", "knowledge", "book", "graduation", "academic"],
    "real_estate": ["home", "building", "construction", "property", "architecture"],
    "art": ["creative", "design", "studio", "gallery", "handmade", "unique"]
}