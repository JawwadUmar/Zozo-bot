from playwright.async_api import Page

from app.agent.state import ApplicationState
from app.config.config import EMAIL, PASSWORD
from app.config.selectors import (
    LOGIN_EMAIL_INPUT,
    LOGIN_PASSWORD_INPUT,
    LOGIN_SUBMIT_BUTTON,
    LOGIN_SUCCESS_URL_PATTERN,
)
from app.config.session_manager import browser_manager
from app.utils.human import human_delay, human_typing
from app.utils.locator import get_first_available_locator


async def handle_login(_state: ApplicationState) -> dict[str, object]:
    """Log in through the browser session created by ``initialize_browser``."""
    session_id = _state.get("session_id")
    if not session_id:
        return {
            "is_logged_in": False,
            "action_status": "login_failed",
            "error": "Cannot log in: browser session_id is missing.",
        }

    try:
        page: Page = browser_manager.get_page(session_id)
        await page.goto("https://www.linkedin.com/login/")
        await page.wait_for_load_state("domcontentloaded")

        # A persisted LinkedIn session may redirect away from the login page.
        if "/feed" in page.url:
            return {
                "is_logged_in": True,
                "action_status": "login_succeeded",
                "error": None,
            }

        if not EMAIL or not PASSWORD:
            raise RuntimeError("LinkedIn email or password is not configured.")

        username = await get_first_available_locator(page, LOGIN_EMAIL_INPUT)
        password = await get_first_available_locator(page, LOGIN_PASSWORD_INPUT)
        submit_button = await get_first_available_locator(page, LOGIN_SUBMIT_BUTTON)
        if username is None or password is None or submit_button is None:
            raise RuntimeError("Could not find all required LinkedIn login controls.")

        await username.click()
        await human_typing(username, EMAIL)
        await password.click()
        await human_typing(password, PASSWORD)
        await submit_button.click()

        # Allow manual completion of a verification prompt in the visible browser.
        await page.wait_for_url(LOGIN_SUCCESS_URL_PATTERN[0], timeout=120_000)
        await human_delay(2, 4)

        return {
            "is_logged_in": True,
            "action_status": "login_succeeded",
            "error": None,
        }
    except Exception as exc:
        return {
            "is_logged_in": False,
            "action_status": "login_failed",
            "error": f"Login failed or timed out: {exc}",
        }
