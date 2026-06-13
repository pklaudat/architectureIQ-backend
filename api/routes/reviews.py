from uuid import uuid4
from typing import List
from fastapi import APIRouter
from api.services.publisher import ServiceBusQueuePublisher
from api.services.cosmos_db import CosmosDbService
from api.utils.dependencies import ProjectDependency, DocumentDependency
from api.models.review import Review
from api.models.summaries import ReviewSummary
from api.services import store

router = APIRouter(tags=["reviews"])


queue = ServiceBusQueuePublisher(queue_name="reviews-processing")
reviews_container = CosmosDbService(container_name="Reviews")


@router.post("/project/{project_id}/document/{document_id}/review", response_model=Review)
async def create_review(project: ProjectDependency, document: DocumentDependency):
    review_id = str(uuid4())

    review = Review(id=review_id, project_id=project["id"], document_id=document["id"])

    # Persist first so the review is queryable immediately, then hand it to the worker.
    await reviews_container.create_item(review.model_dump())

    await queue.publish(
        payload=review.model_dump(),
    )

    return review


@router.get("/reviews", response_model=List[ReviewSummary])
async def list_reviews():
    """All reviews across projects, joined with document + project names."""
    reviews = await store.fetch_all_reviews()
    documents = await store.fetch_all_documents()
    all_projects = await store.fetch_all_projects()

    doc_name = {d.get("id"): d.get("file_name") for d in documents}
    proj_name = {p.get("id"): p.get("display_name") for p in all_projects}

    return [
        store.map_review(r, doc_name.get(r.get("document_id")), proj_name.get(r.get("project_id")))
        for r in reviews
    ]
