import logging

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openrouter", tags=["openrouter"])


@router.get("/key")
def check_openrouter_key(
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    api_key = settings.open_router_api_key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENROUTER_API_KEY is not configured.",
        )

    try:
        response = requests.get(
            url="https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=20,
        )
    except requests.RequestException as exc:
        logger.exception("OpenRouter key check request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to reach OpenRouter key endpoint.",
        ) from exc

    payload = response.json() if response.content else {}
    return JSONResponse(status_code=response.status_code, content=payload)