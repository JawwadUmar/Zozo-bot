from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    # Playwright runtime references
    page: Any  # playwright.async_api.Page
    resolved_locator: Any  # Resolved Playwright locator for current_action

    # Current page state
    current_url: str
    current_title: str
    previous_page_url: Optional[str]
    page_representation: Dict[str, Any]  # Serialized PageObservation
    screenshot_path: Optional[str]
    page_changed: bool

    # Job & Profile context
    current_job: Optional[Dict[str, Any]]  # title, company, url, etc.
    candidate_profile: Dict[str, Any]
    application_stage: str  # job_details, contact_info, resume, additional_questions, work_authorization, work_experience, review, submitted, unknown

    # Action & Execution loop
    action_history: List[Dict[str, Any]]
    current_action: Optional[Dict[str, Any]]  # Serialized AgentAction
    action_result: Optional[Dict[str, Any]]  # Serialized ActionResult
    verification_result: Optional[Dict[str, Any]]  # Serialized VerificationResult

    # Counters & Safety guards
    retry_count: int
    max_retries: int
    action_count: int
    max_actions: int

    # Flags & Terminal states
    error_details: Optional[str]
    human_intervention_needed: bool
    human_intervention_reason: Optional[str]
    human_response: Optional[str]
    completion_status: Optional[str]  # submitted, failed, limit_reached, human_needed, stopped, error
    daily_limit_reached: bool

    # LangGraph conversational/intermediate messages
    messages: List[Any]


def create_initial_state(
    page: Any,
    candidate_profile: Dict[str, Any],
    current_job: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    max_actions: int = 50,
) -> AgentState:
    return {
        "page": page,
        "resolved_locator": None,
        "current_url": "",
        "current_title": "",
        "previous_page_url": None,
        "page_representation": {},
        "screenshot_path": None,
        "page_changed": False,
        "current_job": current_job or {},
        "candidate_profile": candidate_profile,
        "application_stage": "unknown",
        "action_history": [],
        "current_action": None,
        "action_result": None,
        "verification_result": None,
        "retry_count": 0,
        "max_retries": max_retries,
        "action_count": 0,
        "max_actions": max_actions,
        "error_details": None,
        "human_intervention_needed": False,
        "human_intervention_reason": None,
        "human_response": None,
        "completion_status": None,
        "daily_limit_reached": False,
        "messages": [],
    }
