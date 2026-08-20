from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.internship import Domain
from app.schemas.domain import DomainResponse

router = APIRouter(prefix="/api/domains", tags=["domains"])


@router.get("", response_model=list[DomainResponse])
def list_domains(db: Session = Depends(get_db)):
    return list(db.scalars(select(Domain).where(Domain.status == "active")).all())


@router.get("/{domain_id}", response_model=DomainResponse)
def get_domain(domain_id: int, db: Session = Depends(get_db)):
    return db.get(Domain, domain_id)
