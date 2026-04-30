import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")
JOBLINK = os.getenv("LINKEDIN_JOB_LINK")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

if not EMAIL or not PASSWORD or not JOBLINK:
    raise ValueError("Credentials missing in .env")