from uuid import uuid4
from typing import List
from api.models.project import *
from api.models.summaries import ProjectSummary
from api.services.cosmos_db import CosmosDbService
from api.services import store
from fastapi import APIRouter, HTTPException

router = APIRouter()
cosmos = CosmosDbService(container_name="Projects")


@router.post("/project", response_model=ProjectCreateResponse)
async def create_project(project_name: str, description: str = ""):

    project_id = str(uuid4())
    try:
        project = Project(
            id=project_id,
            display_name=project_name,
            description=description,
            author_email="paulo@earewvier.com",
            author_name="Paulo",
        )

        response = await cosmos.create_item(project.model_dump())
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    return response


@router.get("/projects", response_model=List[ProjectSummary])
async def list_projects():
    """All projects, enriched with document counts, scores and finding tallies."""
    projects = await store.fetch_all_projects()
    documents = await store.fetch_all_documents()
    reviews = await store.fetch_all_reviews()

    docs_by_project = store.group_by(documents, "project_id")
    revs_by_project = store.group_by(reviews, "project_id")

    return [
        store.map_project(
            p,
            docs_by_project.get(p.get("id"), []),
            revs_by_project.get(p.get("id"), []),
        )
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ProjectSummary)
async def get_project_summary(project_id: str):
    """A single project, enriched the same way as the list endpoint."""
    project = await cosmos.get_item(item_id=project_id, partition_key=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project doesn't exist")

    documents = await store.documents_for_project(project_id)
    reviews = await store.reviews_for_project(project_id)
    return store.map_project(project, documents, reviews)


@router.get("/project/{project_id}", response_model=Project)
async def get_project_details(project_id: str):
    response = await cosmos.get_item(item_id=project_id, partition_key=project_id)

    return response


@router.post("/project/{project_id}/review")
async def create_project_review():
    pass
