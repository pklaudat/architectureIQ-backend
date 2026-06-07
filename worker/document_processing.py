from api.services.cosmos_db import CosmosDbService
from api.services.blob_storage import BlobStorageService
from api.services.consumer import ServiceBusQueueConsumer
from orchestration.workflow import workflow
from api.models.document import Document, FileFormat

w = workflow()

document = CosmosDbService(container_name="Documents")
reviews = CosmosDbService(container_name="Reviews")
blob = BlobStorageService(container_name="architecture-documents")


class DocumentProcessing(ServiceBusQueueConsumer):

    async def call_agentic_system(
        project_id: str, document_id: str, document_content: str
    ):

        async for event in w.run(document_content):
            if event.type == "executor_started" and event.executor_id == "":
                pass

    async def pre_content_analyzis(document: Document):
        """Review the uploaded content and determine label the file with its content type"""
        pass

    async def content_extraction(document: Document):
        """Call content understanding API to extract content from pdf, png and other formats"""

        content = ""

        if document.file_format == FileFormat.TXT:
            content = await blob.read_text(
                blob_name=f"{document.id}/{document.file_name}",
            )

        return content

    async def process_message(self, payload: dict):

        doc = Document.model_validate(
            document.get_item(
                item_id=payload["document_id"], partition_key=payload["document_id"]
            )
        )

        doc_label = await self.pre_content_analyzis(doc)

        content = await self.content_extraction(doc)

        # await self.call_agentic_system(content=content)
