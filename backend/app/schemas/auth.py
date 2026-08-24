from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    mobile: str
    college: str
    degree: str
    branch: str
    year: int
    password: str = Field(min_length=8)
    domain_id: int | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile: str
    college: str
    degree: str
    branch: str
    year: int
    role: str
    status: str

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    mobile: str
    college: str
    degree: str
    branch: str
    year: int
