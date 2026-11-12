from __future__ import annotations

DAILY_SUBMISSION_LIMIT_TEXT = (
    "We limit daily submissions to maintain quality and prevent bots"
)

# Additional rate limit and account restriction signals
RESTRICTION_PHRASES = [
    DAILY_SUBMISSION_LIMIT_TEXT,
    "You've reached the daily application limit",
    "Please try applying again tomorrow",
    "To protect our members, we limit the number of applications",
    "Your account has been restricted",
]


class DailySubmissionLimitReached(Exception):
    """Raised when LinkedIn blocks more applications for the day."""


class AccountRestrictedException(Exception):
    """Raised when LinkedIn displays an account warning or restriction."""


async def is_daily_submission_limit_visible(page) -> bool:
    """Check if LinkedIn daily submission limit or restriction text is visible on the page."""
    try:
        body_text = await page.locator("body").inner_text(timeout=1000)
        if not isinstance(body_text, str):
            return False
    except Exception:
        return False

    normalized_text = " ".join(body_text.split())
    for phrase in RESTRICTION_PHRASES:
        if phrase in normalized_text:
            return True
    return False


async def stop_if_daily_submission_limit_visible(page) -> None:
    """Raise DailySubmissionLimitReached immediately if daily limit or restriction is present."""
    if await is_daily_submission_limit_visible(page):
        raise DailySubmissionLimitReached(
            "LinkedIn daily application limit reached. Save jobs and apply tomorrow."
        )
