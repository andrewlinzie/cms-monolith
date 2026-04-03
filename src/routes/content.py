from fastapi import APIRouter
from src.models.schemas import ContentItem
from src.services.content_service import list_content, create_content

router = APIRouter(prefix="/admin/content", tags=["content"])


@router.get("", response_model=list[ContentItem])
def get_content():
    return list_content()


@router.post("", response_model=ContentItem)
def post_content(content: ContentItem):
    return create_content(content)