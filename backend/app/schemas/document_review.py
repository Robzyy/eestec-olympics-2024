from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    ESSAY = "essay"
    REPORT = "report"
    RESEARCH_PAPER = "research_paper"
    PRESENTATION = "presentation"
    IMAGE = "image"
    OTHER = "other"

class DocumentSubmission(BaseModel):
    content: str  # Base64 encoded string for images, text content for documents
    document_type: DocumentType
    file_type: str  # e.g., "pdf", "docx", "jpg", "png"
    assignment_name: Optional[str] = None
    assignment_prompt: Optional[str] = None
    requirements: Optional[List[str]] = None
    rubric: Optional[Dict[str, float]] = None  # Criteria and their weights

class DocumentReviewResult(BaseModel):
    category: str
    score: float
    details: str
    suggestions: List[str]

class DocumentReviewResponse(BaseModel):
    status: str
    error: Optional[str] = None
    overall_score: float
    review_results: List[DocumentReviewResult]
    improvement_suggestions: List[str]
    detected_type: str
    content_analysis: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

class SavedDocumentReview(DocumentReviewResponse):
    id: int
    content_hash: str  # Store hash of content instead of full content
    document_type: DocumentType
    file_type: str
    assignment_name: Optional[str]
    assignment_prompt: Optional[str]
    requirements: Optional[List[str]]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 