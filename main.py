import asyncio
from fastapi import FastAPI
from api.routes.document import router as document_router
from api.routes.projects import router as project_router
from api.routes.reviews import router as review_router
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

app.include_router(document_router, prefix="/api", tags=["documents"])
app.include_router(project_router, prefix="/api", tags=["projects"])
app.include_router(review_router, prefix="/api", tags=["reviews"])


if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8080)