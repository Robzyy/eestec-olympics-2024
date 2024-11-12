from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, UTC

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String)
    subject = Column(String, nullable=True)
    level = Column(String, nullable=True)
    overall_score = Column(Float)
    grading_results = Column(JSON)
    detailed_feedback = Column(String)
    improvement_suggestions = Column(JSON)
    language_quality = Column(JSON)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Add relationship to User
    user = relationship("User", back_populates="grades")