import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.dependencies import get_gmail_service, get_llm_service, get_resume_service
from app.models import SentEmail, SentEmailStatus
from app.schemas import (
    ApplicationListItemResponse,
    GenerateApplicationRequest,
    GenerateApplicationResponse,
    SendApplicationRequest,
    SendApplicationResponse,
)
from app.services.gmail_service import GmailOAuthError, GmailSendError, GmailService
from app.services.llm_service import LLMService, LLMServiceError
from app.services.resume_service import ResumeService, ResumeServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationListItemResponse])
def get_all_applications(
    db: Annotated[Session, Depends(get_db)],
) -> list[ApplicationListItemResponse]:
    try:
        records = (
            db.execute(select(SentEmail).order_by(SentEmail.sent_at.desc(), SentEmail.id.desc()))
            .scalars()
            .all()
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to fetch applications")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications.",
        ) from exc

    return records


@router.post("/generate", response_model=GenerateApplicationResponse)
def generate_application_email(
    request: GenerateApplicationRequest,
    llm_service: Annotated[LLMService, Depends(get_llm_service)],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
) -> GenerateApplicationResponse:
    try:
        resume_profile = resume_service.get_or_create_resume_profile(llm_service=llm_service)
        relevant_context = resume_service.select_relevant_resume_context(
            profile=resume_profile,
            job_description=request.job_description,
        )

        generated = llm_service.generate_application_email(
            recruiter_name=request.recruiter_name,
            recruiter_email=request.recruiter_email,
            company_name=request.company_name,
            job_title=request.job_title,
            job_description=request.job_description,
            additional_context=request.additional_context,
            relevant_profile_context=relevant_context,
        )
    except ResumeServiceError as exc:
        logger.exception("Resume profile preparation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except LLMServiceError as exc:
        logger.exception("LLM generation failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate email content from LLM.",
        ) from exc

    return GenerateApplicationResponse(subject=generated["subject"], body=generated["body"])

    # -----------------TEST (kept commented as requested)-----------------
    # subject = f"Application for {request.job_title} at {request.company_name}"

    # body = (
    #     f"Hi {request.recruiter_name},\n\n"
    #     f"I hope you are doing well. I am reaching out to express my interest in the "
    #     f"{request.job_title} role at {request.company_name}.\n\n"
    #     "Based on the job description, this opportunity aligns well with my background "
    #     "and interests. I would appreciate the opportunity to be considered for this "
    #     "position.\n\n"
    #     "I have attached my resume for your review. Please let me know if you would like "
    #     "any additional details.\n\n"
    #     "Thank you for your time and consideration.\n"
    # )

    # return GenerateApplicationResponse(subject=subject, body=body)


@router.post("/send", response_model=SendApplicationResponse)
def send_application_email(
    request: SendApplicationRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    gmail_service: Annotated[GmailService, Depends(get_gmail_service)],
    db: Annotated[Session, Depends(get_db)],
) -> SendApplicationResponse:
    resume_path = Path(settings.resume_path) if settings.resume_path else None
    if not resume_path:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RESUME_PATH is not configured.",
        )

    if not resume_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume file not found at RESUME_PATH.",
        )

    if not resume_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RESUME_PATH must point to a file.",
        )

    try:
        gmail_message_id, gmail_thread_id = gmail_service.send_email(
            to_email=request.recruiter_email,
            subject=request.subject,
            body_text=request.body,
            attachment_path=str(resume_path),
        )
    except GmailOAuthError as exc:
        logger.exception("Gmail OAuth failure")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Gmail OAuth authentication failed.",
        ) from exc
    except GmailSendError as exc:
        logger.exception("Gmail send failure")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send email through Gmail API.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during Gmail send")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unexpected error while sending email.",
        ) from exc

    sent_email = SentEmail(
        recruiter_name=request.recruiter_name,
        recruiter_email=request.recruiter_email,
        company_name=request.company_name,
        job_title=request.job_title,
        subject=request.subject,
        body=request.body,
        gmail_message_id=gmail_message_id,
        gmail_thread_id=gmail_thread_id,
        status=SentEmailStatus.SENT.value,
        sent_at=datetime.now(timezone.utc),
    )

    try:
        db.add(sent_email)
        db.commit()
        db.refresh(sent_email)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database insert failed for sent email")
        return SendApplicationResponse(
            success=True,
            message="Email sent successfully, but failed to store history record.",
            gmail_message_id=gmail_message_id,
            gmail_thread_id=gmail_thread_id,
            sent_email_id=None,
            db_persisted=False,
        )

    return SendApplicationResponse(
        success=True,
        message="Email sent successfully",
        gmail_message_id=gmail_message_id,
        gmail_thread_id=gmail_thread_id,
        sent_email_id=sent_email.id,
        db_persisted=True,
    )
