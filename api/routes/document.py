from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi import UploadFile
from fastapi import File

from api.models.document import *
from api.services.blob_storage import BlobStorageService
from api.services.cosmos_db import CosmosDbService
from api.services.publisher import ServiceBusQueuePublisher

router = APIRouter()


db = CosmosDbService(container_name="Documents")
queue = ServiceBusQueuePublisher(queue_name="document-processing")
storage = BlobStorageService(container_name="architecture-documents")


@router.post("/project/{project_id}/documents", response_model=UploadResponse)
async def upload_document(project_id: str, file: UploadFile = File(...)):

    document_id = str(uuid4())

    extension = file.filename.split(".")[-1]

    blob_name = f"{project_id}/{document_id}/source.{extension}"

    content = await file.read()

    blob_url = await storage.upload_file(
        blob_name=blob_name, content=content, content_type=file.content_type,
    )

    upload_response = UploadResponse(
        document_id=document_id, file_name=file.filename, blob_url=blob_url
    )

    await db.create_item(
        Document(
            id=document_id,
            blob_url=blob_url,
            file_name=f"source.{extension}",
            file_format=FileFormat(extension.upper()),
            file_type=FileType.ARCHITECTURE_DEFINITION,
            project_id=project_id,
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


@router.get("/project/{project_id}/document")
async def get_documents(project_id: str):
    return await db.query_items(query="")


@router.post("/project/{project_id}/document/{document_id}/review")
async def create_review(project_id: str, document_id: str):
    # submit a message in a queue - so the review can be processed later
    pass
