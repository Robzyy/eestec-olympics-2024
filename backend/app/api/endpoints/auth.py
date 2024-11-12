from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.security import (
    create_access_token, 
    verify_password, 
    get_password_hash,
    get_current_user,
    oauth2_scheme
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, Token, UserUpdate
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    query = select(User).where(
        or_(User.email == user.email, User.username == user.username)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create new user
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserInDB)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.put("/users/me", response_model=UserInDB)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    for field, value in user_update.dict(exclude_unset=True).items():
        if field == "password" and value:
            value = get_password_hash(value)
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user