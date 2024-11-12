from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.services.azure_openai import AzureOpenAIService
from app.services.document_converter import DocumentConverter  # We'll create this
from app.models.user import User
from app.core.security import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import json
from typing import Optional

router = APIRouter()

@router.post("/upload-and-analyze")
async def upload_and_analyze_document(
    file: UploadFile = File(...),
    prompt: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    openai_service: AzureOpenAIService = Depends(),
    doc_converter: DocumentConverter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        # Convert document/image to text
        text_content = await doc_converter.to_text(content, file_type)
        
        # Use existing analyze_text method
        analysis = await openai_service.analyze_text(text_content)
        
        return analysis

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 