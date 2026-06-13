"""UI-facing DTOs (camelCase) returned by the list/aggregate endpoints.

These are deliberately shaped to match the React app's TypeScript types so the
frontend can consume them without any field mapping.
"""

from typing import List, Optional
from pydantic import BaseModel


class ProjectSummary(BaseModel):
    id: str
    displayName: str
    description: str = ""
    status: str = "In Review"
    documentCount: int = 0
    processingCount: int = 0
    completedCount: int = 0
    tags: List[str] = []
    createdAt: str = ""
    architectureScore: Optional[int] = None
    openFindings: int = 0
    highSeverity: int = 0
    mediumSeverity: int = 0
    lowSeverity: int = 0


class DocumentSummary(BaseModel):
    id: str
    projectId: str = ""
    projectName: Optional[str] = None
    fileName: str = ""
    status: str = "Pending"
    progress: int = 0
    currentStep: Optional[str] = None
    size: Optional[str] = None
    uploadedAt: Optional[str] = None
    pages: Optional[int] = None
    fileType: Optional[str] = None
    createdAt: str = ""


class ReviewSummary(BaseModel):
    id: str
    documentId: Optional[str] = None
    fileName: str = ""
    projectName: str = ""
    reviewType: str = "Architecture Review"
    status: str = "In Progress"
    score: Optional[int] = None
    findings: Optional[int] = None
    date: str = ""


class FindingSummary(BaseModel):
    id: str
    category: str
    severity: str
    title: str
    projectName: str = ""
    documentId: Optional[str] = None


# ── Analytics ──────────────────────────────────────────────────────────────


class TrendPoint(BaseModel):
    month: str
    value: float = 0


class CategorySlice(BaseModel):
    label: str
    value: int = 0  # percentage


class LeaderboardEntry(BaseModel):
    name: str
    score: int = 0


class AnalyticsKpis(BaseModel):
    avgArchitectureScore: int = 0
    avgScoreDelta: int = 0
    reviewsThisMonth: int = 0
    reviewsDelta: int = 0
    findingsResolved: int = 0
    findingsResolvedDelta: int = 0
    highSeverityOpen: int = 0
    highSeverityDelta: int = 0


class Analytics(BaseModel):
    kpis: AnalyticsKpis = AnalyticsKpis()
    reviewsOverTime: List[TrendPoint] = []
    findingsByCategory: List[CategorySlice] = []
    scoreTrend: List[TrendPoint] = []
    leaderboard: List[LeaderboardEntry] = []
