DAILY_SUBMISSION_LIMIT_TEXT = (
    "We limit daily submissions to maintain quality and prevent bots"
)


class DailySubmissionLimitReached(Exception):
    """Raised when LinkedIn blocks more applications for the day."""


async def is_daily_submission_limit_visible(page):
    try:
        body_text = await page.locator("body").inner_text(timeout=1000)
    except Exception:
        return False

    normalized_text = " ".join(body_text.split())
    return DAILY_SUBMISSION_LIMIT_TEXT in normalized_text


async def stop_if_daily_submission_limit_visible(page):
    if await is_daily_submission_limit_visible(page):
        raise DailySubmissionLimitReached(
            "LinkedIn daily application limit reached. Save jobs and apply tomorrow."
        )
