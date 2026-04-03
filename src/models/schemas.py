from pydantic import BaseModel
from typing import Literal


class HealthResponse(BaseModel):
    status: str
    service: str


class AdminResponse(BaseModel):
    service: str
    domains: list[str]
    status: str


class Exercise(BaseModel):
    id: str
    title: str
    category: str
    status: Literal["draft", "published"]


class ContentItem(BaseModel):
    id: str
    title: str
    content_type: str
    status: Literal["draft", "published"]


class ResourceItem(BaseModel):
    id: str
    title: str
    resource_type: str
    status: Literal["draft", "published"]