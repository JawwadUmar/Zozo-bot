import json
import logging

from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager

logger = logging.getLogger(__name__)


async def fill_contact_info_node(state: ApplicationState) -> dict[str, object]:
    """Fill inspected empty contact fields, preserving any current values."""
    try:
        page = browser_manager.get_page(state.get("session_id", ""))
        fields = [dict(field) for field in state.get("contact_info_fields", [])]
        if not fields:
            raise RuntimeError("No inspected contact fields are available.")
        for field in fields:
            if not field["empty"] or field["disabled"]:
                continue
            control = page.locator(f'[id={json.dumps(field["id"])}]')
            current_value = await control.input_value()
            if current_value.strip():
                field["value"] = current_value
                field["empty"] = False
                continue
            label = field["label"].lower()
            if field["tag"] == "select":
                # A select can only accept one of its supplied options.
                options = control.locator("option:not([disabled]):not([value=''])")
                if not await options.count():
                    raise RuntimeError(f"No selectable option for {field['label']}.")
                await control.select_option(value=await options.first.get_attribute("value"))
            else:
                if "first" in label:
                    value = "Alex"
                elif "last" in label:
                    value = "Example"
                elif "phone" in label or field["type"] == "tel":
                    value = "2025550100"
                elif "email" in label or field["type"] == "email":
                    value = "alex@example.com"
                elif "location" in label or "city" in label:
                    value = "New York"
                else:
                    raise RuntimeError(f"No dummy value defined for contact field {field['label']}.")
                await control.fill(value)
                if "location" in label or "city" in label:
                    # LinkedIn's location control requires a typeahead selection.
                    option = page.locator("[role='listbox']:visible [role='option']:visible").first
                    await option.wait_for(state="visible", timeout=5000)
                    await option.click()
            field["value"] = await control.input_value()
            field["empty"] = not field["value"].strip()
            if field["empty"]:
                raise RuntimeError(f"Could not fill contact field {field['label']}.")
        logger.info("Handled empty contact information fields")
        return {"contact_info_fields": fields, "action_status": "contact_info_filled", "error": None}
    except Exception as exc:
        logger.warning("Could not fill contact information: %s", exc)
        return {"action_status": "contact_info_fill_failed", "error": str(exc)}
