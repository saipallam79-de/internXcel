from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=5, max_length=2000)
    learned: str | None = Field(default=None, max_length=2000)
    recommend: bool = True


class SupportRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=180)
    category: str = Field(min_length=2, max_length=60)
    message: str = Field(min_length=5, max_length=3000)


class SupportReply(BaseModel):
    status: str
    admin_reply: str | None = None