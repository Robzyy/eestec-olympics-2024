from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.schemas.document_review import DocumentType

class DocumentReview(Base):
    __tablename__ = "document_reviews"

    id = Column(Integer, primary_key=True, index=True)
    content_hash = Column(String, index=True)
    document_type = Column(Enum(DocumentType))
    file_type = Column(String)
    assignment_name = Column(String, nullable=True)
    assignment_prompt = Column(String, nullable=True)
    requirements = Column(JSON, nullable=True)
    rubric = Column(JSON, nullable=True)
    status = Column(String)
    overall_score = Column(Float)
    review_results = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="document_reviews") 