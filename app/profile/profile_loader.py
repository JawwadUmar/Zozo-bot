from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional
import yaml

from app.profile.candidate_profile import CandidateProfile, WorkAuthorization


def get_default_profile_path() -> Path:
    base = Path(__file__).resolve().parents[2]
    return base / "data" / "candidate_profile.yaml"


def get_resume_path() -> Path:
    base = Path(__file__).resolve().parents[2]
    return base / "data" / "resume.txt"


def parse_resume_text(resume_text: str) -> CandidateProfile:
    """Best-effort parser for resume text to pre-populate CandidateProfile."""
    profile = CandidateProfile()

    # Name
    name_match = re.search(r"(?:Full Name|Name):\s*([^\n\r]+)", resume_text, re.IGNORECASE)
    if not name_match:
        name_match = re.search(r"#\s*([^\n\r—–-]+)", resume_text)
    if name_match:
        profile.name = name_match.group(1).strip()

    # Phone
    phone_match = re.search(r"(?:Phone(?: Number)?):\s*([^\n\r]+)", resume_text, re.IGNORECASE)
    if phone_match:
        profile.phone = phone_match.group(1).strip()

    # Email
    email_match = re.search(r"(?:Email):\s*([^\n\r\s]+@[^\n\r\s]+)", resume_text, re.IGNORECASE)
    if email_match:
        profile.email = email_match.group(1).strip()

    # URLs
    li_match = re.search(r"(?:LinkedIn(?: Profile)?):\s*(https?://[^\n\r\s]+)", resume_text, re.IGNORECASE)
    if li_match:
        profile.linkedin_url = li_match.group(1).strip()

    gh_match = re.search(r"(?:GitHub(?: Profile)?):\s*(https?://[^\n\r\s]+)", resume_text, re.IGNORECASE)
    if gh_match:
        profile.github_url = gh_match.group(1).strip()

    # Title & Company
    title_match = re.search(r"(?:Current Job Title|Job Title):\s*([^\n\r]+)", resume_text, re.IGNORECASE)
    if title_match:
        profile.current_title = title_match.group(1).strip()

    company_match = re.search(r"(?:Current Employer|Company):\s*([^\n\r]+)", resume_text, re.IGNORECASE)
    if company_match:
        profile.current_company = company_match.group(1).strip()

    # Years of experience
    exp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?(?:\s*of)?\s*(?:work\s*)?experience", resume_text, re.IGNORECASE)
    if exp_match:
        try:
            profile.years_of_experience = int(float(exp_match.group(1)))
        except ValueError:
            profile.years_of_experience = 3

    # Location
    loc_match = re.search(r"(?:Location):\s*([^\n\r]+)", resume_text, re.IGNORECASE)
    if loc_match:
        profile.location = loc_match.group(1).strip()

    # Extract Skills
    skills_section = re.search(r"##\s*KEY SKILLS.*?(?=##|$)", resume_text, re.DOTALL | re.IGNORECASE)
    if skills_section:
        skills_text = skills_section.group(0)
        found_skills = []
        for line in skills_text.splitlines():
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                found_skills.append(line.lstrip("-* ").strip())
            elif "," in line and not line.startswith("#"):
                found_skills.extend([s.strip() for s in line.split(",") if s.strip()])
        if found_skills:
            profile.skills = found_skills

    return profile


def load_candidate_profile(yaml_path: Optional[str] = None) -> CandidateProfile:
    """Load candidate profile from YAML file, with fallback to resume.txt + environment variables."""
    path = Path(yaml_path) if yaml_path else get_default_profile_path()

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            profile = CandidateProfile(**data)
            return profile
        except Exception as e:
            print(f"⚠️ Zozo: Error loading {path}: {e}. Falling back to resume parser.")

    # Fallback to resume.txt
    resume_file = get_resume_path()
    if resume_file.exists():
        try:
            with open(resume_file, "r", encoding="utf-8") as f:
                text = f.read()
            profile = parse_resume_text(text)
            profile.resume_path = str(resume_file)
        except Exception:
            profile = CandidateProfile()
    else:
        profile = CandidateProfile()

    # Apply environment variable overrides if profile is missing details
    email = os.getenv("LINKEDIN_EMAIL")
    if email and not profile.email:
        profile.email = email

    phone = os.getenv("PHONE_NUMBER")
    if phone and not profile.phone:
        profile.phone = phone

    if not profile.location:
        profile.location = "Kolkata, West Bengal, India"

    return profile


def generate_default_profile_yaml(output_path: Optional[str] = None) -> str:
    """Generate a default candidate_profile.yaml template pre-filled with parsed resume data."""
    dest = Path(output_path) if output_path else get_default_profile_path()
    dest.parent.mkdir(parents=True, exist_ok=True)

    profile = load_candidate_profile()
    data = profile.model_dump()

    with open(dest, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return str(dest)
