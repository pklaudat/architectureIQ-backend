from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from orchestration.agents.state import (
    Finding,
    ReviewStatus,
    RecommendationEntity,
    CuratedReport,
    ArchitectureFacts
)

class Review(BaseModel):
    id: str
    project_id: str
    document_id: Optional[str]
    score: Optional[int] = Field(default=None)
    facts: List[ArchitectureFacts] = Field(default=[])
    findings: Optional[List[Finding]] = Field(default=[])
    recommendations: Optional[List[RecommendationEntity]] = Field(default=[])
    report: Optional[CuratedReport] = Field(default=None) 
    completed_at: Optional[str] = Field(default=None)
    status: ReviewStatus = Field(default=ReviewStatus.in_progress)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
