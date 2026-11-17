import re

from playwright.async_api import Page

from app.agent.state import ApplicationState
from app.config.selectors import JOB_CARD_SELECTOR
from app.config.session_manager import browser_manager


async def _first_text(locator) -> str:
    """Read the first matching element's visible text, returning empty if absent."""
    try:
        if await locator.count() == 0:
            return ""
        return " ".join((await locator.first.inner_text()).split())
    except Exception:
        return ""


async def _extract_card(card, page_number: int, page_index: int) -> dict[str, object]:
    # job_page.html structure: title p, company p, location p, then a p
    # containing "Posted ...". CSS module class names are intentionally avoided.
    paragraphs = card.locator("p")
    title = await _first_text(paragraphs.first.locator("span"))
    if not title:
        title = await _first_text(paragraphs.first)

    location = await _first_text(paragraphs.nth(2))
    posting = card.locator('p:has-text("Posted")').first
    posting_time = await _first_text(posting.locator("span"))
    if not posting_time:
        posting_time = await _first_text(posting)
    posting_time = re.sub(r"^Posted\s+", "", posting_time, flags=re.IGNORECASE)

    component_key = await card.get_attribute("componentkey") or ""
    card_selector = (
        f'{JOB_CARD_SELECTOR}[componentkey="{component_key}"]'
        if component_key
        else ""
    )

    return {
        "title": title,
        "location": location,
        "posting_time": posting_time,
        "component_key": component_key,
        "selector": card_selector,
        "page_number": page_number,
        "page_index": page_index,
    }


async def extract_jobs_node(state: ApplicationState) -> dict[str, object]:
    """Extract job metadata and click references from the current results page."""
    session_id = state.get("session_id")
    if not session_id:
        return {
            "current_page_jobs": [],
            "total_cards_on_page": 0,
            "action_status": "job_extraction_failed",
            "error": "Cannot extract jobs: browser session_id is missing.",
        }

    try:
        page: Page = browser_manager.get_page(session_id)
        cards = page.locator(f"{JOB_CARD_SELECTOR}:visible")
        card_count = await cards.count()
        page_number = state.get("current_page", 1)
        current_page_jobs = []

        for index in range(card_count):
            card = cards.nth(index)
            current_page_jobs.append(
                await _extract_card(card, page_number, index)
            )

        return {
            "jobs": [*state.get("jobs", []), *current_page_jobs],
            "current_page_jobs": current_page_jobs,
            "current_card_index": 0,
            "total_cards_on_page": len(current_page_jobs),
            "action_status": "jobs_extracted",
            "error": None,
        }
    except Exception as exc:
        return {
            "current_page_jobs": [],
            "total_cards_on_page": 0,
            "action_status": "job_extraction_failed",
            "error": f"Could not extract jobs from the current page: {exc}",
        }
