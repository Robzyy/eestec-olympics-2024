from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.azure_openai import AzureOpenAIService
from app.services.azure_language import AzureLanguageService
from app.services.azure_document import AzureDocumentService
from app.services.azure_vision import AzureVisionService
from app.db.session import get_db
from app.models.essay import Essay
from app.schemas.essay import EssayCreate, EssayResponse
from app.schemas.ocr import (
    OCRRequest, 
    OCRResponse, 
    DocumentRequest, 
    DocumentResponse,
    AnalysisResponse,
    GradingRequest
)
from typing import Optional, List
import mimetypes
import logging
from app.models.user import User
from app.core.security import get_current_user

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze-essay", response_model=EssayResponse)
async def analyze_essay(
    essay: EssayCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    openai_service: AzureOpenAIService = Depends(),
    language_service: AzureLanguageService = Depends()
):
    try:
        # Perform analysis
        language_analysis = await language_service.analyze_text(essay.text)
        
        document_analysis = None
        if essay.text.startswith('http'):
            document_analysis = await document_service.analyze_document(essay.text)
        
        prompt = f"""
        Based on the following analysis results, provide a comprehensive essay evaluation:
        
        Language Analysis: {language_analysis}
        Document Analysis: {document_analysis if document_analysis else 'Not available'}
        
        Please synthesize these findings into a coherent analysis.
        """
        
        final_analysis = await openai_service.analyze_text(prompt)
        
        # Create database entry
        db_essay = Essay(
            text=essay.text,
            language_analysis=language_analysis,
            document_analysis=document_analysis,
            final_analysis={"analysis": final_analysis}
        )
        
        db.add(db_essay)
        await db.commit()
        await db.refresh(db_essay)
        
        return db_essay
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/essays/{essay_id}", response_model=EssayResponse)
async def get_essay(
    essay_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Essay).where(Essay.id == essay_id, Essay.user_id == current_user.id)
    result = await db.execute(query)
    essay = result.scalar_one_or_none()
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    return essay

@router.get("/essays", response_model=List[EssayResponse])
async def list_essays(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Essay).where(Essay.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/ocr", response_model=OCRResponse)
async def perform_ocr(
    request: OCRRequest,
    vision_service: AzureVisionService = Depends()
):
    """
    Extract text from an image using OCR.
    """
    try:
        result = await vision_service.extract_text(str(request.image_url))
        return result
    except Exception as e:
        return {
            "status": "error",
            "text_lines": [],
            "full_text": "",
            "error": str(e)
        }

@router.post("/analyze-image")
async def analyze_image(
    request: OCRRequest,
    vision_service: AzureVisionService = Depends(),
    openai_service: AzureOpenAIService = Depends(),
    language_service: AzureLanguageService = Depends()
):
    try:
        # Step 1: Extract text from image
        ocr_result = await vision_service.extract_text(str(request.image_url))
        if ocr_result["status"] == "error":
            raise HTTPException(status_code=400, detail=ocr_result["error"])

        extracted_text = ocr_result["full_text"]
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text was extracted from the image")

        # Step 2: Analyze the extracted text
        language_analysis = await language_service.analyze_text(extracted_text)
        
        # Step 3: Get AI insights
        prompt = f"""
        Analyze the following text extracted from an image:

        TEXT:
        {extracted_text}

        LANGUAGE ANALYSIS:
        {language_analysis}

        Please provide:
        1. A summary of the main points
        2. Key insights or findings
        3. Any potential issues or areas of concern
        4. Writing quality assessment
        """
        
        ai_analysis = await openai_service.analyze_text(prompt)

        return {
            "status": "success",
            "ocr_result": ocr_result,
            "language_analysis": language_analysis,
            "ai_analysis": ai_analysis,
            "original_text": extracted_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-text")
async def extract_text(
    request: DocumentRequest,
    vision_service: AzureVisionService = Depends(),
    document_service: AzureDocumentService = Depends()
):
    try:
        # Determine file type from URL
        file_type = mimetypes.guess_type(request.document_url)[0]
        
        if file_type == 'application/pdf':
            # Handle PDF using Document Intelligence
            result = await document_service.analyze_document(str(request.document_url))
        else:
            # Handle images using Computer Vision
            result = await vision_service.extract_text(str(request.document_url))

        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-document", response_model=AnalysisResponse)
async def analyze_document(
    request: DocumentRequest,
    vision_service: AzureVisionService = Depends(),
    document_service: AzureDocumentService = Depends(),
    openai_service: AzureOpenAIService = Depends(),
    language_service: AzureLanguageService = Depends(),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.debug("Starting document analysis")
        document_url = str(request.document_url)
        file_type = mimetypes.guess_type(document_url)[0]
        
        # Extract text based on file type
        if file_type == 'application/pdf':
            extraction_result = await document_service.analyze_document(document_url)
        elif file_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            # Handle Word documents
            extraction_result = await document_service.analyze_document(document_url)
        else:
            # Handle images
            extraction_result = await vision_service.extract_text(document_url)

        if extraction_result["status"] == "error":
            raise HTTPException(status_code=400, detail=extraction_result["error"])

        extracted_text = extraction_result.get("full_text", "")
        
        # Create grading request
        grading_request = GradingRequest(
            text=extracted_text,
            subject=request.subject,  # Add these fields to DocumentRequest
            level=request.level,
            grading_criteria=request.grading_criteria,
            assignment_requirements=request.assignment_requirements,
            rubric_type=request.rubric_type
        )

        # Get language analysis
        language_analysis = await language_service.analyze_text(extracted_text)

        # Get grading analysis
        grading_result = await openai_service.grade_text(grading_request)

        return {
            "status": "success",
            "language_analysis": language_analysis,
            "ai_analysis": grading_result,
            "document_type": file_type,
            "original_text": extracted_text
        }

    except Exception as e:
        logger.error(f"Error in analyze_document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/essays/{essay_id}")
async def delete_essay(
    essay_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Essay).where(Essay.id == essay_id, Essay.user_id == current_user.id)
    result = await db.execute(query)
    essay = result.scalar_one_or_none()
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    await db.delete(essay)
    await db.commit()
    return {"message": "Essay deleted"}
