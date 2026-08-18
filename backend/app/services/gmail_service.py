import base64
import json
import logging
import mimetypes
import os
from email import policy
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
logger = logging.getLogger(__name__)


class GmailOAuthError(Exception):
    """Raised when OAuth authentication fails for Gmail."""


class GmailSendError(Exception):
    """Raised when Gmail API send fails."""


class GmailService:
    def __init__(
        self,
        credentials_path: str,
        token_path: str,
        oauth_host: str,
        oauth_port: int,
    ) -> None:
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.oauth_host = oauth_host
        self.oauth_port = oauth_port

    def _has_required_scopes(self, creds: Credentials | None) -> bool:
        if not creds:
            return False
        if creds.has_scopes(SCOPES):
            return True

        granted_scopes = set(getattr(creds, "granted_scopes", []) or [])
        requested_scopes = set(getattr(creds, "scopes", []) or [])
        effective_scopes = granted_scopes or requested_scopes
        return set(SCOPES).issubset(effective_scopes)

    def _token_file_has_required_scopes(self) -> bool:
        if not os.path.exists(self.token_path):
            return False

        try:
            with open(self.token_path, "r", encoding="utf-8") as token_file:
                payload = json.load(token_file)
        except (OSError, json.JSONDecodeError):
            return False

        raw_scopes = payload.get("scopes", [])
        if isinstance(raw_scopes, str):
            file_scopes = set(raw_scopes.split())
        else:
            file_scopes = set(raw_scopes)

        return set(SCOPES).issubset(file_scopes)

    def _get_credentials(self) -> Credentials:
        if not os.path.exists(self.credentials_path):
            raise GmailOAuthError("Gmail credentials file not found.")

        creds = None
        if os.path.exists(self.token_path) and not self._token_file_has_required_scopes():
            os.remove(self.token_path)

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if creds and not self._has_required_scopes(creds):
            os.remove(self.token_path)
            creds = None

        if creds and creds.valid:
            return creds

        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                if not self._has_required_scopes(creds):
                    raise GmailOAuthError("Refreshed token is missing required Gmail send scope.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                try:
                    creds = flow.run_local_server(
                        host=self.oauth_host,
                        port=self.oauth_port,
                        open_browser=True,
                        redirect_uri_trailing_slash=True,
                        prompt="consent",
                    )
                except OSError as exc:
                    # Port conflicts are common when API server also runs on 8000.
                    if getattr(exc, "winerror", None) == 10048:
                        logger.warning(
                            "Configured Gmail OAuth port %s is in use. "
                            "Retrying with a random free port.",
                            self.oauth_port,
                        )
                        creds = flow.run_local_server(
                            host=self.oauth_host,
                            port=0,
                            open_browser=True,
                            redirect_uri_trailing_slash=True,
                            prompt="consent",
                        )
                    else:
                        raise

            with open(self.token_path, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
        except Exception as exc:
            raise GmailOAuthError("Failed to authenticate with Gmail OAuth.") from exc

        if not creds:
            raise GmailOAuthError("Gmail OAuth did not return credentials.")

        return creds

    def _build_encoded_message(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        attachment_path: str,
    ) -> str:
        # Use a safe SMTP line length to avoid base64 encoding errors on attachments.
        # 998 is the RFC-compliant maximum and preserves formatting for typical email bodies.
        message = EmailMessage(policy=policy.SMTP.clone(max_line_length=998))
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body_text, subtype="plain", charset="utf-8", cte="8bit")

        file_path = Path(attachment_path)
        content_type, _ = mimetypes.guess_type(str(file_path))
        if content_type is None:
            content_type = "application/octet-stream"
        main_type, sub_type = content_type.split("/", 1)

        with open(file_path, "rb") as file:
            attachment_data = file.read()

        message.add_attachment(
            attachment_data,
            maintype=main_type,
            subtype=sub_type,
            filename=file_path.name,
        )

        return base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        attachment_path: str,
    ) -> tuple[str, str]:
        creds = self._get_credentials()

        try:
            service = build("gmail", "v1", credentials=creds, cache_discovery=False)
            encoded_message = self._build_encoded_message(
                to_email=to_email,
                subject=subject,
                body_text=body_text,
                attachment_path=attachment_path,
            )
            payload = {"raw": encoded_message}
            sent_message = service.users().messages().send(userId="me", body=payload).execute()
        except HttpError as exc:
            raise GmailSendError("Gmail API failed to send email.") from exc
        except GmailOAuthError:
            raise
        except Exception as exc:
            raise GmailSendError("Unexpected error while sending email via Gmail API.") from exc

        message_id = sent_message.get("id")
        thread_id = sent_message.get("threadId")
        if not message_id or not thread_id:
            raise GmailSendError("Gmail API response missing message identifiers.")

        return message_id, thread_id
