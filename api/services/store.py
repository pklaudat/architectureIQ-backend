"""Read helpers: load Cosmos items and shape them into the camelCase DTOs the UI expects."""

from datetime import datetime

from api.services.cosmos_db import CosmosDbService
from api.models.summaries import (
    ProjectSummary,
    DocumentSummary,
    ReviewSummary,
    FindingSummary,
    Analytics,
    AnalyticsKpis,
    TrendPoint,
    CategorySlice,
    LeaderboardEntry,
)

projects = CosmosDbService(container_name="Projects")
documents = CosmosDbService(container_name="Documents")
reviews = CosmosDbService(container_name="Reviews")

_ALL = "SELECT * FROM c"
_BY_PROJECT = "SELECT * FROM c WHERE c.project_id = @pid"


# ── fetchers ───────────────────────────────────────────────────────────────


async def fetch_all_projects():
    return await projects.query_items(_ALL)


async def fetch_all_documents():
    return await documents.query_items(_ALL)


async def fetch_all_reviews():
    return await reviews.query_items(_ALL)


async def documents_for_project(project_id):
    return await documents.query_items(_BY_PROJECT, [{"name": "@pid", "value": project_id}])


async def reviews_for_project(project_id):
    return await reviews.query_items(_BY_PROJECT, [{"name": "@pid", "value": project_id}])


# ── lookups ────────────────────────────────────────────────────────────────

_SEVERITY = {"critical": "High", "high": "High", "medium": "Medium", "low": "Low"}
_CATEGORY = {
    "security": "Security", "authentication": "Security",
    "high_availability": "Reliability", "disaster_recovery": "Reliability",
    "technology": "Performance", "operations": "Operations", "governance": "Operations",
}
# document status -> (display label, progress %, current step)
_DOC_VIEW = {
    "Pending": ("Pending", 0, "Queued"),
    "Processing": ("Processing", 55, "Content Extraction"),
    "ContentExtracted": ("Completed", 100, "Finished"),
    "Failed": ("Failed", 100, "Failed"),
}


def group_by(items, key):
    out = {}
    for item in items:
        out.setdefault(item.get(key), []).append(item)
    return out


def _ago(iso):
    if not iso:
        return None
    try:
        secs = (datetime.now() - datetime.fromisoformat(iso)).total_seconds()
    except (ValueError, TypeError):
        return iso
    if secs < 3600:
        return f"{max(1, int(secs // 60))}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


# ── mappers ────────────────────────────────────────────────────────────────


def map_document(doc, project_name=None):
    label, progress, step = _DOC_VIEW.get(doc.get("status"), ("Pending", 0, "Queued"))
    return DocumentSummary(
        id=doc.get("id", ""),
        projectId=doc.get("project_id", ""),
        projectName=project_name,
        fileName=doc.get("file_name", ""),
        status=label,
        progress=progress,
        currentStep=step,
        fileType=doc.get("file_format"),
        uploadedAt=_ago(doc.get("created_at")),
        createdAt=doc.get("created_at", ""),
    )


def map_project(project, docs, revs):
    processing = sum(1 for d in docs if d.get("status") in ("Pending", "Processing"))
    completed = sum(1 for d in docs if d.get("status") == "ContentExtracted")
    status = "Processing" if processing else "Completed" if docs and completed == len(docs) else "In Review"

    findings = [f for r in revs for f in (r.get("findings") or [])]
    scores = [r["score"] for r in revs if r.get("score") is not None]

    return ProjectSummary(
        id=project.get("id", ""),
        displayName=project.get("display_name", ""),
        description=project.get("description", ""),
        status=status,
        documentCount=len(docs),
        processingCount=processing,
        completedCount=completed,
        tags=project.get("tags", []),
        createdAt=project.get("created_at", ""),
        architectureScore=round(sum(scores) / len(scores)) if scores else None,
        openFindings=len(findings),
        highSeverity=sum(1 for f in findings if f.get("severity") in ("critical", "high")),
        mediumSeverity=sum(1 for f in findings if f.get("severity") == "medium"),
        lowSeverity=sum(1 for f in findings if f.get("severity") == "low"),
    )


def map_review(review, document_name=None, project_name=None):
    done = review.get("status") == "completed"
    return ReviewSummary(
        id=review.get("id", ""),
        documentId=review.get("document_id"),
        fileName=document_name or "",
        projectName=project_name or "",
        status="Completed" if done else "In Progress",
        score=review.get("score") if done else None,
        findings=len(review.get("findings") or []) if done else None,
        date=_ago(review.get("completed_at") or review.get("created_at")) or "",
    )


def map_findings(all_reviews, project_names):
    out = []
    for r in all_reviews:
        name = project_names.get(r.get("project_id"), "")
        for i, f in enumerate(r.get("findings") or []):
            out.append(
                FindingSummary(
                    id=f"{r.get('id', 'r')}-{i}",
                    category=_CATEGORY.get(f.get("area", ""), "Operations"),
                    severity=_SEVERITY.get(f.get("severity", "low"), "Low"),
                    title=f.get("title", ""),
                    projectName=name,
                    documentId=r.get("document_id"),
                )
            )
    return out


def build_analytics(all_projects, all_documents, all_reviews):
    now = datetime.now()

    # last six (year, month) buckets, oldest first
    months = []
    for offset in range(5, -1, -1):
        m, y = now.month - offset, now.year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    label = {k: datetime(k[0], k[1], 1).strftime("%b") for k in months}

    count = {k: 0 for k in months}
    score_sum = {k: 0 for k in months}
    score_n = {k: 0 for k in months}
    for r in all_reviews:
        try:
            dt = datetime.fromisoformat(r.get("created_at", ""))
        except (ValueError, TypeError):
            continue
        k = (dt.year, dt.month)
        if k in count:
            count[k] += 1
            if r.get("score") is not None:
                score_sum[k] += r["score"]
                score_n[k] += 1

    reviews_over_time = [TrendPoint(month=label[k], value=count[k]) for k in months]
    score_trend = [
        TrendPoint(month=label[k], value=round(score_sum[k] / score_n[k]) if score_n[k] else 0)
        for k in months
    ]

    findings = [f for r in all_reviews for f in (r.get("findings") or [])]
    cats = {}
    for f in findings:
        c = _CATEGORY.get(f.get("area", ""), "Operations")
        cats[c] = cats.get(c, 0) + 1
    total = sum(cats.values())
    by_category = (
        [CategorySlice(label=c, value=round(100 * n / total)) for c, n in sorted(cats.items(), key=lambda kv: -kv[1])]
        if total else []
    )

    names = {p.get("id"): p.get("display_name", "Unknown") for p in all_projects}
    leaderboard = []
    for pid, revs in group_by(all_reviews, "project_id").items():
        scores = [r["score"] for r in revs if r.get("score") is not None]
        if scores:
            leaderboard.append(LeaderboardEntry(name=names.get(pid, "Unknown"), score=round(sum(scores) / len(scores))))
    leaderboard.sort(key=lambda e: -e.score)

    all_scores = [r["score"] for r in all_reviews if r.get("score") is not None]
    completed = sum(1 for r in all_reviews if r.get("status") == "completed")
    kpis = AnalyticsKpis(
        avgArchitectureScore=round(sum(all_scores) / len(all_scores)) if all_scores else 0,
        reviewsThisMonth=count.get((now.year, now.month), 0),
        findingsResolved=round(100 * completed / len(all_reviews)) if all_reviews else 0,
        highSeverityOpen=sum(1 for f in findings if f.get("severity") in ("critical", "high")),
    )

    return Analytics(
        kpis=kpis,
        reviewsOverTime=reviews_over_time,
        findingsByCategory=by_category,
        scoreTrend=score_trend,
        leaderboard=leaderboard,
    )
