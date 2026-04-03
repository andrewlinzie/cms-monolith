from fastapi import APIRouter
from src.models.schemas import AdminResponse
from src.config.settings import settings

router = APIRouter()


@router.get("/admin", response_model=AdminResponse)
def admin_root():
    return AdminResponse(
        service=settings.APP_NAME,
        domains=["exercises", "content", "resources"],
        status="ready",
    )