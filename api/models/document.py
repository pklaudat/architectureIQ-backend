from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class UploadResponse(BaseModel):
    document_id: str
    file_name: str
    blob_url: str


class FileFormat(str, Enum):
    PDF = "PDF"
    TXT = "TXT"
    MD = "MD"
    DOCX = "DOCX"
    PNG = "PNG"
    JPEG = "JPEG"
    SVG = "SVG"


class FileType(str, Enum):
    ARCHITECTURE_DEFINITION = "ARCHITECTURE_DEFINITION"
    ARCHITECTURE_DIAGRAM = "ARCHITECTURE_DIAGRAM"
    ARCHITECTURE_DECISION_RECORDS = "ARCHITECTURE_DECISION_RECORDS"
    SEQUENCE_DIAGRAM = "SEQUENCE_DIAGRAM"
    COMPONENT_DIAGRAM = "COMPONENT_DIAGRAM"
    DEPLOYMENT_DIAGRAM = "DEPLOYMENT_DIAGRAM"
    NETWORK_DIAGRAM = "NETWORK_DIAGRAM"
    DATA_FLOW_DIAGRAM = "DATA_FLOW_DIAGRAM"


class DocumentStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    CONTENT_EXTRACTED = "ContentExtracted"
    FAILED = "Failed"


class Document(BaseModel):
    id: str
    blob_url: str
    file_name: str
    file_format: FileFormat
    file_type: Optional[FileType]
    project_id: str
    status: DocumentStatus
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
