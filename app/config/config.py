import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("LINKEDIN_EMAIL", "")
PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
JOBLINK = os.getenv("LINKEDIN_JOB_LINK", "")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "")


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


AUTO_CONNECT_HIRING_TEAM = _env_bool("AUTO_CONNECT_HIRING_TEAM")
CONNECTION_NOTE_TEMPLATE = os.getenv(
    "CONNECTION_NOTE_TEMPLATE",
    "Hi {name}, I applied for the {job_title} role at {company}. I would be glad to connect and follow updates from your hiring team."
)

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
DECISION_LLM_MODEL = os.getenv("DECISION_LLM_MODEL")
OBSERVATION_LLM_MODEL = os.getenv("OBSERVATION_LLM_MODEL")

# Agent Safety & Behavior
MAX_ACTIONS_PER_APPLICATION = int(os.getenv("MAX_ACTIONS_PER_APPLICATION", "50"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
HUMAN_APPROVAL_BEFORE_SUBMIT = _env_bool("HUMAN_APPROVAL_BEFORE_SUBMIT", "false")
SCREENSHOT_ON_ERROR = _env_bool("SCREENSHOT_ON_ERROR", "true")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIRECTORY = os.path.join(PROJECT_ROOT, "data")
USER_DATA_DIRECTORY = os.path.join(DATA_DIRECTORY, "session")


def validate_credentials():
    """Validate that required credentials exist before launching live browser session."""
    if not EMAIL or not PASSWORD or not JOBLINK:
        raise ValueError(
            "Missing credentials in .env! Please set LINKEDIN_EMAIL, LINKEDIN_PASSWORD, and LINKEDIN_JOB_LINK."
        )
