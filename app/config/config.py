import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("Credentials missing in .env")