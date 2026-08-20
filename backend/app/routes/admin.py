from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.dependencies import admin_user
from app.database.session import get_db
from app.models.documents import Certificate
from app.models.internship import Domain, Internship
from app.models.module import Module
from app.models.task import Submission, Task
from app.models.user import User
from app.schemas.admin import DomainCreate, DomainUpdate, ModuleCreate, ReviewRequest

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def stats(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return {
        "total_students": db.scalar(select(func.count(User.id)).where(User.role == "student")) or 0,
        "active_interns": db.scalar(select(func.count(Internship.id)).where(Internship.status == "active")) or 0,
        "completed_internships": db.scalar(select(func.count(Internship.id)).where(Internship.status == "completed")) or 0,
        "pending_reviews": db.scalar(select(func.count(Submission.id)).where(Submission.status == "pending_review")) or 0,
        "certificates_issued": db.scalar(select(func.count(Certificate.id)).where(Certificate.status == "valid")) or 0,
        "domains": db.scalar(select(func.count(Domain.id)).where(Domain.status == "active")) or 0,
        "modules": db.scalar(select(func.count(Module.id))) or 0,
    }


@router.get("/students")
def students(search: str | None = None, domain_id: int | None = None, status: str | None = None, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    query = select(User, Internship, Domain).join(Internship, Internship.user_id == User.id, isouter=True).join(Domain, Domain.id == Internship.domain_id, isouter=True).where(User.role == "student")
    if search:
        query = query.where(or_(User.full_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"), User.college.ilike(f"%{search}%")))
    if domain_id:
        query = query.where(Internship.domain_id == domain_id)
    if status:
        query = query.where(User.status == status)
    return [{"id": user.id, "name": user.full_name, "email": user.email, "college": user.college, "status": user.status, "domain": domain.name if domain else None, "intern_id": internship.intern_id if internship else None, "progress": internship.progress if internship else 0, "internship_status": internship.status if internship else "not_enrolled"} for user, internship, domain in db.execute(query).all()]


@router.patch("/students/{user_id}/status")
def student_status(user_id: int, status: str, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if status not in {"active", "suspended"}:
        raise HTTPException(status_code=422, detail="Status must be active or suspended")
    user = db.get(User, user_id)
    if not user or user.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")
    user.status = status
    db.commit()
    return {"id": user.id, "status": user.status}


@router.get("/domains")
def admin_domains(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(Domain).order_by(Domain.name)).all())


@router.post("/domains", status_code=201)
def create_domain(payload: DomainCreate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if db.scalar(select(Domain).where(Domain.name == payload.name)):
        raise HTTPException(status_code=409, detail="Domain already exists")
    domain = Domain(**payload.model_dump())
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return domain


@router.patch("/domains/{domain_id}")
def update_domain(domain_id: int, payload: DomainUpdate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    domain = db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "status" and value not in {"active", "inactive"}:
            raise HTTPException(status_code=422, detail="Domain status must be active or inactive")
        setattr(domain, key, value)
    db.commit()
    return domain


@router.delete("/domains/{domain_id}")
def delete_domain(domain_id: int, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    domain = db.get(Domain, domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if db.scalar(select(Internship).where(Internship.domain_id == domain_id)):
        raise HTTPException(status_code=409, detail="Cannot delete a domain with internship records; deactivate it instead")
    db.delete(domain)
    db.commit()
    return {"deleted": True}


@router.get("/modules")
def admin_modules(domain_id: int | None = None, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    query = select(Module).order_by(Module.domain_id, Module.module_number)
    if domain_id:
        query = query.where(Module.domain_id == domain_id)
    return list(db.scalars(query).all())


@router.post("/modules", status_code=201)
def create_module(payload: ModuleCreate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if not db.get(Domain, payload.domain_id):
        raise HTTPException(status_code=404, detail="Domain not found")
    module = Module(**payload.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.patch("/modules/{module_id}")
def update_module(module_id: int, payload: ModuleCreate, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    module = db.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    for key, value in payload.model_dump().items():
        setattr(module, key, value)
    db.commit()
    return module


@router.delete("/modules/{module_id}")
def delete_module(module_id: int, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    module = db.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if db.scalar(select(Task).where(Task.module_id == module_id)):
        raise HTTPException(status_code=409, detail="Cannot delete a module with tasks")
    db.delete(module)
    db.commit()
    return {"deleted": True}


@router.get("/submissions")
def submissions(status: str | None = None, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    query = select(Submission, Task, Module, Domain, User).join(Task, Submission.task_id == Task.id).join(Module, Task.module_id == Module.id).join(Domain, Module.domain_id == Domain.id).join(User, Submission.user_id == User.id).order_by(Submission.submitted_at.desc())
    if status:
        query = query.where(Submission.status == status)
    return [{"id": submission.id, "student": student.full_name, "email": student.email, "domain": domain.name, "module": module.title, "task": task.title, "submitted_at": submission.submitted_at, "github_url": submission.github_url, "live_url": submission.live_url, "status": submission.status, "admin_comment": submission.admin_comment} for submission, task, module, domain, student in db.execute(query).all()]


@router.patch("/submissions/{submission_id}/review")
def review_submission(submission_id: int, payload: ReviewRequest, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if payload.status not in {"approved", "rejected", "changes_requested"}:
        raise HTTPException(status_code=422, detail="Invalid review status")
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission.status = payload.status
    submission.admin_comment = payload.admin_comment
    db.commit()
    return {"id": submission.id, "status": submission.status, "admin_comment": submission.admin_comment}
