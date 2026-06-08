from uuid import uuid4
import datetime
from api.models.project import *
from api.services.cosmos_db import CosmosDbService
from fastapi import APIRouter, HTTPException
from fastapi import UploadFile
from fastapi import File

router = APIRouter()
cosmos = CosmosDbService(container_name="Projects")


@router.post("/project", response_model=ProjectCreateResponse)
async def create_project(project_name: str):

    project_id = str(uuid4())
    try:
        project = Project(
            id=project_id,
            display_name=project_name,
            created_at=str(datetime.datetime.now()),
            author_email="paulo@earewvier.com",
            author_name="Paulo",
        )

        response = await cosmos.create_item(project.model_dump())
    except Exception as e:
        print(e)
        breakpoint()
        raise HTTPException(status_code=500, detail=e)

    return response


@router.get("/project/{project_id}", response_model=Project)
async def get_project_details(project_id: str):
    response = await cosmos.get_item(item_id=project_id, partition_key=project_id)

    return response


# @router.delete("/project/{project_id}")
# async def delete_project(project_id: str):
#     await cosmos.delete_item(item_id=project_id, partition_key=project_id)


@router.post("/project/{project_id}/review")
async def create_project_review():
    pass
