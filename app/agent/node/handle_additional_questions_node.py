import json

from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager


async def handle_additional_questions_node(state: ApplicationState) -> dict:
    """Fill unanswered question groups; navigation is handled separately."""
    page = browser_manager.get_page(state.get("session_id", ""))
    questions = state.get("additional_questions", [])
    if not questions:
        raise RuntimeError("Additional questions have not been inspected.")
    answers = state.get("application_answers", {})
    for question in questions:
        controls = question["controls"]
        locators = [page.locator(f'[id={json.dumps(c["id"])}]') for c in controls]
        kind = controls[0]["type"]
        if kind in ("radio", "checkbox"):
            if any([await loc.is_checked() for loc in locators]):
                continue
            enabled = [(c, loc) for c, loc in zip(controls, locators) if not c["disabled"]]
            if not enabled:
                raise RuntimeError(f"No enabled answer for {question['question']}")
            answer = str(answers.get(question["question"], "")).lower()
            choice = next(((c, loc) for c, loc in enabled if answer and c["label"].lower() == answer), None)
            choice = choice or next(((c, loc) for c, loc in enabled if c["label"].lower() in ("not applicable", "decline to self-identify")), enabled[0])
            await choice[1].check()
        else:
            for c, loc in zip(controls, locators):
                if c["disabled"] or (await loc.input_value()).strip():
                    continue
                answer = str(answers.get(question["question"], ""))
                if c["tag"] == "select":
                    options = loc.locator("option:not([disabled]):not([value=''])")
                    if not await options.count():
                        raise RuntimeError(f"No options for {question['question']}")
                    if answer:
                        matches = [i for i in range(await options.count())
                                   if answer.lower() in ((await options.nth(i).inner_text()).strip().lower(),
                                                         (await options.nth(i).get_attribute("value") or "").lower())]
                        if not matches:
                            raise RuntimeError(f"Configured answer is unavailable for {question['question']}")
                        option = options.nth(matches[0])
                    else:
                        preferred = options.filter(has_text="Decline to Self-Identify")
                        option = preferred.first if await preferred.count() else options.first
                    await loc.select_option(value=await option.get_attribute("value"))
                elif c["type"] in ("text", "email", "tel", "number", "textarea"):
                    await loc.fill(answer or ("0" if c["type"] == "number" else "example@example.com" if c["type"] == "email" else "Test"))
                else:
                    raise RuntimeError(f"Unsupported question input type: {c['type']}")
    return {"action_status": "questions_handled", "error": None}
