from __future__ import annotations

import os
os.environ["TESTING"] = "1"
os.environ["LINKEDIN_EMAIL"] = "test@example.com"
os.environ["LINKEDIN_PASSWORD"] = "password123"
os.environ["LINKEDIN_JOB_LINK"] = "https://www.linkedin.com/jobs/search/?keywords=python"
os.environ["PHONE_NUMBER"] = "9155027072"
os.environ["GROQ_API_KEY"] = "mock_key"

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from app.agent.models import ElementInfo, PageObservation, PageUnderstanding, AgentAction, ActionType, PageType
from app.profile.candidate_profile import CandidateProfile, WorkAuthorization


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def easy_apply_form_html(fixtures_dir) -> str:
    return (fixtures_dir / "easy_apply_form.html").read_text(encoding="utf-8")


@pytest.fixture
def review_page_html(fixtures_dir) -> str:
    return (fixtures_dir / "review_page.html").read_text(encoding="utf-8")


@pytest.fixture
def daily_limit_html(fixtures_dir) -> str:
    return (fixtures_dir / "daily_limit.html").read_text(encoding="utf-8")


@pytest.fixture
def success_modal_html(fixtures_dir) -> str:
    return (fixtures_dir / "success_modal.html").read_text(encoding="utf-8")


@pytest.fixture
def sample_candidate_profile() -> CandidateProfile:
    return CandidateProfile(
        name="Jawwad Umar",
        email="jawwadumar99@gmail.com",
        phone="9155027072",
        location="Kolkata, India",
        years_of_experience=3,
        current_title="Software Development Engineer - 2",
        current_company="Tata Consultancy Services",
        skills=["Java", "Go", "Python", "LangGraph", "FastAPI"],
        work_authorization=WorkAuthorization(
            authorized_to_work=True,
            requires_sponsorship=False,
            willing_to_relocate=True,
            comfortable_with_remote=True,
            can_start_immediately=True,
            notice_period_days=30,
        ),
        default_answers={
            "current_salary": "11,00,000 INR",
            "expected_salary": "16,00,000 INR",
            "notice_period": "30 days",
            "self_rating": 9,
            "remote": "Yes",
        },
    )


@pytest.fixture
def sample_elements() -> list[ElementInfo]:
    return [
        ElementInfo(
            tag="button",
            role="button",
            name="Easy Apply",
            text="Easy Apply",
            is_visible=True,
            is_enabled=True,
        ),
        ElementInfo(
            tag="input",
            role="textbox",
            name="Mobile phone number",
            input_type="text",
            label="Mobile phone number",
            value="9155027072",
            is_visible=True,
            is_enabled=True,
            is_required=True,
        ),
        ElementInfo(
            tag="input",
            role="textbox",
            name="Total years of exp",
            input_type="text",
            label="Total years of exp",
            value="",
            is_visible=True,
            is_enabled=True,
            is_required=True,
        ),
        ElementInfo(
            tag="select",
            role="combobox",
            name="Are you in Kolkata?",
            label="Are you in Kolkata?",
            options=["Select an option", "Yes", "No"],
            is_visible=True,
            is_enabled=True,
        ),
        ElementInfo(
            tag="button",
            role="button",
            name="Review",
            text="Review",
            is_visible=True,
            is_enabled=True,
        ),
    ]


@pytest.fixture
def sample_page_observation(sample_elements) -> PageObservation:
    return PageObservation(
        url="https://www.linkedin.com/jobs/view/123456789",
        title="Software Engineer at TechCorp | LinkedIn",
        page_type="modal",
        interactive_elements=sample_elements,
        visible_text="Apply to TechCorp\nStep 1 of 3\nMobile phone number\nTotal years of exp",
        form_fields=[e for e in sample_elements if e.tag in ("input", "select")],
        buttons=[e for e in sample_elements if e.tag == "button"],
        dialogs=[{"title": "Apply to TechCorp", "role": "dialog"}],
        progress_indicator="Step 1 of 3",
        error_messages=[],
        has_modal=True,
    )


def create_mock_locator(text="", is_visible=True, is_enabled=True, count=1):
    loc = MagicMock()
    loc.count = AsyncMock(return_value=count)
    loc.is_visible = AsyncMock(return_value=is_visible)
    loc.is_enabled = AsyncMock(return_value=is_enabled)
    loc.inner_text = AsyncMock(return_value=text)
    loc.get_attribute = AsyncMock(return_value=None)
    loc.click = AsyncMock(return_value=None)
    loc.fill = AsyncMock(return_value=None)
    loc.scroll_into_view_if_needed = AsyncMock(return_value=None)
    loc.nth = MagicMock(return_value=loc)
    loc.first = loc
    loc.last = loc
    loc.evaluate = AsyncMock(return_value="button")
    return loc


@pytest.fixture
def mock_page():
    page = MagicMock()
    page.url = "https://www.linkedin.com/jobs/view/123456789"
    page.title = AsyncMock(return_value="Software Engineer | LinkedIn")
    page.evaluate = AsyncMock(return_value={})
    page.goto = AsyncMock()
    page.screenshot = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.mouse = MagicMock()
    page.mouse.wheel = AsyncMock()
    page.mouse.move = AsyncMock()

    body_loc = create_mock_locator("Jobs Search - Easy Apply Available")
    page.locator = MagicMock(return_value=body_loc)
    page.get_by_role = MagicMock(return_value=create_mock_locator("button"))
    page.get_by_label = MagicMock(return_value=create_mock_locator("input"))
    page.get_by_placeholder = MagicMock(return_value=create_mock_locator("input"))
    page.get_by_text = MagicMock(return_value=create_mock_locator("text"))

    return page
