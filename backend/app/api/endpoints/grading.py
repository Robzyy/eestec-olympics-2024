from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.schemas.grading import GradingRequest, GradingResponse, GradingCriteria, AssignmentRequirements, GradeListResponse
from app.services.azure_openai import AzureOpenAIService
from app.services.azure_language import AzureLanguageService
from app.models.user import User
from app.core.security import get_current_user
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.grade import Grade
from app.db.session import get_db
from app.services.azure_vision import AzureVisionService
from app.services.azure_document import AzureDocumentService
import logging
import base64
import os
from io import BytesIO

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/grade")
async def grade_text(
    request: GradingRequest,
    current_user: User = Depends(get_current_user),
    openai_service: AzureOpenAIService = Depends(),
    language_service: AzureLanguageService = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get language analysis
        language_analysis = await language_service.analyze_text(request.text)
        
        # Prepare the prompt with the exact criteria and score ranges
        criteria_text = "\n".join([
            f"- {c.category} (Weight: {c.weight}): {c.description}"
            f"\n  Score range: {c.min_score} to {c.max_score}"
            for c in request.grading_criteria
        ]) if request.grading_criteria else "Use default academic criteria"

        prompt = f"""Grade this {request.subject} text for {request.level} level.

        Text: {request.text}

        Use EXACTLY these grading criteria and score ranges:
        {criteria_text}

        Assignment Requirements:
        Title: {request.assignment_requirements.title if request.assignment_requirements else 'Not specified'}
        Description: {request.assignment_requirements.description if request.assignment_requirements else 'Not specified'}
        Word Count: {request.assignment_requirements.word_count if request.assignment_requirements else 'Not specified'}
        Special Instructions: {request.assignment_requirements.special_instructions if request.assignment_requirements else 'Not specified'}

        IMPORTANT: 
        - Scores MUST be integers within the specified min-max range for each criterion
        - Be critical and thorough in your evaluation
        - Consider both strengths and weaknesses
        - Provide detailed justification for each score
        - Do not inflate scores; use the full range appropriately
        """

        # Get AI grading
        grading_result = await openai_service.get_completion(prompt)
        result = json.loads(grading_result)

        # Ensure scores are within the specified ranges
        if request.grading_criteria:
            criteria_dict = {c.category: c for c in request.grading_criteria}
            for grade in result.get("grading_results", []):
                if grade["criterion"] in criteria_dict:
                    criterion = criteria_dict[grade["criterion"]]
                    # Convert score to the specified range
                    raw_score = float(grade["score"])
                    # If score is between 0-1, scale it to the min-max range
                    if 0 <= raw_score <= 1:
                        grade["score"] = int(criterion.min_score + (raw_score * (criterion.max_score - criterion.min_score)))
                    else:
                        # Ensure score is within bounds
                        grade["score"] = max(criterion.min_score, min(criterion.max_score, int(raw_score)))

            # Calculate weighted average for overall score
            total_weight = sum(c.weight for c in request.grading_criteria)
            weighted_scores = [
                (criteria_dict[grade["criterion"]].weight * grade["score"])
                for grade in result["grading_results"]
                if grade["criterion"] in criteria_dict
            ]
            result["overall_score"] = sum(weighted_scores) / total_weight if total_weight > 0 else 0

        # Save the grade to database
        db_grade = Grade(
            user_id=current_user.id,
            text=request.text,
            subject=request.subject,
            level=request.level,
            overall_score=result["overall_score"],
            grading_results=result["grading_results"],
            detailed_feedback=result["detailed_feedback"],
            improvement_suggestions=result["improvement_suggestions"],
            language_quality=result["language_quality"],
            strengths=result["strengths"],
            weaknesses=result["weaknesses"]
        )
        
        db.add(db_grade)
        await db.commit()
        await db.refresh(db_grade)

        return result

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grades", response_model=List[GradeListResponse])
async def list_grades(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = select(Grade).where(Grade.user_id == current_user.id).order_by(Grade.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        grades = result.scalars().all()
        return grades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grades/{grade_id}", response_model=GradingResponse)
async def get_grade(
    grade_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = select(Grade).where(Grade.id == grade_id, Grade.user_id == current_user.id)
        result = await db.execute(query)
        grade = result.scalar_one_or_none()
        
        if not grade:
            raise HTTPException(status_code=404, detail="Grade not found")
            
        return grade
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grade-document")
async def grade_document(
    file: UploadFile = File(...),
    subject: Optional[str] = Form(None),
    level: Optional[str] = Form(None),
    grading_criteria: Optional[str] = Form(None),
    assignment_requirements: Optional[str] = Form(None),
    rubric_type: Optional[str] = Form("academic"),
    vision_service: AzureVisionService = Depends(),
    document_service: AzureDocumentService = Depends(),
    current_user: User = Depends(get_current_user),
    openai_service: AzureOpenAIService = Depends(),
    language_service: AzureLanguageService = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        content = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        # Extract text based on file type
        if file_type in ['jpg', 'jpeg', 'png']:
            image_stream = BytesIO(content)
            result = await vision_service.extract_text(image_stream)
        elif file_type in ['pdf', 'docx', 'doc']:
            temp_file_path = f"/tmp/{file.filename}"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(content)
            try:
                result = await document_service.analyze_document(temp_file_path)
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_type}"
            )

        if not result or result.get("status") == "error":
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to extract text from document")
            )

        # Parse grading criteria from the request
        criteria_list = []
        if grading_criteria:
            try:
                custom_criteria = json.loads(grading_criteria)
                for c in custom_criteria:
                    criteria_list.append(GradingCriteria(
                        category=c["category"],
                        weight=c["weight"],
                        description=c["description"],
                        min_score=c["min_score"],
                        max_score=c["max_score"]
                    ))
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid grading criteria format: {str(e)}"
                )

        # Parse assignment requirements if provided
        assignment_req = None
        if assignment_requirements:
            try:
                req_data = json.loads(assignment_requirements)
                assignment_req = AssignmentRequirements(**req_data)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid assignment requirements format: {str(e)}"
                )

        # Create grading request
        request = GradingRequest(
            text=result.get("full_text", ""),
            subject=subject if subject != "string" else None,
            level=level if level != "string" else None,
            grading_criteria=criteria_list,
            assignment_requirements=assignment_req,
            rubric_type=rubric_type if rubric_type != "string" else "academic"
        )

        # Get grading result
        grading_result = await grade_text(
            request=request,
            current_user=current_user,
            openai_service=openai_service,
            language_service=language_service
        )

        return {
            "status": "success",
            "error": None,
            "extracted_text": result.get("full_text", ""),
            "grading_result": grading_result
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "extracted_text": "",
            "grading_result": {
                "overall_score": 0,
                "grading_results": [],
                "detailed_feedback": "",
                "improvement_suggestions": [],
                "language_quality": {
                    "grammar": "Error occurred",
                    "vocabulary": "Error occurred",
                    "style": "Error occurred",
                    "comments": str(e)
                },
                "strengths": [],
                "weaknesses": []
            }
        }