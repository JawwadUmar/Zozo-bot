import logging

from app.agent.state import ApplicationState
from app.config.selectors import NEXT_STEP_BUTTON
from app.agent.node.detect_application_section_node import SECTION_HEADINGS
from app.config.session_manager import browser_manager
from app.utils.locator import get_first_available_locator

logger = logging.getLogger(__name__)


async def click_next_node(state: ApplicationState) -> dict[str, object]:
    """Advance from the current section and wait for it to change."""
    try:
        page = browser_manager.get_page(state.get("session_id", ""))
        heading = SECTION_HEADINGS.get(state.get("current_form_step", "contact_info"))
        if not heading:
            raise RuntimeError("Current application section is unknown.")
        header = page.get_by_text(heading, exact=True).first
        button = await get_first_available_locator(page, NEXT_STEP_BUTTON)
        if not await header.count() or not await header.is_visible() or button is None:
            raise RuntimeError("Current section heading or Next button was not found.")
        dialog = page.locator("[role='dialog']:visible").first
        has_dialog = await dialog.count() > 0
        await button.click()
        await header.wait_for(state="hidden", timeout=15000)
        if has_dialog:
            await dialog.wait_for(state="visible", timeout=15000)
        logger.info("Advanced past %s", heading)
        return {"action_status": "next_section_loaded", "current_form_step": "next_section", "error": None}
    except Exception as exc:
        logger.warning("Could not advance application section: %s", exc)
        return {"action_status": "next_section_failed", "error": str(exc)}
