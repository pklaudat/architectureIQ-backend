from enum import Enum
from typing import Optional, Literal

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


class ReviewStatus(str, Enum):
    in_progress = "in_progress"
    started = "started"
    facts_extracted = "facts_extracted"
    ea_review_complete = "ea_review_complete"
    iq_review_complete = "iq_review_complete"
    aggregated = "aggregated"
    curated = "curated"
    completed = "completed"
    failed = "failed"


class StateMap(str, Enum):
    architecture_facts_extractor = ReviewStatus.facts_extracted.value
    enterprise_architecture_reviewer = ReviewStatus.ea_review_complete.value
    internal_iq_advisor = ReviewStatus.iq_review_complete.value
    aggregator = ReviewStatus.aggregated.value
    review_curator = ReviewStatus.completed.value
    review_dispatcher = ReviewStatus.started.value


class ArchitectureFacts(BaseModel):
    status: Literal[ReviewStatus.facts_extracted] = ReviewStatus.facts_extracted
    system_name: str
    stakeholders: list[str] = Field(default_factory=list)
    authentication: Authentication = None
    availability: Optional[Availability] = None
    technology: Technology = None
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


class ReviewResult(BaseModel):
    score: int
    max_score: int = 100
    facts: ArchitectureFacts
    findings: list[Finding] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    recommendations: list[RecommendationEntity] = Field(default_factory=list)


class EAReview(ReviewResult):
    status: Literal[ReviewStatus.ea_review_complete] = ReviewStatus.ea_review_complete
    framework: str = "TOGAF"
    status: str = "completed"


class Violation(BaseModel):
    policy_id: str
    title: str
    description: str
    severity: Severity


class IQReview(ReviewResult):
    status: Literal[ReviewStatus.iq_review_complete] = ReviewStatus.iq_review_complete
    violations: list[Violation] = Field(default_factory=list)
    status: str = "completed"


class AggregatedReview(BaseModel):
    status: Literal[ReviewStatus.aggregated] = ReviewStatus.aggregated
    overall_score: int
    ea_score: int
    iq_score: int
    facts: ArchitectureFacts
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[RecommendationEntity] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)


class CuratedReport(BaseModel):
    status: Literal[ReviewStatus.curated] = ReviewStatus.curated
    executive_summary: str
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    priority_actions: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)


class FinalReviewResult(BaseModel):
    status: ReviewStatus = Field(default=ReviewStatus.started)
    score: int
    facts: ArchitectureFacts
    aggregated_review: AggregatedReview
    curated_report: CuratedReport
