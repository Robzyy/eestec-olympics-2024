from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.endpoints import analysis, grading, auth, code_review, code_classification
from app.db.session import engine
from app.db.base_class import Base
from app.api.deps import get_current_user

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:80", "http://localhost"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Include routers with authentication
app.include_router(
    analysis.router,
    prefix="/api",
    tags=["analysis"],
    dependencies=[Depends(get_current_user)]  # Add auth to all analysis endpoints
)

app.include_router(
    grading.router,
    prefix="/api/grading",
    tags=["grading"],
    dependencies=[Depends(get_current_user)]  # Add auth to all grading endpoints
)

# Auth router doesn't need authentication
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["auth"]
)

# Include the code review router
app.include_router(
    code_review.router,
    prefix="/api/code-review",
    tags=["code-review"],
    dependencies=[Depends(get_current_user)]
)

# Include the code classification router
app.include_router(
    code_classification.router,
    prefix="/api/code-classification",
    tags=["code-review"]
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
