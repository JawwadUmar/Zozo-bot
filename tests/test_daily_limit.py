from __future__ import annotations

import pytest
from app.linkedin.daily_limit import (
    DAILY_SUBMISSION_LIMIT_TEXT,
    DailySubmissionLimitReached,
    is_daily_submission_limit_visible,
    stop_if_daily_submission_limit_visible,
)
from tests.conftest import create_mock_locator


@pytest.mark.asyncio
async def test_daily_limit_detected(mock_page):
    body_loc = create_mock_locator(
        f"Notice: {DAILY_SUBMISSION_LIMIT_TEXT}. Please come back tomorrow."
    )
    mock_page.locator.return_value = body_loc

    is_limit = await is_daily_submission_limit_visible(mock_page)
    assert is_limit is True

    with pytest.raises(DailySubmissionLimitReached):
        await stop_if_daily_submission_limit_visible(mock_page)


@pytest.mark.asyncio
async def test_daily_limit_not_detected(mock_page):
    body_loc = create_mock_locator("Search Jobs: Software Engineer in Kolkata. 25 results found.")
    mock_page.locator.return_value = body_loc

    is_limit = await is_daily_submission_limit_visible(mock_page)
    assert is_limit is False

    # Should not raise exception
    await stop_if_daily_submission_limit_visible(mock_page)
