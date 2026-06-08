from api.services.cosmos_db import CosmosDbService
from api.services.blob_storage import BlobStorageService
from api.services.consumer import ServiceBusQueueConsumer
from orchestration.workflow import workflow
from api.models.document import Document, FileFormat, DocumentStatus

w = workflow()

db = CosmosDbService(container_name="Documents")
reviews = CosmosDbService(container_name="Reviews")
blob = BlobStorageService(container_name="architecture-documents")


class DocumentProcessing(ServiceBusQueueConsumer):

    async def call_agentic_system(
        self, project_id: str, document_id: str, document_content: str
    ):

        async for event in w.run(document_content):
            if event.type == "executor_started" and event.executor_id == "":
                pass

    async def pre_content_analyzis(self, document: Document):
        """Review the uploaded content and determine label the file with its content type"""
        print("Pre Content Analyzis step")

    async def content_extraction(self, document: Document):
        """Call content understanding API to extract content from pdf, png and other formats"""
        print("Running Content Extraction")
        content = ""

        if document.file_format == FileFormat.TXT:
            print("TXT File detected.")
            content = await blob.read_text(
                blob_name="/".join(document.blob_url.replace("https://", "").split("/")[2:]),
            )
            print(content)

        await db.patch_item(
            item_id=document.id,
            partition_key=document.id,
            operations=[{
                "op": "replace",
                "path": "/status",
                "value": DocumentStatus.CONTENT_EXTRACTED.value
            }]
        )

        return content

    async def process_message(self, payload: dict):

        print(f"processing message: {payload}")

        try:
            item = await db.get_item(
                item_id=payload["document_id"], partition_key=payload["document_id"]
            )

            response = await db.patch_item(
                item["id"],
                partition_key=item["id"],
                operations=[{
                    "op": "replace",
                    "path": "/status",
                    "value": DocumentStatus.PROCESSING.value
                }],
            )  

            if response["status"] != DocumentStatus.PROCESSING.value:
                raise Exception("Document status could not be updated.")

            doc = Document(**response)

            print(f"document validation {doc.model_dump()}")

            doc_label = await self.pre_content_analyzis(doc)

            content = await self.content_extraction(doc)

            print(f"Content extracted successfully for {doc}")

        except Exception as e:
            print(e)
