from fastapi import APIRouter, Form, Query, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional

from config import BUSINESS_STYLES, INDUSTRY_KEYWORDS
from services.logo_service import generate_logo_description, generate_svg_logo
from services.llm_service import refine_logo_concept

router = APIRouter()


@router.get("/")
async def index() -> FileResponse:
    return FileResponse("static/index.html")


@router.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "available_styles": list(BUSINESS_STYLES.keys()),
        "available_industries": list(INDUSTRY_KEYWORDS.keys())
    })


@router.get("/styles")
async def get_styles() -> JSONResponse:
    """Get available logo styles"""
    return JSONResponse({
        "styles": BUSINESS_STYLES
    })


@router.get("/industries")
async def get_industries() -> JSONResponse:
    """Get available industry categories"""
    return JSONResponse({
        "industries": list(INDUSTRY_KEYWORDS.keys())
    })


@router.post("/generate")
async def generate_logo(
    business_name: str = Form(...),
    industry: str = Form(...),
    style: str = Form(...),
    slogan: Optional[str] = Form(None),
    additional_info: Optional[str] = Form(None)
) -> JSONResponse:
    """
    Generate a logo based on business information
    """
    if style not in BUSINESS_STYLES:
        raise HTTPException(status_code=400, detail=f"Неизвестный стиль: {style}")
    
    if industry not in INDUSTRY_KEYWORDS:
        raise HTTPException(status_code=400, detail=f"Неизвестная индустрия: {industry}")
    
    try:
        # Generate logo description using AI
        logo_desc = await generate_logo_description(
            business_name=business_name,
            industry=industry,
            style=style,
            slogan=slogan,
            additional_info=additional_info
        )
        
        # Generate SVG logo
        svg_code = await generate_svg_logo(
            business_name=business_name,
            industry=industry,
            style_style=style,
            logo_description=logo_desc,
            slogan=slogan
        )
        
        return JSONResponse({
            "status": "success",
            "logo": {
                "svg": svg_code,
                "description": logo_desc,
                "business_name": business_name,
                "style": style,
                "industry": industry
            }
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@router.post("/refine")
async def refine_logo(
    current_svg: str = Form(...),
    feedback: str = Form(...)
) -> JSONResponse:
    """
    Refine existing logo based on feedback
    """
    try:
        refined_svg = await refine_logo_concept(current_svg, feedback)
        return JSONResponse({
            "status": "success",
            "svg": refined_svg
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка доработки: {str(e)}")


@router.get("/export/{format}")
async def export_logo(
    svg: str = Query(...),
    format: str = "svg"
) -> FileResponse:
    """
    Export logo in different formats (coming soon)
    """
    # For now, just return SVG
    if format != "svg":
        raise HTTPException(status_code=501, detail="Формат пока не поддерживается")
    
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False)
    temp_file.write(svg)
    temp_file.close()
    
    return FileResponse(
        path=temp_file.name,
        filename="logo.svg",
        media_type="image/svg+xml"
    )