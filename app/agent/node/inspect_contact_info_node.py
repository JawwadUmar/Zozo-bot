import logging

from app.agent.state import ApplicationState
from app.config.selectors import CONTACT_INFO_HEADER
from app.config.session_manager import browser_manager
from app.utils.locator import get_first_available_locator

logger = logging.getLogger(__name__)


async def inspect_contact_info_node(state: ApplicationState) -> dict[str, object]:
    """Read the visible contact controls without changing their values."""
    try:
        page = browser_manager.get_page(state.get("session_id", ""))
        header = await get_first_available_locator(page, CONTACT_INFO_HEADER)
        if header is None:
            raise RuntimeError("Contact information section was not found.")
        section = header.locator("xpath=ancestor::div[.//input or .//select or .//textarea][1]")
        controls = section.locator("input:not([type=hidden]), select, textarea")
        fields = []
        for index in range(await controls.count()):
            control = controls.nth(index)
            if not await control.is_visible():
                continue
            details = await control.evaluate("""el => ({
                id: el.id, tag: el.tagName.toLowerCase(), type: el.type,
                label: el.labels?.[0]?.innerText?.trim() ||
                    el.closest('[componentkey]')?.querySelector('p')?.innerText?.trim() ||
                    el.getAttribute('aria-label') || el.getAttribute('placeholder') || '',
                disabled: el.disabled || el.readOnly
            })""")
            if not details["id"]:
                raise RuntimeError("A contact field has no ID and cannot be safely identified.")
            details["value"] = await control.input_value()
            details["empty"] = not details["value"].strip()
            fields.append(details)
        if not fields:
            raise RuntimeError("No visible contact information fields were found.")
        logger.info("Inspected %d contact fields", len(fields))
        return {"contact_info_fields": fields, "action_status": "contact_info_inspected", "error": None}
    except Exception as exc:
        logger.warning("Could not inspect contact information: %s", exc)
        return {"contact_info_fields": [], "action_status": "contact_info_inspection_failed", "error": str(exc)}
