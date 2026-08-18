import base64
import json
import os
import os.path
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
OAUTH_HOST = os.environ.get("GMAIL_OAUTH_HOST", "localhost")
OAUTH_PORT = int(os.environ.get("GMAIL_OAUTH_PORT", "8000"))
TOKEN_PATH = "token.json"


def has_required_scopes(creds):
    """Return True when credentials include all scopes required by this script."""
    if not creds:
        return False

    if creds.has_scopes(SCOPES):
        return True

    granted_scopes = set(getattr(creds, "granted_scopes", []) or [])
    requested_scopes = set(getattr(creds, "scopes", []) or [])
    effective_scopes = granted_scopes or requested_scopes
    return set(SCOPES).issubset(effective_scopes)


def token_file_has_required_scopes(token_path):
    """Check scopes persisted in token.json without trusting runtime overrides."""
    if not os.path.exists(token_path):
        return False

    try:
        with open(token_path, "r", encoding="utf-8") as token_file:
            payload = json.load(token_file)
    except (OSError, json.JSONDecodeError):
        return False

    raw_scopes = payload.get("scopes", [])
    if isinstance(raw_scopes, str):
        file_scopes = set(raw_scopes.split())
    else:
        file_scopes = set(raw_scopes)
    return set(SCOPES).issubset(file_scopes)


def get_credentials():
    """Load saved credentials or run OAuth with a deterministic redirect URI."""
    token_path = TOKEN_PATH
    creds = None

    if os.path.exists(token_path) and not token_file_has_required_scopes(token_path):
        print("Saved token file is missing required scopes. Re-authentication is required.")
        os.remove(token_path)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and not has_required_scopes(creds):
        print("Saved token is missing required scope. Re-authentication is required.")
        os.remove(token_path)
        creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        if not has_required_scopes(creds):
            creds = None
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        # Use a fixed host/port so redirect URI stays stable and can be whitelisted.
        print(f"Using OAuth redirect URI: http://{OAUTH_HOST}:{OAUTH_PORT}/")
        creds = flow.run_local_server(
            host=OAUTH_HOST,
            port=OAUTH_PORT,
            open_browser=True,
            redirect_uri_trailing_slash=True,
            prompt="consent",
        )

    with open(token_path, "w") as token:
        token.write(creds.to_json())

    return creds


def create_message(sender, to, subject, body_text):
    """Build a base64url encoded RFC 2822 email message."""
    message = EmailMessage()
    message["To"] = to
    message["From"] = sender
    message["Subject"] = subject
    message.set_content(body_text)
    return base64.urlsafe_b64encode(message.as_bytes()).decode()


def create_draft(service, user_id, encoded_message):
    """Create a Gmail draft using the encoded raw message payload."""
    body = {"message": {"raw": encoded_message}}
    return service.users().drafts().create(userId=user_id, body=body).execute()


def send_message(service, user_id, encoded_message):
    """Send an email message through the Gmail API."""
    body = {"raw": encoded_message}
    return service.users().messages().send(userId=user_id, body=body).execute()


def main():
    """Create a draft or send a Gmail message using the Gmail API."""
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        creds = get_credentials()

        try:
            service = build("gmail", "v1", credentials=creds)
            profile = service.users().getProfile(userId="me").execute()
            sender_email = profile["emailAddress"]
            to_email = os.environ.get("GMAIL_TO", sender_email)
            subject = os.environ.get("GMAIL_SUBJECT", "Test mail from Gmail API")
            body_text = os.environ.get(
                "GMAIL_BODY",
                "Hello, this email was sent using the Gmail API quickstart script.",
            )
            action = os.environ.get("GMAIL_ACTION", "send").lower()

            encoded_message = create_message(sender_email, to_email, subject, body_text)

            if action == "draft":
                draft = create_draft(service, "me", encoded_message)
                print(f"Draft created successfully. Draft ID: {draft['id']}")
            else:
                sent = send_message(service, "me", encoded_message)
                print(sent)
                print(f"Email sent successfully. Message ID: {sent['id']}")

            print(f"Action: {action}")
            print(f"From: {sender_email}")
            print(f"To: {to_email}")
            return

        except HttpError as error:
            if (
                error.resp.status == 403
                and "insufficientPermissions" in str(error)
                and attempt < max_attempts
            ):
                if os.path.exists(TOKEN_PATH):
                    os.remove(TOKEN_PATH)
                print("Token lacked required Gmail scope. Removed token.json and retrying auth...")
                continue

            print(f"An error occurred: {error}")
            return


if __name__ == "__main__":
    main()
