from typing import List
from fastapi import APIRouter
from api.models.summaries import FindingSummary
from api.services import store

router = APIRouter(tags=["findings"])


@router.get("/findings", response_model=List[FindingSummary])
async def list_findings():
    """Flattens every finding out of every review across all projects."""
    reviews = await store.fetch_all_reviews()
    all_projects = await store.fetch_all_projects()
    proj_name = {p.get("id"): p.get("display_name", "") for p in all_projects}

    return store.map_findings(reviews, proj_name)
