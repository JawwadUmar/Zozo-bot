from __future__ import annotations

import re
from typing import Any
from app.linkedin.daily_limit import is_daily_submission_limit_visible


async def classify_page(page: Any) -> str:
    """Classify current LinkedIn page state based on URL, DOM signals, and modal state."""
    # 1. Check for daily application limit first
    if await is_daily_submission_limit_visible(page):
        return "daily_limit"

    url = page.url.lower()

    # 2. Check for login / security checkpoint
    if "checkpoint/challenge" in url or "security-check" in url:
        return "challenge"
    if "/login" in url or "uas/login" in url:
        return "login_page"

    # 3. Check for open modals/dialogs (Easy Apply workflow)
    try:
        modal = page.locator("div[role='dialog']:visible, .artdeco-modal:visible")
        if await modal.count() > 0:
            modal_text = await modal.first.inner_text(timeout=1000)
            modal_text_lower = modal_text.lower()

            if "application submitted" in modal_text_lower or "your application was sent" in modal_text_lower:
                return "success_page"

            if "review your application" in modal_text_lower or "submit application" in modal_text_lower:
                return "review_page"

            if "include an updated resume" in modal_text_lower or "attach resume" in modal_text_lower:
                return "resume_page"

            if "continue applying?" in modal_text_lower or "discard application?" in modal_text_lower:
                return "warning_modal"

            if "easy apply" in modal_text_lower or "contact info" in modal_text_lower or "additional questions" in modal_text_lower:
                return "application_form"

            return "application_form"
    except Exception:
        pass

    # 4. Check for job search results page vs individual job page
    if "/jobs/search" in url:
        return "search_results"

    if "/jobs/view" in url or "/jobs/collections" in url:
        return "job_details"

    if "/feed" in url:
        return "feed"

    return "unknown"
