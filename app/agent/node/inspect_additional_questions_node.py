from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager


async def inspect_additional_questions_node(state: ApplicationState) -> dict:
    """Capture question groups and controls without changing the form."""
    page = browser_manager.get_page(state.get("session_id", ""))
    header = page.get_by_text("Additional Questions", exact=True).first
    section = header.locator("xpath=ancestor::div[.//input or .//select or .//textarea][1]")
    questions = await section.evaluate("""root => {
        const controls = [...root.querySelectorAll('input:not([type=hidden]):not([type=file]), select, textarea')];
        const groups = [];
        for (const el of controls) {
            const fieldset = el.closest('fieldset');
            let group = fieldset && groups.find(g => g.key === fieldset);
            if (!group) {
                const label = el.labels?.[0]?.innerText?.trim();
                const question = fieldset?.querySelector('legend, p')?.innerText?.trim() ||
                    el.getAttribute('aria-label') || label || el.placeholder || '';
                group = {key: fieldset, question, controls: []};
                groups.push(group);
            }
            group.controls.push({id: el.id, tag: el.tagName.toLowerCase(), type: el.type,
                value: el.value, checked: el.checked || false, disabled: el.disabled,
                label: el.labels?.[0]?.innerText?.trim() || ''});
        }
        return groups.map(({question, controls}) => ({question, controls}));
    }""")
    if not questions or any(not c["id"] for q in questions for c in q["controls"]):
        raise RuntimeError("Could not identify all additional question controls safely.")
    return {"additional_questions": questions, "action_status": "questions_inspected", "error": None}
