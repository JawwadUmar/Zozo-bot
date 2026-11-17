import logging

from app.agent.state import ApplicationState
from app.config.selectors import CONTACT_INFO_HEADER, EASY_APPLY_BUTTON
from app.config.session_manager import browser_manager
from app.utils.locator import get_first_available_locator

logger = logging.getLogger(__name__)


async def click_easy_apply_node(state: ApplicationState) -> dict[str, object]:
    """Open Easy Apply and wait for its contact information section."""
    try:
        page = browser_manager.get_page(state.get("session_id", ""))
        button = await get_first_available_locator(page, EASY_APPLY_BUTTON, timeout=15000)
        if button is None:
            raise RuntimeError("Easy Apply button was not found.")
        await button.click()
        header = await get_first_available_locator(page, CONTACT_INFO_HEADER, timeout=15000)
        if header is None:
            raise RuntimeError("Contact information section did not load.")
        logger.info("Easy Apply contact information loaded")
        return {"action_status": "easy_apply_opened", "application_status": "in_progress",
                "current_form_step": "contact_info", "contact_info_fields": [], "error": None}
    except Exception as exc:
        logger.warning("Could not open Easy Apply: %s", exc)
        return {"action_status": "easy_apply_failed", "application_status": "failed",
                "contact_info_fields": [], "error": str(exc)}
