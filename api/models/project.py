from datetime import datetime
from pydantic import BaseModel, Field


class ProjectCreateResponse(BaseModel):
    id: str
    display_name: str
    author_name: str
    author_email: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Project(BaseModel):
    id: str
    display_name: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    author_name: str
    author_email: str
    model_config = {"populate_by_name": True}
