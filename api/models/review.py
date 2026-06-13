from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from orchestration.agents.state import CuratedReport, ReviewStatus

from enum import Enum


class Review(BaseModel):
    id: str
    project_id: str
    document_id: Optional[str]
    content: Optional[CuratedReport] = None
    completed_at: Optional[str] = None
    status: ReviewStatus = Field(default=ReviewStatus.in_progress)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
