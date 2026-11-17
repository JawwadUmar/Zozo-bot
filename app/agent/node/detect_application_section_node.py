import logging

from app.config.session_manager import browser_manager
from app.agent.state import ApplicationState

logger = logging.getLogger(__name__)

# Exact visible headings avoid matching question text or a resume mentioned in a question.
SECTION_HEADINGS = {
    "contact_info": "Contact info",
    "resume": "Resume",
    "additional_questions": "Additional Questions",
    "work_experience": "Work experience",
}


async def detect_application_section_node(state: ApplicationState) -> dict:
    page = browser_manager.get_page(state.get("session_id", ""))
    dialog = page.locator("[role='dialog']:visible").first
    root = dialog if await dialog.count() else page
    for section, heading in SECTION_HEADINGS.items():
        locator = root.get_by_text(heading, exact=True).first
        if await locator.count() and await locator.is_visible():
            logger.info("Detected application section: %s", section)
            return {"current_form_step": section, "action_status": "section_detected", "error": None}
    logger.info("Application section is not yet supported")
    return {"current_form_step": "other", "action_status": "unsupported_section", "error": None}
