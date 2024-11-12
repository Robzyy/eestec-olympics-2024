from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class GradingCriteria(BaseModel):
    category: str
    weight: float
    description: str
    min_score: int = 0
    max_score: int = 100

class AssignmentRequirements(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    word_count: Optional[Dict[str, int]] = None
    special_instructions: Optional[str] = None

class GradingRequest(BaseModel):
    text: str
    subject: Optional[str] = None
    level: Optional[str] = None
    grading_criteria: Optional[List[GradingCriteria]] = None
    assignment_requirements: Optional[AssignmentRequirements] = None
    rubric_type: Optional[str] = "academic"

class GradeListResponse(BaseModel):
    id: int
    overall_score: float
    subject: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class GradingResponse(BaseModel):
    status: str = "success"
    error: Optional[str] = None
    overall_score: float
    grading_results: List[Dict[str, Any]]
    detailed_feedback: str
    improvement_suggestions: List[str]
    language_quality: Dict[str, str]
    strengths: List[str]
    weaknesses: List[str]
    text: str
    subject: Optional[str] = None
    level: Optional[str] = None

    class Config:
        from_attributes = True
 