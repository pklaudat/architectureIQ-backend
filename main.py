import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.document import router as document_router
from api.routes.projects import router as project_router
from api.routes.reviews import router as review_router
from api.routes.findings import router as findings_router
from api.routes.analytics import router as analytics_router
from worker.document_processing import DocumentProcessing
from worker.agentic_review import AgenticReview
from contextlib import asynccontextmanager
import uvicorn

document_worker = DocumentProcessing(queue_name="document-processing")
agentic_review = AgenticReview(queue_name="reviews-processing")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("STARTUP")
    task = asyncio.create_task(document_worker.start())
    task2 = asyncio.create_task(agentic_review.start())
    yield
    print("SHUTDOWN")
    task.cancel()
    task2.cancel()

app = FastAPI(title="Enterprise Architecture Advisor", lifespan=lifespan)

# Allow the Vite dev server (and any other local origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(document_router, prefix="/api", tags=["documents"])
app.include_router(project_router, prefix="/api", tags=["projects"])
app.include_router(review_router, prefix="/api", tags=["reviews"])
app.include_router(findings_router, prefix="/api", tags=["findings"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8080)
