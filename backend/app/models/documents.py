from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base


class OfferLetter(Base):
    __tablename__ = "offer_letters"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"))
    offer_id: Mapped[str] = mapped_column(String(50), unique=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Certificate(Base):
    __tablename__ = "certificates"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"))
    certificate_id: Mapped[str] = mapped_column(String(50), unique=True)
    issue_date: Mapped[date] = mapped_column(Date)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="valid")


class LORDocument(Base):
    __tablename__ = "lor_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"))
    document_id: Mapped[str] = mapped_column(String(50), unique=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="valid")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
