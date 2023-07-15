

from fastapi import APIRouter, Depends
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
# from settings.app import AppSettings
# from config import get_app_settings


from schemas.translation import (
    TranslationInRequest,
    TranslationForResponse
)

router = APIRouter()

@router.post("/translator", response_model=TranslationForResponse, name="tools:translation")
async def portal(
    article: TranslationInRequest,
    # settings: AppSettings = Depends(get_app_settings),
) -> TranslationForResponse:
    
    return TranslationForResponse(
        result=article.src,
    )