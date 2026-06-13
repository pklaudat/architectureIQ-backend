from uuid import uuid4
from datetime import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File
from api.utils.dependencies import ProjectDependency
from api.models.document import *
from api.services.blob_storage import BlobStorageService
from api.services.cosmos_db import CosmosDbService
from api.services.publisher import ServiceBusQueuePublisher

document = CosmosDbService(container_name="Documents")
projects = CosmosDbService(container_name="Projects")
queue = ServiceBusQueuePublisher("document-processing")
storage = BlobStorageService(container_name="architecture-documents")

router = APIRouter()


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

    return UploadResponse(
        document_id=document_id, file_name=file.filename, blob_url=blob_url
    )


@router.get("/project/{project_id}/document", response_model=List[Document])
async def get_documents(project: ProjectDependency):

    documents = await document.query_items(
        query=f"""
            SELECT *
            FROM c
            WHERE c.project_id = @project_id""",
        parameters=[{"name": "@project_id", "value": project["id"]}],
    )

    return documents
