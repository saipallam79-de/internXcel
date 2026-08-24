from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import ProfileUpdateRequest, UserResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(user: User = Depends(current_user)):
    return user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(payload: ProfileUpdateRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    for key, value in payload.model_dump().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_profile(user_id: int, current: User = Depends(current_user), db: Session = Depends(get_db)):
    if current.role != "admin" and current.id != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You cannot access another student's profile")
    user = db.get(User, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user
