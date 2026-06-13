from fastapi import APIRouter
from api.models.summaries import Analytics
from api.services import store

router = APIRouter(tags=["analytics"])


@router.get("/analytics", response_model=Analytics)
async def get_analytics():
    """Aggregate metrics, trends and a project leaderboard for the Analytics page."""
    projects = await store.fetch_all_projects()
    documents = await store.fetch_all_documents()
    reviews = await store.fetch_all_reviews()

    return store.build_analytics(projects, documents, reviews)
