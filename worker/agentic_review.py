from datetime import datetime
from orchestration.agents.state import StateMap
from api.services.blob_storage import BlobStorageService
from api.services.consumer import ServiceBusQueueConsumer
from api.services.cosmos_db import CosmosDbService
from orchestration.workflow import review_workflow

doc = CosmosDbService("Documents")
reviews = CosmosDbService("Reviews")
blob = BlobStorageService(container_name="architecture-documents")


class AgenticReview(ServiceBusQueueConsumer):

    async def update_status(self, review_id: str, status: str):
        await reviews.patch_item(
            partition_key=review_id,
            item_id=review_id,
            operations=[{"op": "replace", "path": "/status", "value": status}],
        )

        print(f"Updated review {review_id} status with {status}")

    async def execute(self, review_id: str, document_content: str):
        w = review_workflow()

        async for event in w.run(document_content, stream=True):

            if event.type == "executor_completed":
                print(f"A step in workflow has been completed {event.executor_id}")
                status = StateMap.__members__[event.executor_id].value

                await self.update_status(review_id, status)

                print(
                    f"Updated status in review container - {status}"
                )

            elif event == "superstep_completed":
                print(f"Agentic Workflow for {review_id} completed")

                await reviews.patch_item(
                    item_id=review_id,
                    partition_key=review_id,
                    operations=[
                        {"op": "replace", "path": "/content", "value": ""},
                        {"op": "replace", "path": "/status", "value": "completed"},
                        {
                            "op": "replace",
                            "path": "/completed_at",
                            "value": datetime.now().isoformat(),
                        },
                    ],
                )

                breakpoint()

                print(f"Successfully persisted the memory for {review_id}")

    async def process_message(self, payload: dict):
        print(f"Review started for {payload["id"]}")
        try:
            review = await reviews.get_item(
                item_id=payload["id"], partition_key=payload["id"]
            )

            print(f"review item being processed: {review['id']}")

            document = await doc.get_item(
                item_id=review["document_id"], partition_key=review["document_id"]
            )

            content = await blob.read_text(
                blob_name="/".join(
                    document["blob_url"].replace("https://", "").split("/")[2:]
                ),
            )

            print(f"retrieved document content for {payload["id"]}")

            await self.execute(review["id"], content)
        except Exception as e:
            print(e)
            raise Exception
