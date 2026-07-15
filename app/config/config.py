import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
JOBLINK = os.getenv("LINKEDIN_JOB_LINK")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")


def _env_bool(name, default="false"):
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


AUTO_CONNECT_HIRING_TEAM = _env_bool("AUTO_CONNECT_HIRING_TEAM")
CONNECTION_NOTE_TEMPLATE = os.getenv(
    "CONNECTION_NOTE_TEMPLATE",
    "Hi {name}, I applied for the {job_title} role at {company}. I would be glad to connect and follow updates from your hiring team."
)

if not EMAIL or not PASSWORD or not JOBLINK:
    raise ValueError("Credentials missing in .env")
