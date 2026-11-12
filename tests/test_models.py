from __future__ import annotations

import pytest
from app.agent.models import (
    ElementInfo,
    PageObservation,
    PageUnderstanding,
    AgentAction,
    ActionResult,
    VerificationResult,
    ActionType,
    PageType,
)


def test_element_info_defaults():
    el = ElementInfo(tag="button", name="Submit", role="button")
    assert el.is_visible is True
    assert el.is_enabled is True
    assert el.is_required is False
    assert el.selector_hint is None


def test_agent_action_validation():
    action = AgentAction(
        action_type=ActionType.CLICK,
        target_description="Submit button",
        target_role="button",
        target_name="Submit application",
        reason="Submit application to job",
        confidence=0.95,
    )
    assert action.action_type == ActionType.CLICK
    assert action.requires_confirmation is False
    assert action.confidence == 0.95


def test_page_understanding_validation():
    understanding = PageUnderstanding(
        page_type=PageType.REVIEW_PAGE,
        description="Candidate is on the final review page",
        available_actions=["submit", "uncheck follow company"],
        current_step_description="Final review step",
        can_proceed=True,
        confidence=0.9,
    )
    assert understanding.page_type == PageType.REVIEW_PAGE
    assert understanding.can_proceed is True
