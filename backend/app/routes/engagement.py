from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import admin_user, current_user
from app.database.session import get_db
from app.models.gamification import Feedback, Notification, StudentReward, SupportTicket
from app.models.internship import Domain, Internship
from app.models.module import ModuleCompletion
from app.models.user import User
from app.schemas.engagement import FeedbackRequest, SupportReply, SupportRequest

router = APIRouter(prefix="/api", tags=["engagement"])


@router.get("/rewards/me")
def rewards(user: User = Depends(current_user), db: Session = Depends(get_db)):
    earned = list(db.scalars(select(StudentReward).where(StudentReward.user_id == user.id).order_by(StudentReward.awarded_at.desc())).all())
    points = sum(item.points for item in earned)
    totals = [value for value in db.scalars(select(func.coalesce(func.sum(StudentReward.points), 0)).group_by(StudentReward.user_id)).all()]
    rank = sum(value > points for value in totals) + 1
    return {"points": points, "rank": rank, "badges": [{"name": item.badge, "points": item.points, "awarded_at": item.awarded_at} for item in earned]}


@router.get("/leaderboard")
def leaderboard(_: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(select(User, func.coalesce(func.sum(StudentReward.points), 0).label("points"), func.count(ModuleCompletion.id).label("completed_modules")).join(Internship, Internship.user_id == User.id, isouter=True).join(StudentReward, StudentReward.user_id == User.id, isouter=True).join(ModuleCompletion, ModuleCompletion.internship_id == Internship.id, isouter=True).where(User.role == "student").group_by(User.id).order_by(func.coalesce(func.sum(StudentReward.points), 0).desc()).limit(20)).all()
    return [{"rank": index, "student": user.full_name.split(" ")[0] + (f" {user.full_name.split(' ')[-1][0]}." if len(user.full_name.split()) > 1 else ""), "domain": None, "points": int(points), "completed_modules": completed_modules} for index, (user, points, completed_modules) in enumerate(rows, 1)]


@router.get("/notifications/me")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = list(db.scalars(select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc()).limit(30)).all())
    return items


@router.patch("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.get(Notification, notification_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    item.is_read = True
    db.commit()
    return {"id": item.id, "is_read": item.is_read}


@router.post("/feedback", status_code=201)
def submit_feedback(payload: FeedbackRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    internship = db.scalar(select(Internship).where(Internship.user_id == user.id, Internship.status == "completed"))
    if not internship:
        raise HTTPException(status_code=409, detail="Feedback unlocks after internship completion")
    existing = db.scalar(select(Feedback).where(Feedback.user_id == user.id, Feedback.internship_id == internship.id))
    if existing:
        raise HTTPException(status_code=409, detail="Feedback has already been submitted")
    feedback = Feedback(user_id=user.id, internship_id=internship.id, **payload.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"id": feedback.id, "message": "Thank you for your feedback"}


@router.post("/support", status_code=201)
def create_support_ticket(payload: SupportRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    ticket = SupportTicket(user_id=user.id, **payload.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"id": ticket.id, "status": ticket.status, "message": "Support ticket created"}


@router.get("/support/me")
def my_support_tickets(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(SupportTicket).where(SupportTicket.user_id == user.id).order_by(SupportTicket.created_at.desc())).all())


@router.get("/admin/support")
def admin_support(_: User = Depends(admin_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(SupportTicket).order_by(SupportTicket.created_at.desc())).all())


@router.patch("/admin/support/{ticket_id}")
def reply_support(ticket_id: int, payload: SupportReply, _: User = Depends(admin_user), db: Session = Depends(get_db)):
    if payload.status not in {"open", "in_progress", "resolved"}:
        raise HTTPException(status_code=422, detail="Invalid support status")
    ticket = db.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    ticket.status = payload.status
    ticket.admin_reply = payload.admin_reply
    db.commit()
    return {"id": ticket.id, "status": ticket.status, "admin_reply": ticket.admin_reply}
