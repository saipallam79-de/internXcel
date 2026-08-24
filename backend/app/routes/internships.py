from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dependencies import current_user
from app.database.session import get_db
from app.models.documents import OfferLetter
from app.models.internship import Domain, Internship
from app.models.user import User
from app.schemas.internship import InternshipApplyRequest, InternshipEnrollmentResponse, InternshipResponse
from app.services.enrollment_service import enroll_user

router = APIRouter(prefix="/api/internships", tags=["internships"])


@router.post("/apply", response_model=InternshipEnrollmentResponse, status_code=status.HTTP_201_CREATED)
def apply(payload: InternshipApplyRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        internship, offer = enroll_user(db, user, payload.domain_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    response = InternshipResponse.model_validate(internship)
    return InternshipEnrollmentResponse(**response.model_dump(), offer_id=offer.offer_id)


@router.get("/me", response_model=InternshipResponse)
def my_internship(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    return internship
