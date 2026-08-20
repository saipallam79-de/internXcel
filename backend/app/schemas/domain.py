from pydantic import BaseModel


class DomainResponse(BaseModel):
    id: int
    name: str
    description: str
    duration: int
    status: str

    model_config = {"from_attributes": True}
