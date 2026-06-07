from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from orchestration.agents.state import CuratedReport, ReviewStatus

from enum import Enum

# class ReviewStatus(str, Enum):
#     uploaded = "uploaded"
#     content_extracted = "content_extracted"
#     facts_extracted = "facts_extracted"
#     ea_review_complete = "ea_review_complete"
#     iq_review_complete = "iq_review_complete"
#     aggregated = "aggregated"
#     curated = "curated"
#     completed = "completed"


class Review(BaseModel):
    id: str
    project_id: str
    content: Optional[CuratedReport]
    status: ReviewStatus
