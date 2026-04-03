from src.data.seed_data import resources
from src.models.schemas import ResourceItem


def list_resources():
    return resources


def create_resource(resource: ResourceItem):
    resources.append(resource.model_dump())
    return resource