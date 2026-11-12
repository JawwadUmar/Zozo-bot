from __future__ import annotations

import pytest
from app.linkedin.page_classifier import classify_page
from app.linkedin.application_state import ApplicationTracker
from app.profile.profile_loader import parse_resume_text
from tests.conftest import create_mock_locator


@pytest.mark.asyncio
async def test_page_classifier_classifies_search_and_modals(mock_page):
    # Search page without modal
    mock_page.url = "https://www.linkedin.com/jobs/search/?keywords=python"
    empty_modal = create_mock_locator("", is_visible=False, count=0)
    body_loc = create_mock_locator("LinkedIn Jobs Search Results", is_visible=True, count=1)

    def locator_side_effect(selector, *args, **kwargs):
        if "dialog" in selector or "artdeco-modal" in selector:
            return empty_modal
        return body_loc

    mock_page.locator.side_effect = locator_side_effect
    page_type = await classify_page(mock_page)
    assert page_type == "search_results"

    # Search page with open review modal
    review_modal = create_mock_locator("Review your application Submit application", is_visible=True, count=1)
    def modal_side_effect(selector, *args, **kwargs):
        if "dialog" in selector or "artdeco-modal" in selector:
            return review_modal
        return body_loc

    mock_page.locator.side_effect = modal_side_effect
    page_type = await classify_page(mock_page)
    assert page_type == "review_page"


def test_application_tracker_records_and_prevents_duplicate(tmp_path):
    tracker_file = tmp_path / "test_tracker.json"
    tracker = ApplicationTracker(storage_path=str(tracker_file))

    url = "https://www.linkedin.com/jobs/view/999888777/?ref=search"
    assert tracker.is_applied(url) is False

    tracker.mark_applied(url, "Software Engineer", "Google", status="applied")
    assert tracker.is_applied(url) is True
    assert tracker.is_applied("https://www.linkedin.com/jobs/view/999888777/") is True

    stats = tracker.get_session_stats()
    assert stats["attempts"] == 1
    assert stats["successes"] == 1


def test_resume_parser_populates_candidate_profile():
    sample_resume = """
# Jawwad Umar — Resume
- Phone Number: 9155027072
- Email: jawwadumar99@gmail.com
- Current Job Title: Software Development Engineer - 2 (SDE-2)
- Total Work Experience: 3 years
- Current Employer: Tata Consultancy Services
"""
    profile = parse_resume_text(sample_resume)
    assert profile.name == "Jawwad Umar"
    assert profile.phone == "9155027072"
    assert profile.email == "jawwadumar99@gmail.com"
    assert profile.years_of_experience == 3
    assert profile.current_title == "Software Development Engineer - 2 (SDE-2)"
    assert profile.current_company == "Tata Consultancy Services"
