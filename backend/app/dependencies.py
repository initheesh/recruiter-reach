from app.config import get_settings
from app.services.gmail_service import GmailService
from app.services.llm_service import LLMService
from app.services.resume_service import ResumeService


def get_llm_service() -> LLMService:
    settings = get_settings()
    return LLMService(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        provider=settings.llm_provider,
        open_router_api_key=settings.open_router_api_key,
        open_router_model=settings.open_router_model,
        candidate_name=settings.candidate_name,
        candidate_linkedin_url=settings.candidate_linkedin_url,
    )


def get_gmail_service() -> GmailService:
    settings = get_settings()
    return GmailService(
        credentials_path=settings.gmail_credentials_path,
        token_path=settings.gmail_token_path,
        oauth_host=settings.gmail_oauth_host,
        oauth_port=settings.gmail_oauth_port,
    )


def get_resume_service() -> ResumeService:
    return ResumeService()
