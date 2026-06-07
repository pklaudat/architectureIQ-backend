from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# --------------------------
# Architecture Facts
# --------------------------
class Authentication(BaseModel):
    provider: Optional[str] = None
    protocol: Optional[str] = None
    confidence: float = 0.0


class Availability(BaseModel):
    rto: Optional[str] = None
    rpo: Optional[str] = None
    multi_region: bool = False


class Technology(BaseModel):
    databases: list[str] = Field(default_factory=list)
    runtimes: list[str] = Field(default_factory=list)
    cloud_services: list[str] = Field(default_factory=list)


class ArchitectureFacts(BaseModel):
    system_name: Optional[str] = None
    stakeholders: list[str] = Field(default_factory=list)
    authentication: Optional[Authentication] = None
    availability: Optional[Availability] = None
    technology: Optional[Technology] = None
    missing_information: list[str] = Field(default_factory=list)


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class ArchitectureArea(str, Enum):
    authentication = "authentication"
    high_availability = "high_availability"
    disaster_recovery = "disaster_recovery"
    security = "security"
    operations = "operations"
    technology = "technology"
    governance = "governance"


class Evidence(BaseModel):
    area: ArchitectureArea
    fact_name: str
    value: str
    source_section: Optional[str] = None
    confidence: float = 1.0


class Finding(BaseModel):
    severity: Severity
    area: ArchitectureArea
    title: str
    message: str
    recommendation: Optional[str] = None


class RecommendationEntity(BaseModel):
    title: str
    content: str
    references: list[str] = Field(default_factory=list)


class ReviewStatus(str, Enum):
    uploaded = "uploaded"
    content_extracted = "content_extracted"
    facts_extracted = "facts_extracted"
    ea_review_complete = "ea_review_complete"
    iq_review_complete = "iq_review_complete"
    aggregated = "aggregated"
    curated = "curated"
    completed = "completed"


class ReviewResult(BaseModel):
    score: int
    max_score: int = 100
    findings: list[Finding] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    recommendations: list[RecommendationEntity] = Field(default_factory=list)


class EAReview(ReviewResult):
    review_id: str
    framework: str = "TOGAF"
    status: str = "completed"


class Violation(BaseModel):
    policy_id: str
    title: str
    description: str
    severity: Severity


class IQReview(ReviewResult):
    review_id: str
    violations: list[Violation] = Field(default_factory=list)
    status: str = "completed"


class AggregatedReview(BaseModel):
    review_id: str
    overall_score: int
    ea_score: int
    iq_score: int
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[RecommendationEntity] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


class CuratedReport(BaseModel):
    executive_summary: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    priority_actions: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class ReviewState(BaseModel):
    document_url: str
    status: ReviewStatus
    extracted_content: Optional[str] = None
    facts: Optional[ArchitectureFacts] = None
    ea_review: Optional[EAReview] = None
    iq_review: Optional[IQReview] = None
    aggregated_review: Optional[AggregatedReview] = None
    curated_report: Optional[CuratedReport] = None
