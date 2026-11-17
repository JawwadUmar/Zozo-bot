import logging

from app.agent.state import ApplicationState
from app.config.selectors import CONTACT_INFO_HEADER, NEXT_STEP_BUTTON
from app.config.session_manager import browser_manager
from app.utils.locator import get_first_available_locator

logger = logging.getLogger(__name__)


async def click_next_node(state: ApplicationState) -> dict[str, object]:
    """Advance from contact information and wait for the section to change."""
    try:
        page = browser_manager.get_page(state.get("session_id", ""))
        header = await get_first_available_locator(page, CONTACT_INFO_HEADER)
        button = await get_first_available_locator(page, NEXT_STEP_BUTTON)
        if header is None or button is None:
            raise RuntimeError("Contact information or Next button was not found.")
        dialog = page.locator("[role='dialog']:visible").first
        has_dialog = await dialog.count() > 0
        await button.click()
        await header.wait_for(state="hidden", timeout=15000)
        if has_dialog:
            await dialog.wait_for(state="visible", timeout=15000)
        logger.info("Advanced past contact information")
        return {"action_status": "next_section_loaded", "current_form_step": "next_section", "error": None}
    except Exception as exc:
        logger.warning("Could not advance from contact information: %s", exc)
        return {"action_status": "next_section_failed", "error": str(exc)}
