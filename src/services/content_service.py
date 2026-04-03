from src.data.seed_data import content_items
from src.models.schemas import ContentItem


def list_content():
    return content_items


def create_content(content: ContentItem):
    content_items.append(content.model_dump())
    return content