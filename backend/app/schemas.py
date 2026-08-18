from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GenerateApplicationRequest(BaseModel):
    recruiter_name: str = Field(min_length=1, max_length=255)
    recruiter_email: EmailStr
    company_name: str = Field(min_length=1, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    job_description: str = Field(min_length=1)
    additional_context: str = Field(default="", max_length=2000)


class GenerateApplicationResponse(BaseModel):
    subject: str
    body: str


class SendApplicationRequest(BaseModel):
    recruiter_name: str = Field(min_length=1, max_length=255)
    recruiter_email: EmailStr
    company_name: str = Field(min_length=1, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1)


class SendApplicationResponse(BaseModel):
    success: bool
    message: str
    gmail_message_id: str
    gmail_thread_id: str
    sent_email_id: int | None
    db_persisted: bool

    model_config = ConfigDict(from_attributes=True)


class ApplicationListItemResponse(BaseModel):
    id: int
    recruiter_name: str
    recruiter_email: EmailStr
    company_name: str
    job_title: str
    subject: str
    body: str
    gmail_message_id: str
    gmail_thread_id: str
    status: str
    sent_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
