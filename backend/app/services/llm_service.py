import json
import logging
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Raised when LLM content generation fails."""


class LLMService:
    def __init__(
        self,
        api_key: str,
        model: str,
        provider: str = "openai",
        open_router_api_key: str = "",
        open_router_model: str = "",
        candidate_name: str = "",
        candidate_linkedin_url: str = "",
    ) -> None:
        # Allow OpenRouter fallback when default LLM key is intentionally left empty.
        normalized_provider = provider.lower().strip()

        if normalized_provider == "openrouter" or (not api_key and open_router_api_key):
            self.provider = "openrouter"
            self.api_key = open_router_api_key
            self.model = open_router_model or model
        else:
            self.provider = "openai"
            self.api_key = api_key
            self.model = model

        self.candidate_name = candidate_name.strip()
        self.candidate_linkedin_url = candidate_linkedin_url.strip()

        logger.info(
            "LLMService initialized with provider=%s model=%s",
            self.provider,
            self.model,
        )

    def _create_client(self) -> OpenAI:
        if not self.api_key:
            logger.error("LLM API key is not configured for provider=%s", self.provider)
            raise LLMServiceError("LLM API key is not configured.")

        client_kwargs = {"api_key": self.api_key}
        if self.provider == "openrouter":
            client_kwargs["base_url"] = "https://openrouter.ai/api/v1"
        logger.debug("Creating LLM client for provider=%s", self.provider)
        return OpenAI(**client_kwargs)

    def _run_json_completion(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        client = self._create_client()

        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            logger.exception(
                "LLM request failed for provider=%s model=%s",
                self.provider,
                self.model,
            )
            raise LLMServiceError("LLM request failed.") from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            logger.error(
                "LLM returned empty content for provider=%s model=%s",
                self.provider,
                self.model,
            )
            raise LLMServiceError("LLM returned an empty response.")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.exception("LLM returned non-JSON payload")
            raise LLMServiceError("LLM returned a non-JSON response.") from exc

        if not isinstance(payload, dict):
            logger.error("LLM JSON payload is not an object")
            raise LLMServiceError("LLM JSON response must be an object.")

        return payload

    def generate_resume_profile(self, resume_text: str) -> dict[str, Any]:
        resume_text = resume_text.strip()
        if not resume_text:
            logger.error("Resume text is empty while generating profile")
            raise LLMServiceError("Resume text is empty.")

        logger.info("Generating resume profile from resume text")

        system_prompt = (
            "You are an expert resume parser. Convert resume text into concise, factual JSON. "
            "Do not invent any information. If a field is unknown, use an empty string, "
            "empty list, or 0 as appropriate. Return strict JSON only."
        )
        user_prompt = (
            "Extract a compact resume profile from this resume text.\n\n"
            "Output JSON with only these keys:\n"
            "name, summary, years_of_experience, current_role, skills, "
            "programming_languages, frameworks, tools, databases, experience, "
            "education, certifications\n\n"
            "Rules:\n"
            "- Keep entries concise and factual.\n"
            "- Do not copy full resume sections verbatim.\n"
            "- experience is a list of objects with company, role, duration, highlights (list).\n"
            "- Mention only information clearly present in the resume text.\n\n"
            f"Resume Text:\n{resume_text}"
        )

        return self._run_json_completion(system_prompt=system_prompt, user_prompt=user_prompt)

    def generate_application_email(
        self,
        recruiter_name: str,
        recruiter_email: str,
        company_name: str,
        job_title: str,
        job_description: str,
        additional_context: str,
        relevant_profile_context: dict[str, Any],
    ) -> dict[str, str]:
        logger.info("Generating recruiter email for company=%s role=%s", company_name, job_title)
        system_prompt = (
            "You are an expert career assistant. Generate recruiter outreach/application emails "
            "that are concise and professional. Return strict JSON with keys subject and body only."
        )
        profile_context_json = json.dumps(relevant_profile_context, ensure_ascii=False)
        user_prompt = (
            f"Recruiter name: {recruiter_name}\n"
            f"Recruiter email: {recruiter_email}\n"
            f"Company: {company_name}\n"
            f"Job title: {job_title}\n"
            f"Job description:\n{job_description}\n\n"
            f"Additional context from candidate:\n{additional_context.strip() or '(none)'}\n\n"
            f"Candidate full name from env: {self.candidate_name or '(not provided)'}\n"
            "Candidate LinkedIn URL from env: "
            f"{self.candidate_linkedin_url or '(not provided)'}\n\n"
            f"Relevant candidate profile (from resume):\n{profile_context_json}\n\n"
            "Constraints:\n"
            "- Personalize using recruiter name and company.\n"
            "- Analyze the job description and reference relevant requirements.\n"
            "- Use additional context when it helps "
            "(for example prior application note, job ID, or referral info).\n"
            "- Use only the provided candidate profile as resume context.\n"
            "- Do not invent experience, skills, employers, achievements, or education.\n"
            "- Keep it concise and professional.\n"
            "- Format body as readable short paragraphs with blank lines between sections.\n"
            "- Include a greeting line and a professional closing line.\n"
            "- Use candidate full name from env in the sign-off when provided.\n"
            "- Include candidate LinkedIn URL from env in the email body when provided.\n"
            "- Do not dump resume details into the email body.\n"
            "- Mention that the resume is attached where appropriate.\n"
            "- Return strict JSON with only subject and body."
        )

        payload = self._run_json_completion(system_prompt=system_prompt, user_prompt=user_prompt)

        subject = str(payload.get("subject", "")).strip()
        body = str(payload.get("body", "")).strip()
        if not subject or not body:
            logger.error("LLM response missing subject/body fields")
            raise LLMServiceError("LLM response did not include subject and body.")

        return {"subject": subject, "body": body}
