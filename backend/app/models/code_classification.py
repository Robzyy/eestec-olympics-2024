from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CodeClassification(Base):
    __tablename__ = "code_classifications"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Text)
    primary_language = Column(String)
    confidence_score = Column(Float)
    possible_languages = Column(JSON)
    features = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="code_classifications") 