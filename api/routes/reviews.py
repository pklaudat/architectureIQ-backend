from uuid import uuid4
from fastapi import APIRouter
from api.services.publisher import ServiceBusQueuePublisher
from api.utils.dependencies import ProjectDependency, DocumentDependency
from api.models.review import Review

router = APIRouter(tags=["reviews"])


queue = ServiceBusQueuePublisher(queue_name="reviews-processing")


@router.post("/project/{project_id}/document/{document_id}/review")
async def create_review(project: ProjectDependency, document: DocumentDependency):
    review_id = str(uuid4())

    review = Review(id=review_id, project_id=project["id"], document_id=document["id"])

    await queue.publish(
        payload=review.model_dump(),
    )
