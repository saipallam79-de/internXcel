from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base


class Module(Base):
    __tablename__ = "modules"
    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    module_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(String(500))
    is_locked: Mapped[bool] = mapped_column(Boolean, default=True)
    learning_objectives: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_duration: Mapped[int] = mapped_column(Integer, default=5)
    prerequisites: Mapped[str | None] = mapped_column(Text, nullable=True)
    resources: Mapped[str | None] = mapped_column(Text, nullable=True)


class ModuleCompletion(Base):
    __tablename__ = "module_completions"
    __table_args__ = (UniqueConstraint("internship_id", "module_id", name="uq_internship_module"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    internship_id: Mapped[int] = mapped_column(ForeignKey("internships.id"))
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    status: Mapped[str] = mapped_column(String(30), default="completed")
