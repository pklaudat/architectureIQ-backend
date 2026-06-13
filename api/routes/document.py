from uuid import uuid4
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from typing import Annotated, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi import UploadFile
from fastapi import File

from api.models.document import *
from api.services.blob_storage import BlobStorageService
from api.services.cosmos_db import CosmosDbService
from api.services.publisher import ServiceBusQueuePublisher
from config import settings


document = CosmosDbService(container_name="Documents")
projects = CosmosDbService(container_name="Projects")
queue = ServiceBusQueuePublisher()
storage = BlobStorageService(container_name="architecture-documents")

router = APIRouter()


async def get_project(project_id: str):
    project = await projects.get_item(item_id=project_id, partition_key=project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project doesn't exist")
    
    return project

ProjectDependency = Annotated[dict, Depends(get_project)]


@router.post("/project/{project_id}/documents", response_model=UploadResponse)
async def upload_document(project: ProjectDependency, file: UploadFile = File(...)):


    document_id = str(uuid4())

    extension = file.filename.split(".")[-1]

    blob_name = f"{project["id"]}/{document_id}/{file.filename}"

    content = await file.read()

    blob_url = await storage.upload_file(
        blob_name=blob_name,
        content=content,
        content_type=file.content_type,
    )

    upload_response = UploadResponse(
        document_id=document_id, file_name=file.filename, blob_url=blob_url
    )

    await document.create_item(
        Document(
            id=document_id,
            blob_url=blob_url,
            file_name=file.filename,
            file_format=FileFormat(extension.upper()),
            file_type=FileType.ARCHITECTURE_DEFINITION,
            project_id=project["id"],
            status=DocumentStatus.PENDING,
        ).model_dump()
    )

    await queue.publish(
        payload=upload_response.model_dump(),
    )

    # except Exception as e:
    #     try:
    #         await db.delete_item(partition_key=document_id, item_id=document_id)
    #     finally:
    #         raise HTTPException(status_code=500, detail="Failed to process document")

    return UploadResponse(
        document_id=document_id, file_name=file.filename, blob_url=blob_url
    )


@router.get("/project/{project_id}/document", response_model=List[Document])
async def get_documents(project: ProjectDependency):
    
    documents = await document.query_items(query=f"""
            SELECT *
            FROM c
            WHERE c.project_id = @project_id""",
            parameters=[{
                "name": "@project_id",
                "value": project["id"]
            }]
    )

    return documents 


@router.post("/project/{project_id}/document/{document_id}/review")
async def create_review(project: ProjectDependency, document_id: str):
    # submit a message in a queue - so the review can be processed later
    pass
