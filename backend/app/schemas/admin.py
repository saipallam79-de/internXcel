from pydantic import BaseModel, Field


class DomainCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    description: str = Field(min_length=5, max_length=500)
    duration: int = Field(default=30, ge=1, le=365)


class DomainUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    description: str | None = Field(default=None, min_length=5, max_length=500)
    duration: int | None = Field(default=None, ge=1, le=365)
    status: str | None = None


class ModuleCreate(BaseModel):
    domain_id: int
    module_number: int = Field(ge=1)
    title: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=2, max_length=500)
    learning_objectives: str | None = None
    estimated_duration: int = Field(default=5, ge=1, le=90)
    prerequisites: str | None = None
    resources: str | None = None


class ReviewRequest(BaseModel):
    status: str
    admin_comment: str | None = None