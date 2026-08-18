import json
import logging
import re
from pathlib import Path
from typing import Any

from docx import Document
from pypdf import PdfReader

from app.services.llm_service import LLMService, LLMServiceError

logger = logging.getLogger(__name__)


class ResumeServiceError(Exception):
    """Base error for resume profile workflows."""


class ResumeNotFoundError(ResumeServiceError):
    """Raised when no resume exists in assets."""


class MultipleResumeFilesError(ResumeServiceError):
    """Raised when multiple resume files exist in assets."""


class ResumeExtractionError(ResumeServiceError):
    """Raised when resume text cannot be extracted."""


class ResumeProfileGenerationError(ResumeServiceError):
    """Raised when LLM fails to generate resume profile."""


class ResumeProfileValidationError(ResumeServiceError):
    """Raised when profile JSON is invalid or empty."""


class ResumeService:
    PROFILE_FILENAME = "resume_profile.json"
    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    def __init__(self, assets_dir: Path | None = None) -> None:
        self.assets_dir = assets_dir or self._resolve_assets_dir()
        self.profile_path = self.assets_dir / self.PROFILE_FILENAME
        logger.info("ResumeService initialized with assets_dir=%s", self.assets_dir)

    def _resolve_assets_dir(self) -> Path:
        current_file = Path(__file__).resolve()
        backend_root = current_file.parents[2]
        workspace_root = current_file.parents[3]

        candidate_dirs = [
            backend_root / "assets",
            workspace_root / "assets",
        ]

        for candidate in candidate_dirs:
            if candidate.exists() and candidate.is_dir():
                logger.debug("Resolved assets directory: %s", candidate)
                return candidate

        # Keep backend/assets as the default target if neither exists yet.
        logger.debug("Using default assets directory: %s", backend_root / "assets")
        return backend_root / "assets"

    def find_resume(self) -> Path:
        if not self.assets_dir.exists() or not self.assets_dir.is_dir():
            logger.error("Assets directory not found: %s", self.assets_dir)
            raise ResumeNotFoundError(f"Assets directory not found: {self.assets_dir}")

        candidates = [
            path
            for path in self.assets_dir.iterdir()
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]

        if not candidates:
            logger.error("No resume file found in assets directory: %s", self.assets_dir)
            raise ResumeNotFoundError(
                f"No resume file found in {self.assets_dir}. Expected one .pdf or .docx file."
            )

        if len(candidates) > 1:
            names = ", ".join(sorted(path.name for path in candidates))
            logger.error("Multiple resume files found: %s", names)
            raise MultipleResumeFilesError(
                f"Multiple resume files found in {self.assets_dir}: {names}. Keep only one file."
            )

        logger.info("Using resume file: %s", candidates[0].name)
        return candidates[0]

    def extract_resume_text(self, resume_path: Path) -> str:
        logger.info("Extracting resume text from %s", resume_path.name)
        suffix = resume_path.suffix.lower()
        if suffix == ".pdf":
            text = self._extract_pdf_text(resume_path)
        elif suffix == ".docx":
            text = self._extract_docx_text(resume_path)
        else:
            raise ResumeExtractionError(
                f"Unsupported resume format: {suffix}. Supported formats: .pdf, .docx"
            )

        cleaned = text.strip()
        if not cleaned:
            logger.error("Extracted resume text is empty for %s", resume_path.name)
            raise ResumeExtractionError("Extracted resume text is empty.")

        return cleaned

    def _extract_pdf_text(self, resume_path: Path) -> str:
        try:
            reader = PdfReader(str(resume_path))
            parts = [(page.extract_text() or "") for page in reader.pages]
        except Exception as exc:
            logger.exception("Failed to extract text from PDF: %s", resume_path)
            raise ResumeExtractionError(
                f"Failed to extract text from PDF resume: {resume_path}"
            ) from exc

        return "\n".join(parts)

    def _extract_docx_text(self, resume_path: Path) -> str:
        try:
            document = Document(str(resume_path))
            parts = [paragraph.text for paragraph in document.paragraphs]
        except Exception as exc:
            logger.exception("Failed to extract text from DOCX: %s", resume_path)
            raise ResumeExtractionError(
                f"Failed to extract text from DOCX resume: {resume_path}"
            ) from exc

        return "\n".join(parts)

    def generate_resume_profile(self, resume_text: str, llm_service: LLMService) -> dict[str, Any]:
        logger.info("Generating resume profile using LLM service")
        try:
            profile = llm_service.generate_resume_profile(resume_text=resume_text)
        except LLMServiceError as exc:
            logger.exception("LLM failed while generating resume profile")
            raise ResumeProfileGenerationError(
                "Failed to generate resume profile from LLM."
            ) from exc

        self._validate_profile(profile)
        return profile

    def load_resume_profile(self) -> dict[str, Any]:
        if not self.profile_path.exists() or not self.profile_path.is_file():
            logger.error("Resume profile not found: %s", self.profile_path)
            raise ResumeProfileValidationError(
                f"Resume profile not found: {self.profile_path}"
            )

        try:
            profile = json.loads(self.profile_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.exception("Invalid JSON in resume profile file: %s", self.profile_path)
            raise ResumeProfileValidationError(
                "resume_profile.json contains invalid JSON."
            ) from exc
        except OSError as exc:
            logger.exception("Failed reading resume profile file: %s", self.profile_path)
            raise ResumeProfileValidationError("Failed to read resume_profile.json.") from exc

        self._validate_profile(profile)
        return profile

    def save_resume_profile(self, profile: dict[str, Any]) -> None:
        self._validate_profile(profile)
        try:
            self.assets_dir.mkdir(parents=True, exist_ok=True)
            self.profile_path.write_text(
                json.dumps(profile, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info("Saved resume profile to %s", self.profile_path)
        except OSError as exc:
            logger.exception("Failed writing resume profile file: %s", self.profile_path)
            raise ResumeProfileValidationError("Failed to write resume_profile.json.") from exc

    def get_or_create_resume_profile(self, llm_service: LLMService) -> dict[str, Any]:
        if self.profile_path.exists():
            logger.info("Using cached resume profile: %s", self.profile_path)
            return self.load_resume_profile()

        logger.info("Cached resume profile not found. Generating a new one.")
        resume_path = self.find_resume()
        resume_text = self.extract_resume_text(resume_path)
        profile = self.generate_resume_profile(resume_text, llm_service)
        self.save_resume_profile(profile)
        return profile

    def select_relevant_resume_context(
        self,
        profile: dict[str, Any],
        job_description: str,
    ) -> dict[str, Any]:
        logger.debug("Selecting relevant resume context for job description")
        self._validate_profile(profile)
        keywords = self._extract_keywords(job_description)

        def pick_matches(items: list[str], fallback_limit: int = 3) -> list[str]:
            normalized_items = [
                item.strip()
                for item in items
                if isinstance(item, str) and item.strip()
            ]
            if not normalized_items:
                return []

            matched = [
                item
                for item in normalized_items
                if self._contains_keyword(item.lower(), keywords)
            ]
            if matched:
                return matched[:8]
            return normalized_items[:fallback_limit]

        relevant_skills: list[str] = []
        for field_name in ["skills", "programming_languages", "frameworks", "tools", "databases"]:
            values = profile.get(field_name)
            if isinstance(values, list):
                relevant_skills.extend(pick_matches(values, fallback_limit=0))

        if not relevant_skills:
            for field_name in [
                "skills",
                "programming_languages",
                "frameworks",
                "tools",
                "databases",
            ]:
                values = profile.get(field_name)
                if isinstance(values, list):
                    relevant_skills.extend(pick_matches(values, fallback_limit=2))
                if len(relevant_skills) >= 6:
                    break
        relevant_skills = relevant_skills[:10]

        relevant_experience: list[dict[str, Any]] = []
        experience_items = profile.get("experience")
        if isinstance(experience_items, list):
            for exp in experience_items:
                if not isinstance(exp, dict):
                    continue
                company = str(exp.get("company", "")).strip()
                role = str(exp.get("role", "")).strip()
                duration = str(exp.get("duration", "")).strip()
                highlights_raw = exp.get("highlights")
                highlights = [
                    item.strip()
                    for item in (highlights_raw if isinstance(highlights_raw, list) else [])
                    if isinstance(item, str) and item.strip()
                ]

                searchable = " ".join([company, role, duration, *highlights]).lower()
                if self._contains_keyword(searchable, keywords):
                    relevant_experience.append(
                        {
                            "company": company,
                            "role": role,
                            "duration": duration,
                            "highlights": highlights[:4],
                        }
                    )

            if not relevant_experience:
                for exp in experience_items[:2]:
                    if not isinstance(exp, dict):
                        continue
                    highlights = exp.get("highlights")
                    relevant_experience.append(
                        {
                            "company": str(exp.get("company", "")).strip(),
                            "role": str(exp.get("role", "")).strip(),
                            "duration": str(exp.get("duration", "")).strip(),
                            "highlights": [
                                item.strip()
                                for item in (highlights if isinstance(highlights, list) else [])
                                if isinstance(item, str) and item.strip()
                            ][:3],
                        }
                    )

        context = {
            "name": str(profile.get("name", "")).strip(),
            "summary": str(profile.get("summary", "")).strip(),
            "current_role": str(profile.get("current_role", "")).strip(),
            "years_of_experience": profile.get("years_of_experience", 0),
            "relevant_skills": relevant_skills,
            "relevant_experience": relevant_experience[:3],
        }

        # Keep context compact to reduce token usage in high-volume generation.
        filtered = {key: value for key, value in context.items() if value not in ("", [], None)}
        logger.debug("Selected resume context keys: %s", ", ".join(sorted(filtered.keys())))
        return filtered

    def _extract_keywords(self, text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", text.lower())
        stop_words = {
            "and",
            "the",
            "with",
            "for",
            "you",
            "your",
            "are",
            "our",
            "from",
            "this",
            "that",
            "will",
            "have",
            "has",
            "into",
            "about",
            "role",
            "team",
            "work",
            "using",
            "years",
            "experience",
            "developer",
            "engineer",
            "required",
            "plus",
        }
        return {word for word in words if len(word) > 2 and word not in stop_words}

    def _contains_keyword(self, text: str, keywords: set[str]) -> bool:
        return bool(keywords) and any(keyword in text for keyword in keywords)

    def _validate_profile(self, profile: Any) -> None:
        if not isinstance(profile, dict):
            logger.error("Resume profile validation failed: payload is not a JSON object")
            raise ResumeProfileValidationError("Resume profile must be a JSON object.")

        if not profile:
            logger.error("Resume profile validation failed: profile is empty")
            raise ResumeProfileValidationError("Resume profile is empty.")

        has_meaningful_value = False
        for value in profile.values():
            if isinstance(value, str) and value.strip():
                has_meaningful_value = True
                break
            if isinstance(value, (int, float)) and value > 0:
                has_meaningful_value = True
                break
            if isinstance(value, list) and value:
                has_meaningful_value = True
                break
            if isinstance(value, dict) and value:
                has_meaningful_value = True
                break

        if not has_meaningful_value:
            logger.error("Resume profile validation failed: no meaningful data found")
            raise ResumeProfileValidationError("Resume profile does not contain meaningful data.")