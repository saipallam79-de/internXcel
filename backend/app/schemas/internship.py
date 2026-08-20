from datetime import date
from pydantic import BaseModel


class InternshipResponse(BaseModel):
    id: int
    intern_id: str
    domain_id: int
    start_date: date | None
    end_date: date | None
    status: str
    progress: int

    model_config = {"from_attributes": True}


class InternshipApplyRequest(BaseModel):
    domain_id: int


class InternshipEnrollmentResponse(InternshipResponse):
    offer_id: str
