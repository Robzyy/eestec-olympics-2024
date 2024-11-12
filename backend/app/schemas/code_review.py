from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class CodeSubmission(BaseModel):
    code: str
    assignment_name: Optional[str] = None
    assignment_prompt: Optional[str] = None
    requirements: Optional[List[str]] = None

class PossibleLanguage(BaseModel):
    language: str
    score: float

class DetectedLanguage(BaseModel):
    name: str
    confidence: float
    possible_languages: List[PossibleLanguage]
    features: Dict[str, List[str]]

class ReviewResult(BaseModel):
    category: str
    details: Union[str, Dict[str, Any]]

class CodeReviewResponse(BaseModel):
    status: str
    error: Optional[str] = None
    overall_score: float
    review_results: List[ReviewResult]
    detected_language: DetectedLanguage
    improvement_suggestions: List[str]

    class Config:
        arbitrary_types_allowed = True

class SavedCodeReview(CodeReviewResponse):
    id: int
    code: str
    language: str
    assignment_name: Optional[str]
    assignment_prompt: Optional[str]
    requirements: Optional[List[str]]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class CodeReviewListResponse(BaseModel):
    id: int
    language: str
    overall_score: float
    created_at: datetime
    assignment_name: Optional[str] = None

    class Config:
        from_attributes = True