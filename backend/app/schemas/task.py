from pydantic import BaseModel, HttpUrl


class TaskSubmissionRequest(BaseModel):
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    linkedin_url: HttpUrl | None = None
    text_response: str | None = None