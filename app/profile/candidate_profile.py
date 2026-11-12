from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkAuthorization(BaseModel):
    authorized_to_work: bool = Field(default=True, description="Legally authorized to work in target country")
    requires_sponsorship: bool = Field(default=False, description="Requires visa sponsorship now or in the future")
    willing_to_relocate: bool = Field(default=True, description="Willing to relocate if required")
    comfortable_with_remote: bool = Field(default=True, description="Comfortable working remotely")
    can_start_immediately: bool = Field(default=True, description="Able to start immediately")
    notice_period_days: int = Field(default=30, description="Notice period in days")


class CandidateProfile(BaseModel):
    name: str = Field(default="", description="Candidate's full name")
    email: str = Field(default="", description="Candidate's primary email address")
    phone: str = Field(default="", description="Candidate's phone number")
    location: str = Field(default="", description="City, State, Country")
    years_of_experience: int = Field(default=3, description="Total years of professional experience")
    current_title: str = Field(default="", description="Current job title")
    current_company: str = Field(default="", description="Current employer")
    skills: List[str] = Field(default_factory=list, description="List of technical and soft skills")
    education: List[Dict[str, Any]] = Field(default_factory=list, description="Educational degrees and institutions")
    work_experience: List[Dict[str, Any]] = Field(default_factory=list, description="Previous job positions")
    resume_path: Optional[str] = Field(default=None, description="Path to candidate resume file")
    work_authorization: WorkAuthorization = Field(default_factory=WorkAuthorization)
    default_answers: Dict[str, Any] = Field(
        default_factory=lambda: {
            "current_salary": "11,00,000 INR",
            "expected_salary": "16,00,000 INR",
            "notice_period": "30 days",
            "self_rating": 9,
            "can_start_immediately": "Yes",
            "remote": "Yes",
            "authorized": "Yes",
            "sponsorship": "No",
        },
        description="Pre-configured answers for common application questions",
    )
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, description="Portfolio or website URL")

    def to_context_dict(self) -> Dict[str, Any]:
        """Produce a formatted dictionary suitable for prompt interpolation."""
        return {
            "candidate_name": self.name,
            "candidate_email": self.email,
            "candidate_phone": self.phone,
            "candidate_location": self.location,
            "candidate_yoe": self.years_of_experience,
            "candidate_role": self.current_title,
            "candidate_company": self.current_company,
            "candidate_skills": ", ".join(self.skills[:25]) if self.skills else "Software Engineering",
            "candidate_work_auth": (
                f"Authorized: {self.work_authorization.authorized_to_work}, "
                f"Needs Sponsorship: {self.work_authorization.requires_sponsorship}, "
                f"Remote: {self.work_authorization.comfortable_with_remote}, "
                f"Notice: {self.work_authorization.notice_period_days} days"
            ),
            "candidate_default_answers": str(self.default_answers),
        }
