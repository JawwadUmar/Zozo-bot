from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage

from app.agent.state import AgentState
from app.agent.models import (
    PageObservation,
    PageUnderstanding,
    AgentAction,
    ActionResult,
    VerificationResult,
    ActionType,
    PageType,
)
from app.agent.prompts import (
    PAGE_UNDERSTANDING_PROMPT,
    ACTION_DECISION_PROMPT,
    FORM_ANSWER_PROMPT,
    VERIFICATION_PROMPT,
)
from app.browser.observer import PageObserver
from app.browser.element_resolver import ElementResolver
from app.browser.page_context import PageContextManager
from app.browser.screenshots import capture_on_error
from app.browser import playwright_tools as tools
from app.models.llm_factory import get_decision_llm, get_observation_llm
from app.linkedin.daily_limit import is_daily_submission_limit_visible
from app.human.intervention import request_human_input


observer = PageObserver()
resolver = ElementResolver()
context_mgr = PageContextManager()


async def observe_page_node(state: AgentState) -> Dict[str, Any]:
    """Capture current page state and interactive elements."""
    page = state["page"]
    print("🤖 Zozo: Observing current page state...")

    # Wait for page settling
    await context_mgr.wait_for_page_stable(page, timeout_ms=3000)

    # Check for daily submission limit
    daily_limit = await is_daily_submission_limit_visible(page)
    if daily_limit:
        print("🚨 Zozo: Daily submission limit detected!")
        return {
            "daily_limit_reached": True,
            "completion_status": "limit_reached",
        }

    # Extract structured observation
    observation = await observer.observe_page(page)

    previous_url = state.get("current_url")
    previous_title = state.get("current_title")
    page_changed = await context_mgr.detect_page_change(page, previous_url, previous_title)

    return {
        "current_url": observation.url,
        "current_title": observation.title,
        "previous_page_url": previous_url,
        "page_representation": observation.model_dump(),
        "page_changed": page_changed,
        "daily_limit_reached": False,
    }


async def understand_page_node(state: AgentState) -> Dict[str, Any]:
    """Analyze the page observation with LLM to classify application stage."""
    if state.get("daily_limit_reached"):
        return {"application_stage": "daily_limit"}

    page_rep = state.get("page_representation", {})
    url = page_rep.get("url", "")
    title = page_rep.get("title", "")
    buttons = page_rep.get("buttons", [])
    form_fields = page_rep.get("form_fields", [])
    dialogs = page_rep.get("dialogs", [])
    has_modal = page_rep.get("has_modal", False)
    progress = page_rep.get("progress_indicator")
    errors = page_rep.get("error_messages", [])
    visible_text = page_rep.get("visible_text", "")

    # Check for immediate success modal
    visible_text_lower = visible_text.lower()
    if "application submitted" in visible_text_lower or "your application was sent" in visible_text_lower:
        print("✅ Zozo: Success screen detected! Application already submitted.")
        return {
            "application_stage": "submitted",
            "completion_status": "submitted",
        }

    # Check for login or security challenge
    if "checkpoint/challenge" in url or "security-check" in url:
        return {
            "application_stage": "auth_challenge",
            "human_intervention_needed": True,
            "human_intervention_reason": "LinkedIn security checkpoint / verification challenge encountered.",
        }

    # Prepare prompt for LLM
    prompt_text = PAGE_UNDERSTANDING_PROMPT.format(
        url=url,
        title=title,
        has_modal=has_modal,
        progress_indicator=progress or "N/A",
        error_messages=", ".join(errors) if errors else "None",
        dialogs_json=json.dumps(dialogs[:5], indent=2),
        buttons_json=json.dumps([{"role": b.get("role"), "name": b.get("name"), "text": b.get("text")} for b in buttons[:15]], indent=2),
        form_fields_json=json.dumps([{"type": f.get("input_type"), "name": f.get("name"), "label": f.get("label"), "value": f.get("value")} for f in form_fields[:15]], indent=2),
        visible_text=visible_text[:1500],
    )

    llm = get_observation_llm()
    try:
        structured_llm = llm.with_structured_output(PageUnderstanding)
        understanding: PageUnderstanding = await structured_llm.ainvoke([
            SystemMessage(content="You analyze web pages and return structured PageUnderstanding objects."),
            HumanMessage(content=prompt_text),
        ])
        stage = understanding.page_type.value
    except Exception as e:
        print(f"⚠️ Zozo: Structured understanding fallback: {e}")
        # Rule-based fallback
        if has_modal:
            # Check buttons for submit
            has_submit = any("submit" in (b.get("name") or "").lower() for b in buttons)
            if has_submit:
                stage = "review_page"
            elif any("resume" in (f.get("name") or "").lower() for f in form_fields) or "resume" in visible_text_lower:
                stage = "resume_page"
            else:
                stage = "application_form"
        elif any("easy apply" in (b.get("name") or "").lower() for b in buttons):
            stage = "job_details"
        else:
            stage = "unknown"

    print(f"🤖 Zozo: Understood page stage as '{stage}'")
    return {"application_stage": stage}


async def decide_action_node(state: AgentState) -> Dict[str, Any]:
    """Decide next action using decision LLM based on page state and candidate profile."""
    page_rep = state.get("page_representation", {})
    buttons = page_rep.get("buttons", [])
    form_fields = page_rep.get("form_fields", [])
    stage = state.get("application_stage", "unknown")
    errors = page_rep.get("error_messages", [])
    profile_data = state.get("candidate_profile", {})
    history = state.get("action_history", [])[-5:]

    # Check for "Follow company" checkbox on review page
    if stage == "review_page":
        for field in form_fields:
            name_label = f"{field.get('name') or ''} {field.get('label') or ''}".lower()
            if "follow" in name_label and field.get("input_type") == "checkbox":
                if field.get("value") in ("true", "checked", "on"):
                    print("🤖 Zozo: Decided to uncheck 'Follow company' checkbox.")
                    return {
                        "current_action": {
                            "action_type": "uncheck",
                            "target_description": "Follow company checkbox",
                            "target_role": "checkbox",
                            "target_name": field.get("name") or field.get("label"),
                            "value": None,
                            "reason": "Uncheck follow company before submitting",
                            "confidence": 0.95,
                            "requires_confirmation": False,
                        }
                    }

    prompt_text = ACTION_DECISION_PROMPT.format(
        candidate_name=profile_data.get("name", "Candidate"),
        candidate_email=profile_data.get("email", ""),
        candidate_phone=profile_data.get("phone", ""),
        candidate_location=profile_data.get("location", ""),
        candidate_yoe=profile_data.get("years_of_experience", 3),
        candidate_role=profile_data.get("current_title", ""),
        candidate_company=profile_data.get("current_company", ""),
        candidate_skills=", ".join(profile_data.get("skills", [])[:20]),
        candidate_work_auth=str(profile_data.get("work_authorization", {})),
        candidate_default_answers=str(profile_data.get("default_answers", {})),
        application_stage=stage,
        page_type=stage,
        page_description=page_rep.get("title", ""),
        progress_indicator=page_rep.get("progress_indicator") or "N/A",
        error_messages=", ".join(errors) if errors else "None",
        buttons_json=json.dumps([{"role": b.get("role"), "name": b.get("name"), "text": b.get("text")} for b in buttons[:20]], indent=2),
        form_fields_json=json.dumps([{"type": f.get("input_type"), "name": f.get("name"), "label": f.get("label"), "value": f.get("value"), "options": f.get("options")} for f in form_fields[:20]], indent=2),
        action_history=json.dumps(history, indent=2),
    )

    llm = get_decision_llm()
    try:
        structured_llm = llm.with_structured_output(AgentAction)
        action: AgentAction = await structured_llm.ainvoke([
            SystemMessage(content="You are a precise browser automation planner. Always output valid AgentAction JSON grounded in observed elements."),
            HumanMessage(content=prompt_text),
        ])
        action_dict = action.model_dump()
    except Exception as e:
        print(f"⚠️ Zozo: Structured decision fallback: {e}")
        # Rule-based fallback decision based on visible buttons
        if stage == "job_details":
            action_dict = {
                "action_type": "click",
                "target_description": "Easy Apply button",
                "target_role": "button",
                "target_name": "Easy Apply",
                "value": None,
                "reason": "Click Easy Apply to initiate application",
                "confidence": 0.8,
                "requires_confirmation": False,
            }
        elif stage == "review_page":
            action_dict = {
                "action_type": "click",
                "target_description": "Submit application button",
                "target_role": "button",
                "target_name": "Submit application",
                "value": None,
                "reason": "Submit final application",
                "confidence": 0.9,
                "requires_confirmation": False,
            }
        else:
            action_dict = {
                "action_type": "click",
                "target_description": "Next step button",
                "target_role": "button",
                "target_name": "Next",
                "value": None,
                "reason": "Proceed to next step in application",
                "confidence": 0.7,
                "requires_confirmation": False,
            }

    print(f"🤖 Zozo: Decided action -> {action_dict.get('action_type')} on '{action_dict.get('target_name')}' ({action_dict.get('reason')})")
    return {"current_action": action_dict}


async def resolve_element_node(state: AgentState) -> Dict[str, Any]:
    """Resolve the target element using ElementResolver with priority strategies."""
    page = state["page"]
    action_dict = state.get("current_action") or {}
    action = AgentAction(**action_dict)

    print(f"🤖 Zozo: Resolving target element '{action.target_name or action.target_description}'...")
    locator = await resolver.resolve_element(page, action)

    if locator is not None:
        print("✅ Zozo: Element successfully resolved and verified.")
        return {
            "resolved_locator": locator,
            "retry_count": 0,
        }
    else:
        retries = state.get("retry_count", 0) + 1
        max_retries = state.get("max_retries", 3)
        print(f"⚠️ Zozo: Failed to resolve element. Retry {retries}/{max_retries}")

        if retries >= max_retries:
            return {
                "resolved_locator": None,
                "retry_count": retries,
                "human_intervention_needed": True,
                "human_intervention_reason": f"Cannot find element matching '{action.target_description}' ({action.target_name}) after {retries} attempts.",
            }

        return {
            "resolved_locator": None,
            "retry_count": retries,
        }


async def execute_action_node(state: AgentState) -> Dict[str, Any]:
    """Execute the chosen Playwright action using verified tools."""
    page = state["page"]
    action_dict = state.get("current_action") or {}
    action_type = action_dict.get("action_type")
    value = action_dict.get("value")
    locator = state.get("resolved_locator")

    action_count = state.get("action_count", 0) + 1
    result: ActionResult

    try:
        if action_type == ActionType.CLICK:
            if locator is not None:
                result = await tools.click_element(page, locator)
            else:
                result = ActionResult(success=False, message="No locator resolved to click", error="Missing locator")

        elif action_type == ActionType.FILL:
            if locator is not None and value is not None:
                result = await tools.fill_input(page, locator, str(value))
            else:
                result = ActionResult(success=False, message="Missing locator or value for fill", error="Invalid arguments")

        elif action_type == ActionType.SELECT:
            if locator is not None and value is not None:
                result = await tools.select_option(page, locator, str(value))
            else:
                result = ActionResult(success=False, message="Missing locator or option value", error="Invalid arguments")

        elif action_type == ActionType.CHECK:
            if locator is not None:
                result = await tools.check_checkbox(page, locator)
            else:
                result = ActionResult(success=False, message="Missing locator to check", error="Missing locator")

        elif action_type == ActionType.UNCHECK:
            if locator is not None:
                result = await tools.uncheck_checkbox(page, locator)
            else:
                result = ActionResult(success=False, message="Missing locator to uncheck", error="Missing locator")

        elif action_type == ActionType.SCROLL:
            direction = "down" if (value or "").lower() != "up" else "up"
            result = await tools.scroll_page(page, direction=direction)

        elif action_type == ActionType.WAIT:
            result = await tools.wait_for_element(page, action_dict.get("target_description", "page settle"), timeout=3000)

        else:
            result = ActionResult(success=True, message=f"Action '{action_type}' acknowledged", page_changed=False)

    except Exception as e:
        await capture_on_error(page, f"exec_failed_{action_type}")
        result = ActionResult(success=False, message=f"Execution exception: {e}", error=str(e))

    # Append to history
    history_entry = {
        "step": action_count,
        "action": action_dict,
        "result": result.model_dump(),
    }
    action_history = list(state.get("action_history", []))
    action_history.append(history_entry)

    print(f"🤖 Zozo: Action executed -> {result.message} (success={result.success})")

    return {
        "action_result": result.model_dump(),
        "action_history": action_history,
        "action_count": action_count,
        "resolved_locator": None,
    }


async def verify_action_node(state: AgentState) -> Dict[str, Any]:
    """Verify outcome of executed action and check if workflow completed."""
    page = state["page"]
    action_dict = state.get("current_action") or {}
    action_result_dict = state.get("action_result") or {}
    action_success = action_result_dict.get("success", False)

    # Settle page
    await context_mgr.wait_for_page_stable(page, timeout_ms=2500)

    # Check for daily submission limit after action
    if await is_daily_submission_limit_visible(page):
        return {
            "daily_limit_reached": True,
            "completion_status": "limit_reached",
        }

    # Verify if submit was just executed
    target_name = (action_dict.get("target_name") or "").lower()
    if "submit application" in target_name and action_success:
        print("✅ Zozo: Submit application action completed! Verifying submission...")
        # Check for confirmation modal or text
        try:
            body = await page.locator("body").inner_text(timeout=2000)
            if "application submitted" in body.lower() or "your application was sent" in body.lower():
                print("🎉 Zozo: Application submission confirmed!")
                return {
                    "completion_status": "submitted",
                    "verification_result": {
                        "action_succeeded": True,
                        "page_state_changed": True,
                        "expected_outcome_met": True,
                        "details": "Application successfully submitted",
                    },
                }
        except Exception:
            pass

        # If submit was clicked without error, mark as submitted
        return {
            "completion_status": "submitted",
            "verification_result": {
                "action_succeeded": True,
                "page_state_changed": True,
                "expected_outcome_met": True,
                "details": "Application submit button clicked",
            },
        }

    verification = {
        "action_succeeded": action_success,
        "page_state_changed": action_result_dict.get("page_changed", False),
        "expected_outcome_met": action_success,
        "details": action_result_dict.get("message", ""),
        "should_retry": not action_success,
        "should_inspect": not action_success,
    }

    return {"verification_result": verification}


async def handle_human_intervention_node(state: AgentState) -> Dict[str, Any]:
    """Pause workflow and ask human for guidance or intervention."""
    reason = state.get("human_intervention_reason") or "Manual assistance needed to proceed."
    last_action = (state.get("current_action") or {}).get("target_description")
    context = {
        "URL": state.get("current_url"),
        "Stage": state.get("application_stage"),
        "Last Action": last_action,
        "Action Count": state.get("action_count"),
    }
    current_job = state.get("current_job")

    response = await request_human_input(reason=reason, context=context, current_job=current_job)

    return {
        "human_intervention_needed": False,
        "human_intervention_reason": None,
        "human_response": response,
        "retry_count": 0,
    }
