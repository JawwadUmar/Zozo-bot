from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager


async def handle_resume_section_node(state: ApplicationState) -> dict:
    """Verify the existing selection without changing it."""
    page = browser_manager.get_page(state.get("session_id", ""))
    header = page.get_by_text("Resume", exact=True).first
    section = header.locator("xpath=ancestor::div[.//input[@type='radio']][1]")
    selected = section.locator("input[type='radio']:checked")
    if await selected.count() != 1:
        raise RuntimeError("A selected resume could not be verified.")
    return {"action_status": "resume_verified", "error": None}
