from fastapi import APIRouter
from src.models.schemas import ResourceItem
from src.services.resource_service import list_resources, create_resource

router = APIRouter(prefix="/admin/resources", tags=["resources"])


@router.get("", response_model=list[ResourceItem])
def get_resources():
    return list_resources()


@router.post("", response_model=ResourceItem)
def post_resource(resource: ResourceItem):
    return create_resource(resource)