from pydantic import BaseModel
from orchestration.agents.state import Finding

class Finding(BaseModel, Finding):
    project_id: str
    document_id: str

