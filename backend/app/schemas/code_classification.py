from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class CodeClassificationRequest(BaseModel):
    code: str
    include_features: bool = True
    include_frameworks: bool = True

class PossibleLanguage(BaseModel):
    language: str
    score: float

class LanguageFeatures(BaseModel):
    syntax_elements: List[str]
    programming_paradigms: List[str]
    language_version_hints: List[str]
    frameworks_and_libraries: List[str]
    special_language_features: List[str]

class CodeClassificationResponse(BaseModel):
    primary_language: str
    confidence_score: float
    possible_languages: List[PossibleLanguage]  # Changed to use PossibleLanguage model
    features: Optional[LanguageFeatures] = None
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class SavedClassification(CodeClassificationResponse):
    id: int
    code: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True