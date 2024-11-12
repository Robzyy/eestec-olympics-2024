from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

class DetectedLanguage(BaseModel):
    name: str
    confidence: float
    possible_languages: List[Dict[str, float]]
    features: Dict[str, List[str]]

class ReviewResult(BaseModel):
    category: str
    details: Union[str, Dict[str, Any]]

class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text)
    language = Column(String)
    assignment_name = Column(String, nullable=True)
    assignment_prompt = Column(Text, nullable=True)
    requirements = Column(JSON, nullable=True)
    status = Column(String)
    overall_score = Column(Integer)
    review_results = Column(JSON)
    security_analysis = Column(JSON, nullable=True)
    performance_analysis = Column(JSON, nullable=True)
    best_practices = Column(JSON)
    improvement_suggestions = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="code_reviews")