import datetime
from typing import Optional
from pydantic import BaseModel, Field
from orchestration.agents.state import CuratedReport, ReviewStatus


class ProjectCreateResponse(BaseModel):
    id: str
    display_name: str
    author_name: str
    author_email: str
    created_at: str


class Project(BaseModel):
    id: str
    display_name: str
    created_at: str
    author_name: str
    author_email: str
    model_config = {"populate_by_name": True}
