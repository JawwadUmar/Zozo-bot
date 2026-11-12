from __future__ import annotations

from typing import Literal
from app.agent.state import AgentState


def route_after_understand(state: AgentState) -> Literal["daily_limit", "human_intervention", "complete", "decide_action"]:
    """Route after page understanding."""
    if state.get("daily_limit_reached"):
        return "daily_limit"

    if state.get("human_intervention_needed"):
        return "human_intervention"

    app_stage = state.get("application_stage", "")
    if app_stage in ("submitted", "success_page"):
        return "complete"

    return "decide_action"


def route_after_decision(state: AgentState) -> Literal["complete", "daily_limit", "human_intervention", "resolve_element", "execute_action"]:
    """Route after action decision."""
    current_action = state.get("current_action") or {}
    action_type = current_action.get("action_type")

    if action_type == "complete":
        return "complete"

    if action_type == "stop":
        reason = current_action.get("reason", "").lower()
        if "daily_limit" in reason:
            return "daily_limit"
        return "human_intervention"

    if action_type == "ask_human" or current_action.get("requires_confirmation"):
        return "human_intervention"

    # Actions that do not require element resolution (e.g. scroll, wait)
    if action_type in ("scroll", "wait"):
        return "execute_action"

    return "resolve_element"


def route_after_resolve(state: AgentState) -> Literal["execute_action", "human_intervention", "decide_action"]:
    """Route after element resolution."""
    resolved_locator = state.get("resolved_locator")
    if resolved_locator is not None:
        return "execute_action"

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)

    if retry_count >= max_retries:
        return "human_intervention"

    # Re-decide with updated context
    return "decide_action"


def route_after_verify(state: AgentState) -> Literal["complete", "daily_limit", "human_intervention", "observe_page"]:
    """Route after action verification."""
    if state.get("daily_limit_reached"):
        return "daily_limit"

    if state.get("completion_status") in ("submitted", "complete"):
        return "complete"

    action_count = state.get("action_count", 0)
    max_actions = state.get("max_actions", 50)
    if action_count >= max_actions:
        return "human_intervention"

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)
    if retry_count >= max_retries:
        return "human_intervention"

    return "observe_page"
