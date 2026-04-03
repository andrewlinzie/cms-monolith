from fastapi import APIRouter
from src.models.schemas import HealthResponse
from src.config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service=settings.APP_NAME)