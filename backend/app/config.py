import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    resume_path: str
    candidate_name: str
    candidate_linkedin_url: str
    gmail_credentials_path: str
    gmail_token_path: str
    gmail_oauth_host: str
    gmail_oauth_port: int
    llm_provider: str
    llm_api_key: str
    llm_model: str

    open_router_model: str
    open_router_api_key: str


@lru_cache
def get_settings() -> Settings:
    oauth_port = int(os.getenv("GMAIL_OAUTH_PORT", "8000"))
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres",
        ),
        resume_path=os.getenv("RESUME_PATH", ""),
        candidate_name=os.getenv("CANDIDATE_NAME", ""),
        candidate_linkedin_url=os.getenv("CANDIDATE_LINKEDIN_URL", ""),
        gmail_credentials_path=os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"),
        gmail_token_path=os.getenv("GMAIL_TOKEN_PATH", "token.json"),
        gmail_oauth_host=os.getenv("GMAIL_OAUTH_HOST", "localhost"),
        gmail_oauth_port=oauth_port,
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_api_key=os.getenv("LLM_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        open_router_model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        open_router_api_key=os.getenv("OPENROUTER_API_KEY", ""),
    )
