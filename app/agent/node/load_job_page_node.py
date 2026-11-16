from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from playwright.async_api import Page

from app.agent.state import ApplicationState
from app.config.selectors import JOB_CARD_CONTAINER
from app.config.session_manager import browser_manager
from app.utils.human import human_delay
from app.utils.locator import get_first_available_locator
from app.config.config import JOBLINK


def _validate_job_link(job_link: str) -> str:
    parsed = urlparse(job_link.strip())
    hostname = (parsed.hostname or "").lower()
    if (
        parsed.scheme not in {"http", "https"}
        or not hostname
        or not (hostname == "linkedin.com" or hostname.endswith(".linkedin.com"))
    ):
        raise ValueError("job_link must be an HTTP(S) URL on linkedin.com.")
    return urlunparse(parsed)


def _url_for_page(job_link: str, start: int) -> str:
    parsed = urlparse(job_link)
    # The start offset applies to LinkedIn search result pages, not direct jobs.
    if "/jobs/search" not in parsed.path:
        return job_link

    query = parse_qs(parsed.query)
    query["start"] = [str(start)]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


async def load_jobs_page(state: ApplicationState) -> dict[str, object]:
    """Open the user-provided LinkedIn job/search URL in the active session."""
    session_id = state.get("session_id")
    if not session_id:
        return {
            "action_status": "job_page_load_failed",
            "error": "Cannot load job page: browser session_id is missing.",
        }
    if not state.get("is_logged_in", False):
        return {
            "action_status": "job_page_load_failed",
            "error": "Cannot load job page before LinkedIn login succeeds.",
        }

    try:
        job_link = _validate_job_link(state.get("job_link", JOBLINK))
        start = state.get("start", 0)
        if not isinstance(start, int) or start < 0:
            raise ValueError("start must be a non-negative integer.")

        target_url = _url_for_page(job_link, start)
        page: Page = browser_manager.get_page(session_id)
        print(f"Zozo: Opening {target_url}")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60_000)
        await human_delay(1, 2)

        is_search_page = "/jobs/search" in urlparse(target_url).path
        total_cards = 0
        if is_search_page:
            card_locator = await get_first_available_locator(
                page, JOB_CARD_CONTAINER, timeout=10_000
            )
            if card_locator is not None:
                total_cards = await page.locator(JOB_CARD_CONTAINER[0]).count()

        return {
            "is_search_page": is_search_page,
            "total_cards_on_page": total_cards,
            "current_card_index": 0,
            "action_status": (
                "job_search_loaded" if is_search_page else "job_page_loaded"
            ),
            "error": None,
        }
    except Exception as exc:
        return {
            "action_status": "job_page_load_failed",
            "error": f"Could not load the provided job link: {exc}",
        }
