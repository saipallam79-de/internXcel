from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import current_user
from app.database.session import get_db
from app.models.internship import Internship
from app.models.module import Module, ModuleCompletion
from app.models.task import Task
from app.models.user import User

router = APIRouter(prefix="/api/modules", tags=["modules"])


def module_status(module: Module, modules: list[Module], completed_ids: set[int]) -> str:
    if module.id in completed_ids:
        return "completed"
    if module.module_number == 0 or (module.module_number - 1 in {item.module_number for item in modules if item.id in completed_ids}):
        return "available"
    return "locked"


@router.get("")
def list_modules(domain_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Module)
    if domain_id:
        query = query.where(Module.domain_id == domain_id)
    return list(db.scalars(query.order_by(Module.module_number)).all())


@router.get("/learning-path/{internship_id}")
def learning_path(internship_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.get(Internship, internship_id)
    if not internship or internship.user_id != user.id:
        raise HTTPException(status_code=404, detail="Internship not found")
    modules = list(db.scalars(select(Module).where(Module.domain_id == internship.domain_id).order_by(Module.module_number)).all())
    completed_ids = set(db.scalars(select(ModuleCompletion.module_id).where(ModuleCompletion.internship_id == internship_id, ModuleCompletion.status == "completed")).all())
    return [{"id": module.id, "module_number": module.module_number, "title": module.title, "description": module.description, "learning_objectives": module.learning_objectives, "estimated_duration": module.estimated_duration, "prerequisites": module.prerequisites, "resources": module.resources, "status": module_status(module, modules, completed_ids)} for module in modules]


@router.get("/{module_id}")
def module_detail(module_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    module = db.get(Module, module_id)
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status.in_(["active", "completed"])))
    if not module or not internship or module.domain_id != internship.domain_id:
        raise HTTPException(status_code=404, detail="Module not found in your internship")
    modules = list(db.scalars(select(Module).where(Module.domain_id == internship.domain_id).order_by(Module.module_number)).all())
    completed_ids = set(db.scalars(select(ModuleCompletion.module_id).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed")).all())
    tasks = list(db.scalars(select(Task).where(Task.module_id == module.id)).all())
    return {"id": module.id, "module_number": module.module_number, "title": module.title, "description": module.description, "learning_objectives": module.learning_objectives, "estimated_duration": module.estimated_duration, "prerequisites": module.prerequisites, "resources": module.resources, "status": module_status(module, modules, completed_ids), "tasks": tasks}


@router.post("/{module_id}/complete")
def complete_module(module_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    module = db.get(Module, module_id)
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status == "active"))
    if not module or not internship or module.domain_id != internship.domain_id:
        raise HTTPException(status_code=404, detail="Module or internship not found")
    tasks = list(db.scalars(select(Task).where(Task.module_id == module_id)).all())
    if tasks:
        from app.models.task import Submission
        for task in tasks:
            approved = db.scalar(select(Submission).where(Submission.task_id == task.id, Submission.user_id == user.id, Submission.status == "approved"))
            if not approved:
                raise HTTPException(status_code=409, detail="Submit and receive approval for every task before completing this module")
    previous = db.scalar(select(Module).where(Module.domain_id == module.domain_id, Module.module_number == module.module_number - 1))
    if previous and not db.scalar(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.module_id == previous.id, ModuleCompletion.status == "completed")):
        raise HTTPException(status_code=409, detail="Complete the previous module before unlocking this one")
    completion = db.scalar(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.module_id == module_id))
    if not completion:
        db.add(ModuleCompletion(internship_id=internship.id, module_id=module_id))
    total = len(db.scalars(select(Module).where(Module.domain_id == internship.domain_id)).all())
    completed = len(db.scalars(select(ModuleCompletion).where(ModuleCompletion.internship_id == internship.id, ModuleCompletion.status == "completed")).all()) + (0 if completion else 1)
    internship.progress = round((completed / total) * 100) if total else 0
    if completed >= total:
        internship.status = "completed"
    db.commit()
    return {"status": "completed", "progress": internship.progress, "internship_status": internship.status}
