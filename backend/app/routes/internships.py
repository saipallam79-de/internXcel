from datetime import date, timedelta
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import BACKEND_ROOT
from app.core.dependencies import current_user
from app.database.session import get_db
from app.models.documents import OfferLetter
from app.models.internship import Domain, Internship
from app.models.user import User
from app.schemas.internship import InternshipApplyRequest, InternshipEnrollmentResponse, InternshipResponse
from app.services.offer_letter_service import generate_personalized_offer_letter
from app.utils.id_generator import make_unique_intern_id

router = APIRouter(prefix="/api/internships", tags=["internships"])


@router.post("/apply", response_model=InternshipEnrollmentResponse, status_code=status.HTTP_201_CREATED)
def apply(payload: InternshipApplyRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    domain = db.scalar(select(Domain).where(Domain.id == payload.domain_id, Domain.status == "active"))
    if not domain:
        raise HTTPException(status_code=404, detail="Selected internship domain is unavailable")
    existing = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if existing:
        offer = db.scalar(select(OfferLetter).where(OfferLetter.internship_id == existing.id))
        if not offer:
            offer = OfferLetter(user_id=user.id, internship_id=existing.id, offer_id=f"INTX-OFFER-{existing.intern_id.replace('/', '-')}")
            db.add(offer)
            db.commit()
            db.refresh(offer)
        response = InternshipResponse.model_validate(existing)
        return InternshipEnrollmentResponse(**response.model_dump(), offer_id=offer.offer_id)
    start = date.today()
    intern_id = make_unique_intern_id(start.year)
    while db.scalar(select(Internship).where(Internship.intern_id == intern_id)):
        intern_id = make_unique_intern_id(start.year)
    internship = Internship(user_id=user.id, domain_id=domain.id, intern_id=intern_id, start_date=start, end_date=start + timedelta(days=domain.duration), progress=0)
    db.add(internship)
    db.flush()
    offer = OfferLetter(user_id=user.id, internship_id=internship.id, offer_id=f"INTX-OFFER-{intern_id.replace('/', '-')}")
    db.add(offer)
    db.commit()
    db.refresh(internship)
    db.refresh(offer)
    output = BACKEND_ROOT / "uploads" / "offer_letters" / f"{offer.offer_id}.pdf"
    generate_personalized_offer_letter(str(output), user.full_name, domain.name, intern_id, str(start), str(internship.end_date), offer.offer_id, user.email)
    offer.pdf_path = str(output)
    db.commit()
    response = InternshipResponse.model_validate(internship)
    return InternshipEnrollmentResponse(**response.model_dump(), offer_id=offer.offer_id)


@router.get("/me", response_model=InternshipResponse)
def my_internship(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    return internship
