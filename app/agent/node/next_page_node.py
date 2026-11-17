from urllib.parse import parse_qs, urlparse

from playwright.async_api import Page

from app.agent.state import ApplicationState
from app.config.selectors import (
    JOB_CARD_SELECTOR,
    JOB_CURRENT_PAGE_BUTTON,
    JOB_NEXT_PAGE_BUTTON,
)
from app.config.session_manager import browser_manager
from app.utils.human import human_delay


async def next_page_node(state: ApplicationState) -> dict[str, object]:
    """Click LinkedIn's Next pagination control, or finish when unavailable."""
    session_id = state.get("session_id")
    if not session_id:
        return {
            "has_next_page": False,
            "action_status": "pagination_failed",
            "error": "Cannot paginate: browser session_id is missing.",
        }

    try:
        page: Page = browser_manager.get_page(session_id)
        next_button = page.locator(JOB_NEXT_PAGE_BUTTON)
        if await next_button.count() == 0 or not await next_button.is_visible():
            return {
                "has_next_page": False,
                "action_status": "pagination_complete",
            }
        if not await next_button.is_enabled():
            return {
                "has_next_page": False,
                "action_status": "pagination_complete",
            }

        current_page_button = page.locator(JOB_CURRENT_PAGE_BUTTON).first
        old_page_test_id = (
            await current_page_button.get_attribute("data-testid")
            if await current_page_button.count()
            else None
        )
        first_card = page.locator(JOB_CARD_SELECTOR).first
        old_first_card_key = (
            await first_card.get_attribute("componentkey")
            if await first_card.count()
            else None
        )

        await next_button.click()
        if old_page_test_id or old_first_card_key:
            await page.wait_for_function(
                """({oldPageId, oldCardKey}) => {
                    const current = document.querySelector(
                        'ul[data-testid="pagination-controls-list"] button[aria-current="true"]'
                    );
                    const firstCard = document.querySelector(
                        'div[role="button"][componentkey^="job-card-component-ref-"]'
                    );
                    const pageChanged = oldPageId && current &&
                        current.getAttribute("data-testid") !== oldPageId;
                    const cardsChanged = oldCardKey && firstCard &&
                        firstCard.getAttribute("componentkey") !== oldCardKey;
                    return pageChanged || cardsChanged;
                }""",
                arg={"oldPageId": old_page_test_id, "oldCardKey": old_first_card_key},
                timeout=15_000,
            )
        await human_delay(0.5, 1)

        old_start = state.get("start", 0)
        query_start = parse_qs(urlparse(page.url).query).get("start", [None])[0]
        try:
            new_start = int(query_start) if query_start is not None else old_start + 25
        except (TypeError, ValueError):
            new_start = old_start + 25
        if new_start <= old_start:
            new_start = old_start + 25

        return {
            "has_next_page": True,
            "start": new_start,
            "current_page": state.get("current_page", 1) + 1,
            "current_card_index": 0,
            "action_status": "next_page_loaded",
            "error": None,
        }
    except Exception as exc:
        return {
            "has_next_page": False,
            "action_status": "pagination_failed",
            "error": f"Could not load the next results page: {exc}",
        }
