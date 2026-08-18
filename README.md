# Recruiter Reach

AI-powered recruiter outreach app.

This project helps you:

- Generate a tailored outreach/application email from a job description and your resume context.
- Review and edit the generated email in the UI.
- Send the final email using Gmail API with your resume attached.
- Store sent-email history in Supabase Postgres and view it from the app.

## Tech Stack

- Frontend: Next.js 16, React 19, TypeScript
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: Supabase Postgres
- Email: Gmail API (OAuth desktop flow)
- LLM: OpenAI or OpenRouter (configurable)
- Tooling: npm, uv (Python package manager)

## Project Structure

- Root scripts orchestrate frontend + backend setup and dev run.
- frontend/ contains the Next.js app and proxy API routes.
- backend/ contains FastAPI app, DB models, Gmail and LLM services.
- backend/assets/ contains resume input and generated resume profile cache.

## Prerequisites

Install these first:

- Node.js 20+
- npm 10+
- Python 3.13+
- uv

Install uv:

- Windows (PowerShell):

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

- macOS/Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 1) Install Dependencies

From repo root:

```bash
npm run install:all
```

This does:

- frontend dependency install via npm
- backend dependency sync via uv

## 2) Configure Environment Variables

Create backend/.env and set values like this:

```env
# Required for DB persistence
DATABASE_URL=postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres

# Required to send emails (path to your resume file)
RESUME_PATH=assets/your_resume.pdf

# Candidate identity used in generated email content
CANDIDATE_NAME=Your Full Name
CANDIDATE_LINKEDIN_URL=https://www.linkedin.com/in/your-handle

# Gmail OAuth files
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# Gmail OAuth local callback host/port
# Important: backend runs on port 8000 by default, so use another port to avoid conflicts.
GMAIL_OAUTH_HOST=localhost
GMAIL_OAUTH_PORT=8080

# LLM provider selection: openai or openrouter
LLM_PROVIDER=openai

# OpenAI
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini

# OpenRouter (used when LLM_PROVIDER=openrouter, or as fallback when LLM_API_KEY is empty)
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
```

Create frontend/.env.local only if backend is not at default URL:

```env
BACKEND_BASE_URL=http://127.0.0.1:8000
```

If omitted, frontend already defaults to http://127.0.0.1:8000.

## 3) Supabase Database Setup

1. Create a Supabase project.
2. Go to Project Settings -> Database.
3. Copy your Postgres connection string and map it to DATABASE_URL.
4. Use the psycopg SQLAlchemy format:

```text
postgresql+psycopg://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres
```

Notes:

- The backend enforces SSL for non-SQLite connections.
- On startup, the backend auto-creates the sent_emails table via SQLAlchemy metadata.
- You can verify DB connectivity from:

```text
GET /db-status
```

## 4) Gmail API Setup (Required for Sending)

This app uses OAuth desktop flow and stores token at GMAIL_TOKEN_PATH.

1. In Google Cloud Console:
   - Create or select a project.
   - Enable Gmail API.
   - Configure OAuth consent screen.
   - Create OAuth Client ID of type Desktop app.
2. Download OAuth client JSON.
3. Place it at backend/credentials.json (or update GMAIL_CREDENTIALS_PATH).
4. Ensure backend/token.json is writable.

During first send:

- Browser opens for Google sign-in/consent.
- OAuth token is saved to backend/token.json.
- Next sends reuse/refresh token automatically.

Important behavior:

- App requires Gmail send scope.
- If existing token lacks required scope, app deletes token and re-authenticates.
- If configured OAuth port is busy, app retries with a random free port.

Optional standalone Gmail test script:

```bash
cd backend
uv run python quickstart.py
```

Useful env options for quickstart.py:

- GMAIL_ACTION=send or draft
- GMAIL_TO, GMAIL_SUBJECT, GMAIL_BODY

## 5) Resume File Requirements

Two resume behaviors exist:

- Email generation flow:
  - Looks in assets directories for exactly one resume file (.pdf or .docx).
  - Supported locations include backend/assets and workspace-level assets.
  - Generates and caches profile at backend/assets/resume_profile.json.

- Email send flow:
  - Uses RESUME_PATH directly.
  - Must point to an existing file.

Recommended:

- Keep your resume in backend/assets/.
- Set RESUME_PATH to that exact file path.
- Keep only one .pdf/.docx resume in the scanned assets folder for generation.

## 6) Run the App

Run both frontend and backend together from repo root:

```bash
npm run dev
```

Services:

- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000

Run individually if needed:

```bash
npm run dev:frontend
npm run dev:backend
```

## Application Flow

1. Open frontend at http://localhost:3000.
2. Fill recruiter/job fields and generate email.
3. Edit subject/body if needed.
4. Send email (first time triggers Gmail OAuth).
5. View sent history at /requests.

## Backend API Endpoints

- GET /health
  - Health check.
- GET /db-status
  - DB connectivity status.
- POST /applications/generate
  - Generates subject/body from job details + resume context.
- POST /applications/send
  - Sends Gmail email with resume attachment and stores history.
- GET /applications
  - Lists sent email history.
- GET /openrouter/key
  - Verifies OPENROUTER_API_KEY against OpenRouter key endpoint.

## Common Problems and Fixes

1. Database is unreachable

- Check DATABASE_URL value and password.
- Confirm Supabase project is active and network access is allowed.
- Verify URL uses postgresql+psycopg prefix.

2. RESUME_PATH is not configured or file not found

- Set RESUME_PATH in backend/.env.
- Confirm file exists at that exact path.

3. Gmail OAuth fails

- Confirm Gmail API is enabled.
- Confirm backend/credentials.json is valid Desktop app OAuth JSON.
- Delete backend/token.json and retry to force fresh consent.
- Change GMAIL_OAUTH_PORT if port conflict occurs.

4. LLM generation fails

- Set either LLM_API_KEY (OpenAI) or OPENROUTER_API_KEY (OpenRouter).
- Ensure LLM_PROVIDER matches intended provider.

5. Frontend cannot reach backend

- Ensure backend is running on expected host/port.
- Set frontend/.env.local BACKEND_BASE_URL when using non-default backend URL.

## Security Notes

- Never commit secrets.
- Keep these private:
  - backend/credentials.json
  - backend/token.json
  - backend/.env
  - frontend/.env.local

Root .gitignore already excludes env files and Gmail credential/token files.

## Useful Commands

From repo root:

```bash
npm run install:all
npm run dev
npm run dev:frontend
npm run dev:backend
```

From backend:

```bash
uv sync
uv run uvicorn main:app --reload
uv run python quickstart.py
```

## License

This project is licensed under the MIT License.

See LICENSE for full text.
