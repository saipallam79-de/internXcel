from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BACKEND_ROOT
from app.core.dependencies import admin_user, current_user
from app.database.session import get_db
from app.models.documents import Certificate, LORDocument, OfferLetter
from app.models.internship import Domain, Internship
from app.models.module import Module, ModuleCompletion
from app.models.task import Submission, Task
from app.models.user import User
from app.services.certificate_service import generate_certificate
from app.services.lor_service import generate_lor
from app.services.offer_letter_service import generate_personalized_offer_letter
from app.utils.id_generator import make_certificate_id, make_lor_id

router = APIRouter(prefix="/api/certificate", tags=["certificates"])
offer_router = APIRouter(prefix="/api/offer-letter", tags=["offer letters"])
lor_router = APIRouter(prefix="/api/lor", tags=["letters of recommendation"])


def get_owned_internship(internship_id: int, user: User, db: Session) -> tuple[Internship, Domain, User]:
    internship = db.get(Internship, internship_id)
    if not internship or (internship.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Internship not found")
    domain = db.get(Domain, internship.domain_id)
    student = db.get(User, internship.user_id)
    return internship, domain, student


def completion_eligibility(internship: Internship, db: Session) -> tuple[bool, dict[str, int]]:
    modules = list(db.scalars(select(Module).where(Module.domain_id == internship.domain_id)).all())
    completed_modules = db.scalar(select(ModuleCompletion.id).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed").order_by(ModuleCompletion.id.desc()))
    completed_count = len(db.scalars(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed")).all())
    tasks = list(db.scalars(select(Task).join(Module, Task.module_id == Module.id).where(Module.domain_id == internship.domain_id)).all())
    approved_count = sum(bool(db.scalar(select(Submission.id).where(Submission.task_id == task.id, Submission.user_id == internship.user_id, Submission.status == "approved"))) for task in tasks)
    ready = completed_count == len(modules) and approved_count == len(tasks) and len(modules) > 0
    return ready, {"completed_modules": completed_count, "total_modules": len(modules), "approved_tasks": approved_count, "total_tasks": len(tasks)}


@router.get("/verify/{certificate_id}")
def verify_certificate(certificate_id: str, db: Session = Depends(get_db)):
    certificate = db.scalar(select(Certificate).where(Certificate.certificate_id == certificate_id))
    if not certificate or certificate.status != "valid":
        raise HTTPException(status_code=404, detail="Certificate not found or invalid")
    internship = db.get(Internship, certificate.internship_id)
    domain = db.get(Domain, internship.domain_id)
    student = db.get(User, certificate.user_id)
    return {"certificate_id": certificate.certificate_id, "student": student.full_name, "domain": domain.name, "internship": "InternXcel", "status": certificate.status.upper(), "issue_date": certificate.issue_date}


@router.get("/me")
def certificate_preview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    ready, counts = completion_eligibility(internship, db)
    certificate = db.scalar(select(Certificate).where(Certificate.internship_id == internship.id))
    return {"unlocked": bool(certificate and certificate.status == "valid") or ready, "certificate_id": certificate.certificate_id if certificate else None, "issue_date": certificate.issue_date if certificate else None, "requirements": counts}


@router.post("/generate")
def generate_certificate_document(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship, domain, student = get_owned_internship(db.scalar(select(Internship.id).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"]))), user, db) if db.scalar(select(Internship.id).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"]))) else (None, None, None)
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    ready, counts = completion_eligibility(internship, db)
    if not ready:
        raise HTTPException(status_code=409, detail={"message": "Complete all modules and receive approval for all required tasks first.", "requirements": counts})
    certificate = db.scalar(select(Certificate).where(Certificate.internship_id == internship.id))
    if not certificate:
        certificate_id = make_certificate_id(date.today().year, internship.id)
        certificate = Certificate(user_id=student.id, internship_id=internship.id, certificate_id=certificate_id, issue_date=date.today())
        db.add(certificate)
        db.flush()
    path = BACKEND_ROOT / "uploads" / "certificates" / f"{certificate.certificate_id}.pdf"
    generate_certificate(str(path), student.full_name, domain.name, certificate.certificate_id, internship.intern_id, str(certificate.issue_date))
    certificate.pdf_path = str(path)
    db.commit()
    return {"certificate_id": certificate.certificate_id, "issue_date": certificate.issue_date, "status": certificate.status}


@router.get("/{certificate_id}/download")
def download_certificate(certificate_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    certificate = db.scalar(select(Certificate).where(Certificate.certificate_id == certificate_id, Certificate.status == "valid"))
    if not certificate or (certificate.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Certificate not found")
    internship, domain, student = get_owned_internship(certificate.internship_id, user, db)
    path = BACKEND_ROOT / "uploads" / "certificates" / f"{certificate.certificate_id}.pdf"
    generate_certificate(str(path), student.full_name, domain.name, certificate.certificate_id, internship.intern_id, str(certificate.issue_date))
    certificate.pdf_path = str(path)
    db.commit()
    return FileResponse(path, media_type="application/pdf", filename="internxcel-certificate.pdf")


@lor_router.get("/me")
def lor_preview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    ready, counts = completion_eligibility(internship, db)
    lor = db.scalar(select(LORDocument).where(LORDocument.internship_id == internship.id))
    return {"unlocked": bool(lor and lor.status == "valid") or ready, "document_id": lor.document_id if lor else None, "requirements": counts}


@lor_router.post("/generate")
def generate_lor_document(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship_id = db.scalar(select(Internship.id).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship_id:
        raise HTTPException(status_code=404, detail="No active internship")
    internship, domain, student = get_owned_internship(internship_id, user, db)
    ready, counts = completion_eligibility(internship, db)
    if not ready:
        raise HTTPException(status_code=409, detail={"message": "Complete the internship before requesting an LOR.", "requirements": counts})
    lor = db.scalar(select(LORDocument).where(LORDocument.internship_id == internship.id))
    if not lor:
        lor = LORDocument(user_id=student.id, internship_id=internship.id, document_id=make_lor_id(date.today().year, internship.id))
        db.add(lor)
        db.flush()
    path = BACKEND_ROOT / "uploads" / "lor" / f"{lor.document_id}.pdf"
    generate_lor(str(path), student.full_name, domain.name, internship.intern_id, domain.duration, "structured learning, practical problem solving, project delivery")
    lor.pdf_path = str(path)
    db.commit()
    return {"document_id": lor.document_id, "status": lor.status}


@lor_router.get("/{document_id}/download")
def download_lor(document_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    lor = db.scalar(select(LORDocument).where(LORDocument.document_id == document_id, LORDocument.status == "valid"))
    if not lor or (lor.user_id != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="LOR not found")
    internship, domain, student = get_owned_internship(lor.internship_id, user, db)
    path = BACKEND_ROOT / "uploads" / "lor" / f"{lor.document_id}.pdf"
    generate_lor(str(path), student.full_name, domain.name, internship.intern_id, domain.duration, "structured learning, practical problem solving, project delivery")
    lor.pdf_path = str(path)
    db.commit()
    return FileResponse(path, media_type="application/pdf", filename="internxcel-letter-of-recommendation.pdf")


@offer_router.get("/{internship_id}/download")
def download_offer_letter(internship_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship, domain, student = get_owned_internship(internship_id, user, db)
    offer = db.scalar(select(OfferLetter).where(OfferLetter.internship_id == internship_id))
    if not offer:
        offer = OfferLetter(user_id=student.id, internship_id=internship.id, offer_id=f"INTX-OFFER-{internship.intern_id.replace('/', '-')}")
        db.add(offer)
        db.commit()
        db.refresh(offer)
    path = BACKEND_ROOT / "uploads" / "offer_letters" / f"{offer.offer_id}.pdf"
    generate_personalized_offer_letter(str(path), student.full_name, domain.name, internship.intern_id, str(internship.start_date), str(internship.end_date), offer.offer_id, student.email)
    offer.pdf_path = str(path)
    db.commit()
    return FileResponse(path, media_type="application/pdf", filename="internxcel-offer-letter.pdf")


@offer_router.post("/generate-all")
def generate_all_offer_letters(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    internships = list(db.scalars(select(Internship).where(Internship.status.in_(["active", "completed"]))).all())
    generated = []
    for internship in internships:
        student = db.get(User, internship.user_id)
        domain = db.get(Domain, internship.domain_id)
        offer = db.scalar(select(OfferLetter).where(OfferLetter.internship_id == internship.id))
        if not offer:
            offer = OfferLetter(user_id=student.id, internship_id=internship.id, offer_id=f"INTX-OFFER-{internship.intern_id.replace('/', '-')}")
            db.add(offer)
            db.flush()
        path = BACKEND_ROOT / "uploads" / "offer_letters" / f"{offer.offer_id}.pdf"
        generate_personalized_offer_letter(str(path), student.full_name, domain.name, internship.intern_id, str(internship.start_date), str(internship.end_date), offer.offer_id, student.email)
        offer.pdf_path = str(path)
        generated.append({"internship_id": internship.id, "student": student.full_name, "offer_id": offer.offer_id, "file": str(path)})
    db.commit()
    return {"generated": len(generated), "offer_letters": generated}
