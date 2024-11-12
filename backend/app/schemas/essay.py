from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class EssayBase(BaseModel):
    text: str

class EssayCreate(EssayBase):
    pass

class EssayResponse(EssayBase):
    id: int
    language_analysis: Dict[str, Any]
    document_analysis: Optional[Dict[str, Any]]
    final_analysis: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 