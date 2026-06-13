from typing import Annotated
from fastapi import HTTPException, Depends
from api.services.cosmos_db import CosmosDbService

documents_container = CosmosDbService(container_name="Documents")
projects_container = CosmosDbService(container_name="Projects")


async def get_item(item_id: str, container: CosmosDbService, label: str):
    item = await container.get_item(item_id=item_id, partition_key=item_id)

    if not item:
        raise HTTPException(status_code=404, detail=f"{label} doesn't exist")

    return item


async def get_project(project_id: str):
    project = await get_item(project_id, projects_container, "Project")
    return project


async def get_document(document_id: str):
    document = await get_item(document_id, documents_container, "Document")
    return document


ProjectDependency = Annotated[dict, Depends(get_project)]
DocumentDependency = Annotated[dict, Depends(get_document)]
