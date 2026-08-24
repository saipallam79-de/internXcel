from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_ROOT
from app.models.documents import OfferLetter
from app.models.internship import Domain, Internship
from app.models.user import User
from app.services.offer_letter_service import generate_personalized_offer_letter
from app.utils.id_generator import make_unique_intern_id


def enroll_user(db: Session, user: User, domain_id: int) -> tuple[Internship, OfferLetter]:
    domain = db.scalar(select(Domain).where(Domain.id == domain_id, Domain.status == "active"))
    if not domain:
        raise ValueError("Selected internship domain is unavailable")
    existing = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if existing:
        offer = db.scalar(select(OfferLetter).where(OfferLetter.internship_id == existing.id))
        if not offer:
            offer = OfferLetter(user_id=user.id, internship_id=existing.id, offer_id=f"INTX-OFFER-{existing.intern_id.replace('/', '-')}")
            db.add(offer)
            db.commit()
            db.refresh(offer)
        return existing, offer
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
    return internship, offer
