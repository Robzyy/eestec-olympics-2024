Essay Analysis and Code Review API Documentation
Overview
This API provides services for essay analysis, code review, and document processing using Azure AI services. It includes user authentication and secure endpoints.
Base URL http://localhost:8000/api
Authentication
The API uses JWT (JSON Web Token) authentication.
Auth Endpoints
POST /auth/register
- Register a new user
- Body: {
    "email": "user@example.com",
    "username": "username",
    "password": "password"
}

POST /auth/token
- Login and get access token
- Body: {
    "username": "username",
    "password": "password"
}
- Returns: {
    "access_token": "string",
    "token_type": "bearer"
}

GET /auth/users/me
- Get current user information
- Requires: Bearer token

Essay Analysis
Endpoints
POST /analyze-essay
- Analyze essay text
- Requires: Bearer token
- Body: {
    "text": "Essay text content"
}
- Returns: {
    "id": int,
    "language_analysis": {...},
    "document_analysis": {...},
    "final_analysis": {...},
    "created_at": "datetime",
    "updated_at": "datetime"
}

GET /essays
- List user's essays
- Requires: Bearer token
- Query params: 
  - skip: int (default: 0)
  - limit: int (default: 10)

GET /essays/{essay_id}
- Get specific essay
- Requires: Bearer token

DELETE /essays/{essay_id}
- Delete essay
- Requires: Bearer token

Code Review
Endpoints

POST /grading/review
- Review code submission
- Requires: Bearer token
- Body: {
    "code": "string",
    "language": "string",
    "assignment_name": "string (optional)",
    "requirements": ["string"] (optional),
    "test_cases": [{
        "input": "string",
        "expected_output": "string"
    }] (optional)
}
- Returns: {
    "status": "string",
    "overall_score": float,
    "review_results": [{
        "category": "string",
        "score": float,
        "feedback": "string",
        "suggestions": ["string"],
        "code_snippets": {...}
    }],
    "security_analysis": {...},
    "performance_analysis": {...},
    "best_practices": ["string"],
    "improvement_suggestions": ["string"]
}

GET /grading/reviews
- List code reviews
- Requires: Bearer token
- Query params:
  - skip: int (default: 0)
  - limit: int (default: 10)

GET /grading/reviews/{review_id}
- Get specific code review
- Requires: Bearer token

DELETE /grading/reviews/{review_id}
- Delete code review
- Requires: Bearer token

Document Processing
OCR Endpoints

POST /ocr/image
- Extract text from image
- Requires: Bearer token
- Body: {
    "image_url": "string (URL)"
}
- Returns: {
    "status": "string",
    "text_lines": [{
        "text": "string",
        "confidence": float,
        "bounding_box": [float],
        "page": int
    }],
    "full_text": "string"
}

POST /ocr/document
- Analyze document
- Requires: Bearer token
- Body: {
    "document_url": "string (URL)"
}
- Returns: {
    "status": "string",
    "pages": [...],
    "full_text": "string",
    "page_count": int,
    "metadata": {...}
}

Models
User Model
{
    "id": int,
    "email": string,
    "username": string,
    "is_active": boolean,
    "is_superuser": boolean,
    "created_at": datetime
}

Essay Model
{
    "id": int,
    "text": string,
    "language_analysis": JSON,
    "document_analysis": JSON,
    "final_analysis": JSON,
    "user_id": int,
    "created_at": datetime,
    "updated_at": datetime
}

Code Review Model
{
    "id": int,
    "code": string,
    "language": string,
    "assignment_name": string,
    "requirements": JSON,
    "test_cases": JSON,
    "review_results": JSON,
    "security_analysis": JSON,
    "performance_analysis": JSON,
    "user_id": int,
    "created_at": datetime,
    "updated_at": datetime
}

Azure Services Used
Azure OpenAI (GPT-4) for text analysis and code review
Azure Language Service for language analysis
Azure Document Intelligence for document processing
Azure Computer Vision for OCR
Environment Variables
Required environment variables in .env:
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_API_VERSION=
AZURE_LANGUAGE_ENDPOINT=
AZURE_LANGUAGE_KEY=
AZURE_DOCUMENT_ENDPOINT=
AZURE_DOCUMENT_KEY=
AZURE_VISION_ENDPOINT=
AZURE_VISION_KEY=
SECRET_KEY=

Database
SQLite with async support (aiosqlite)
Async SQLAlchemy for ORM
Migrations handled automatically on startup
Running the Application