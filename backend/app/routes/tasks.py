from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import admin_user, current_user
from app.database.session import get_db
from app.models.internship import Internship
from app.models.module import Module, ModuleCompletion
from app.models.task import Submission, Task
from app.models.user import User
from app.schemas.task import TaskSubmissionRequest

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks(module_id: int | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not internship:
        raise HTTPException(status_code=404, detail="No active internship")
    query = select(Task).join(Module, Task.module_id == Module.id).where(Module.domain_id == internship.domain_id)
    if module_id:
        query = query.where(Task.module_id == module_id)
    modules = list(db.scalars(select(Module).where(Module.domain_id == internship.domain_id).order_by(Module.module_number)).all())
    completed_ids = set(db.scalars(select(ModuleCompletion.module_id).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed")).all())
    module_by_id = {module.id: module for module in modules}
    tasks = list(db.scalars(query.order_by(Module.module_number, Task.id)).all())
    return [{
        "id": task.id,
        "module_id": task.module_id,
        "module_number": module_by_id[task.module_id].module_number,
        "module_title": module_by_id[task.module_id].title,
        "title": task.title,
        "description": task.description,
        "instructions": task.instructions,
        "submission_type": task.submission_type,
        "required_links": task.required_links,
        "status": "completed" if db.scalar(select(Submission.id).where(Submission.task_id == task.id, Submission.user_id == user.id, Submission.status == "approved")) else "pending",
        "module_status": _module_status(module_by_id[task.module_id], modules, completed_ids),
    } for task in tasks]


def _module_status(module: Module, modules: list[Module], completed_ids: set[int]) -> str:
    if module.id in completed_ids:
        return "completed"
    if module.module_number == 0 or (module.module_number - 1 in {item.module_number for item in modules if item.id in completed_ids}):
        return "available"
    return "locked"


@router.post("/{task_id}/submit")
def submit_task(task_id: int, payload: TaskSubmissionRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status == "active"))
    if not task or not internship:
        raise HTTPException(status_code=404, detail="Task not found")
    module = db.get(Module, task.module_id)
    if not module or module.domain_id != internship.domain_id:
        raise HTTPException(status_code=403, detail="Task is outside your internship")
    if not any([payload.github_url, payload.live_url, payload.linkedin_url, payload.text_response]):
        raise HTTPException(status_code=422, detail="Provide at least one submission item")
    if task.submission_type == "linkedin_url" and not payload.linkedin_url:
        raise HTTPException(status_code=422, detail="Submit the LinkedIn post URL for onboarding")
    submission = Submission(task_id=task.id, user_id=user.id, github_url=str(payload.github_url) if payload.github_url else None, live_url=str(payload.live_url) if payload.live_url else None, linkedin_url=str(payload.linkedin_url) if payload.linkedin_url else None, text_response=payload.text_response, status="pending_review")
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.patch("/{submission_id}/review")
def review_submission(submission_id: int, status: str, admin_comment: str | None = None, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if status not in {"approved", "rejected", "changes_requested"}:
        raise HTTPException(status_code=422, detail="Invalid review status")
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission.status = status
    submission.admin_comment = admin_comment
    if status == "approved":
        db.flush()
        module = db.scalar(select(Module).join(Task, Task.module_id == Module.id).where(Task.id == submission.task_id))
        internship = db.scalar(select(Internship).where(Internship.user_id == submission.user_id, Internship.status == "active"))
        if module and internship:
            module_tasks = list(db.scalars(select(Task).where(Task.module_id == module.id)).all())
            all_approved = all(db.scalar(select(Submission).where(Submission.task_id == task.id, Submission.user_id == submission.user_id, Submission.status == "approved")) for task in module_tasks)
            previous = db.scalar(select(Module).where(Module.domain_id == module.domain_id, Module.module_number == module.module_number - 1))
            previous_done = not previous or db.scalar(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.module_id == previous.id, ModuleCompletion.status == "completed"))
            if all_approved and previous_done and not db.scalar(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.module_id == module.id)):
                db.add(ModuleCompletion(internship_id=internship.id, module_id=module.id))
                total = len(db.scalars(select(Module).where(Module.domain_id == internship.domain_id)).all())
                completed = len(db.scalars(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed")).all()) + 1
                internship.progress = round((completed / total) * 100) if total else 0
                if completed >= total:
                    internship.status = "completed"
    db.commit()
    return submission
