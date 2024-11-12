from fastapi import APIRouter, Depends, HTTPException
from app.schemas.code_review import CodeSubmission, CodeReviewResponse, ReviewResult, DetectedLanguage, SavedCodeReview, PossibleLanguage, CodeReviewListResponse
from app.services.azure_openai import AzureOpenAIService
from app.models.user import User
from app.core.security import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.code_review import CodeReview
from app.db.session import get_db
import json
from typing import List
import logging
from sqlalchemy import select

router = APIRouter()

@router.post("/review", response_model=CodeReviewResponse)
async def review_code(
    request: CodeSubmission,
    current_user: User = Depends(get_current_user),
    openai_service: AzureOpenAIService = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get language classification
        classification_str = await openai_service.classify_code(
            code=request.code,
            include_features=True,
            include_frameworks=True
        )
        classification = json.loads(classification_str)
        
        # Get code review with dynamic categories
        review_str = await openai_service.review_code(
            code=request.code,
            language=classification["primary_language"],
            assignment_prompt=request.assignment_prompt,
            requirements=request.requirements
        )
        review_data = json.loads(review_str)
        
        # Convert all review data into dynamic categories
        review_results = [
            ReviewResult(
                category=category,
                details=details
            )
            for category, details in review_data.items()
            if category not in ["Overall Code Quality", "Specific Issues Found", "error", "status"]
        ]

        # Create the response object
        response = CodeReviewResponse(
            status="success",
            error=None,
            overall_score=float(review_data.get("Overall Code Quality", 0)),
            review_results=review_results,
            detected_language=DetectedLanguage(
                name=classification["primary_language"],
                confidence=classification["confidence_score"],
                possible_languages=[
                    PossibleLanguage(
                        language=lang["language"],
                        score=lang["score"]
                    ) for lang in classification.get("possible_languages", [])
                ],
                features=classification.get("features", {})
            ),
            improvement_suggestions=review_data.get("Specific Issues Found", [])
        )
        
        # Save to database
        db_review = CodeReview(
            code=request.code,
            language=classification["primary_language"],
            assignment_name=request.assignment_name,
            assignment_prompt=request.assignment_prompt,
            requirements=request.requirements,
            status="success",
            overall_score=response.overall_score,
            review_results=response.model_dump(),  # Use model_dump() instead of dict()
            user_id=current_user.id
        )
        
        try:
            db.add(db_review)
            await db.commit()
            await db.refresh(db_review)
        except Exception as e:
            await db.rollback()
            
        return response  # Return the response object directly

    except Exception as e:
        error_response = CodeReviewResponse(
            status="error",
            error=str(e),
            overall_score=0,
            review_results=[],
            detected_language=DetectedLanguage(
                name="Unknown",
                confidence=0,
                possible_languages=[],
                features={}
            ),
            improvement_suggestions=[]
        )
        return error_response  # Return the error response object

@router.get("/reviews", response_model=List[CodeReviewListResponse])
async def list_reviews(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = select(CodeReview).where(
            CodeReview.user_id == current_user.id
        ).order_by(CodeReview.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        reviews = result.scalars().all()
        
        return [
            CodeReviewListResponse(
                id=review.id,
                language=review.language,
                overall_score=review.overall_score,
                created_at=review.created_at,
                assignment_name=review.assignment_name
            ) for review in reviews
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{review_id}", response_model=SavedCodeReview)
async def get_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(CodeReview).where(CodeReview.id == review_id, CodeReview.user_id == current_user.id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Convert database model to Pydantic model
    return SavedCodeReview(
        id=review.id,
        code=review.code,
        language=review.language,
        assignment_name=review.assignment_name,
        assignment_prompt=review.assignment_prompt,
        requirements=review.requirements,
        status=review.status,
        overall_score=review.overall_score,
        review_results=review.review_results["review_results"],
        detected_language=review.review_results["detected_language"],
        improvement_suggestions=review.review_results["improvement_suggestions"],
        user_id=review.user_id,
        created_at=review.created_at,
        updated_at=review.updated_at
    )