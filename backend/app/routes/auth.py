from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database.session import get_db
from app.models.internship import Domain
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.enrollment_service import enroll_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    if payload.domain_id is not None and not db.scalar(select(Domain).where(Domain.id == payload.domain_id, Domain.status == "active")):
        raise HTTPException(status_code=404, detail="Selected internship domain is unavailable")
    user = User(**payload.model_dump(exclude={"password", "domain_id"}), password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    if payload.domain_id is not None:
        try:
            enroll_user(db, user, payload.domain_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserResponse)
def get_current_user(user: User = Depends(current_user)):
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
