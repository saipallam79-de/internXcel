from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User


def current_user_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    subject = decode_access_token(authorization.removeprefix("Bearer "))
    if not subject:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return int(subject)


def current_user(user_id: int = Depends(current_user_id), db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Account not found")
    return user


def admin_user(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
