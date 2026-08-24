from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import current_user
from app.database.session import get_db
from app.models.documents import Certificate, OfferLetter
from app.models.gamification import Notification, StudentReward
from app.models.internship import Domain, Internship
from app.models.module import Module, ModuleCompletion
from app.models.task import Submission, Task
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    domain = db.get(Domain, internship.domain_id)
    modules = list(db.scalars(select(Module).where(Module.domain_id == internship.domain_id).order_by(Module.module_number)).all())
    completed_ids = set(db.scalars(select(ModuleCompletion.module_id).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed")).all())
    current_module = next((module for module in modules if module.id not in completed_ids), None)
    submitted_tasks = db.scalar(select(func.count(Submission.id)).join(Task, Submission.task_id == Task.id).join(Module, Task.module_id == Module.id).where(Submission.user_id == user.id, Module.domain_id == internship.domain_id, Submission.status.in_(["pending_review", "approved"]))) or 0
    completed_tasks = db.scalar(select(func.count(Submission.id)).join(Task, Submission.task_id == Task.id).join(Module, Task.module_id == Module.id).where(Submission.user_id == user.id, Module.domain_id == internship.domain_id, Submission.status == "approved")) or 0
    total_tasks = db.scalar(select(func.count(Task.id)).join(Module, Task.module_id == Module.id).where(Module.domain_id == internship.domain_id)) or 0
    offer = db.scalar(select(OfferLetter).where(OfferLetter.internship_id == internship.id))
    certificate = db.scalar(select(Certificate).where(Certificate.internship_id == internship.id))
    rewards = list(db.scalars(select(StudentReward).where(StudentReward.user_id == user.id).order_by(StudentReward.awarded_at.desc())).all())
    notifications = list(db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(5)).all())
    return {
        "student": {"id": user.id, "name": user.full_name, "email": user.email},
        "internship": {"id": internship.id, "domain": domain.name, "intern_id": internship.intern_id, "status": internship.status, "progress": internship.progress, "start_date": internship.start_date, "end_date": internship.end_date},
        "modules": {"completed": len(completed_ids), "total": len(modules), "current": {"id": current_module.id, "title": current_module.title, "module_number": current_module.module_number} if current_module else None},
        "tasks": {"total": total_tasks, "completed": completed_tasks, "pending": max(total_tasks - completed_tasks, 0), "submitted": submitted_tasks},
        "documents": {"offer_letter": bool(offer), "certificate": bool(certificate and certificate.status == "valid"), "certificate_id": certificate.certificate_id if certificate else None},
        "rewards": {"points": sum(reward.points for reward in rewards), "badges": [reward.badge for reward in rewards]},
        "notifications": [{"title": item.title, "message": item.message, "is_read": item.is_read} for item in notifications],
    }