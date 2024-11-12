from fastapi import APIRouter, Depends, HTTPException
from app.schemas.code_classification import (
    CodeClassificationRequest,
    CodeClassificationResponse,
    SavedClassification,
    PossibleLanguage
)
from app.services.azure_openai import AzureOpenAIService
from app.models.user import User
from app.core.security import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.code_classification import CodeClassification
from app.db.session import get_db
import json
from typing import List

router = APIRouter()

@router.post("/classify", response_model=CodeClassificationResponse)
async def classify_code(
    request: CodeClassificationRequest,
    current_user: User = Depends(get_current_user),
    openai_service: AzureOpenAIService = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get classification from Azure OpenAI
        classification_str = await openai_service.classify_code(
            code=request.code,
            include_features=request.include_features,
            include_frameworks=request.include_frameworks
        )
        
        # Parse the JSON string response
        classification = json.loads(classification_str)
        
        # Format possible_languages to match the schema
        possible_languages = [
            PossibleLanguage(language=lang["language"], score=lang["score"])
            for lang in classification.get("possible_languages", [])
        ]
        
        # Create the response
        response = CodeClassificationResponse(
            primary_language=classification["primary_language"],
            confidence_score=float(classification["confidence_score"]),
            possible_languages=possible_languages,
            features=classification.get("features"),
            error=None
        )
        
        # Save to database
        db_classification = CodeClassification(
            code=request.code,
            primary_language=response.primary_language,
            confidence_score=response.confidence_score,
            possible_languages=[{"language": pl.language, "score": pl.score} for pl in response.possible_languages],
            features=response.features.dict() if response.features else None,
            user_id=current_user.id
        )
        
        db.add(db_classification)
        await db.commit()
        await db.refresh(db_classification)
        
        # Format the response to match our schema
        response = {
            "primary_language": classification["primary_language"],
            "confidence_score": float(classification["confidence_score"]),
            "possible_languages": classification["possible_languages"],
            "features": classification.get("features"),
            "error": None
        }
        
        return response

    except Exception as e:
        return {
            "primary_language": "unknown",
            "confidence_score": 0.0,
            "possible_languages": [],
            "features": None,
            "error": str(e)
        }

@router.get("/classifications", response_model=List[SavedClassification])
async def list_classifications(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(CodeClassification).where(
        CodeClassification.user_id == current_user.id
    ).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/classifications/{classification_id}", response_model=SavedClassification)
async def get_classification(
    classification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(CodeClassification).where(
        CodeClassification.id == classification_id,
        CodeClassification.user_id == current_user.id
    )
    result = await db.execute(query)
    classification = result.scalar_one_or_none()
    if not classification:
        raise HTTPException(status_code=404, detail="Classification not found")
    return classification 