from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from app.schemas.grading import (
    GradingCriteria, 
    AssignmentRequirements,
    GradingRequest,
    GradingResponse
)

# Base request models
class OCRRequest(BaseModel):
    image_url: HttpUrl

class DocumentRequest(BaseModel):
    document_url: HttpUrl
    subject: Optional[str] = None
    level: Optional[str] = None
    grading_criteria: Optional[List[GradingCriteria]] = None
    assignment_requirements: Optional[AssignmentRequirements] = None
    rubric_type: Optional[str] = "academic"

# Text line model for both OCR and Document
class TextLine(BaseModel):
    text: str
    confidence: Optional[float] = None
    bounding_box: Optional[List[float]] = None
    page: Optional[int] = None

# Response models
class OCRResponse(BaseModel):
    status: str
    text_lines: List[TextLine] = []
    full_text: str = ""
    error: Optional[str] = None

class DocumentResponse(BaseModel):
    status: str
    pages: Optional[List[List[TextLine]]] = None
    full_text: Optional[str] = None
    page_count: Optional[int] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None

# Combined analysis response
class AnalysisResponse(BaseModel):
    status: str
    language_analysis: Optional[Dict] = None
    ai_analysis: Optional[str] = None
    document_type: Optional[str] = None
    original_text: Optional[str] = None
    error: Optional[str] = None 