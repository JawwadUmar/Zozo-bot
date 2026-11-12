from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch
from app.agent.graph import build_easy_apply_graph
from app.agent.state import create_initial_state
from app.agent.nodes import (
    observe_page_node,
    understand_page_node,
    decide_action_node,
    execute_action_node,
    verify_action_node,
    handle_human_intervention_node,
)
from app.agent.decisions import (
    route_after_understand,
    route_after_decision,
    route_after_resolve,
    route_after_verify,
)
from app.agent.models import AgentAction, ActionType


def test_graph_builds_without_error():
    app = build_easy_apply_graph()
    assert app is not None


@pytest.mark.asyncio
async def test_observe_node_updates_state(mock_page, sample_candidate_profile):
    mock_page.evaluate.return_value = {
        "hasModal": True,
        "dialogs": [{"title": "Apply", "role": "dialog"}],
        "progressIndicator": "Step 1 of 3",
        "errorMessages": [],
        "interactiveElements": [],
        "visibleText": "Easy Apply Form",
    }

    state = create_initial_state(mock_page, sample_candidate_profile.model_dump())
    result = await observe_page_node(state)

    assert result["daily_limit_reached"] is False
    assert result["page_representation"]["has_modal"] is True
    assert result["current_url"] == mock_page.url


@pytest.mark.asyncio
async def test_execute_node_updates_history(mock_page, sample_candidate_profile):
    state = create_initial_state(mock_page, sample_candidate_profile.model_dump())
    state["current_action"] = {
        "action_type": "scroll",
        "target_description": "Page scroll",
        "target_role": None,
        "target_name": None,
        "value": "down",
        "reason": "Scroll to view more elements",
        "confidence": 1.0,
        "requires_confirmation": False,
    }

    result = await execute_action_node(state)
    assert result["action_count"] == 1
    assert len(result["action_history"]) == 1
    assert result["action_history"][0]["action"]["action_type"] == "scroll"
    assert result["action_result"]["success"] is True


@pytest.mark.asyncio
async def test_verify_node_detects_submission(mock_page, sample_candidate_profile):
    state = create_initial_state(mock_page, sample_candidate_profile.model_dump())
    state["current_action"] = {
        "action_type": "click",
        "target_name": "Submit application",
        "target_description": "Submit button",
    }
    state["action_result"] = {"success": True, "message": "Clicked", "page_changed": True}

    body_mock = AsyncMock()
    body_mock.inner_text.return_value = "Your application was sent to Google! Application submitted."
    mock_page.locator.return_value = body_mock

    result = await verify_action_node(state)
    assert result.get("completion_status") == "submitted"
    assert result["verification_result"]["action_succeeded"] is True


@pytest.mark.asyncio
async def test_human_intervention_node_and_resumption(sample_candidate_profile, mock_page):
    state = create_initial_state(mock_page, sample_candidate_profile.model_dump())
    state["human_intervention_needed"] = True
    state["human_intervention_reason"] = "Ambiguous question detected"
    state["retry_count"] = 3

    with patch("app.agent.nodes.request_human_input", new=AsyncMock(return_value="Kolkata")):
        result = await handle_human_intervention_node(state)

        assert result["human_intervention_needed"] is False
        assert result["human_response"] == "Kolkata"
        assert result["retry_count"] == 0


def test_conditional_edges_routing(mock_page, sample_candidate_profile):
    state = create_initial_state(mock_page, sample_candidate_profile.model_dump())

    # Understand routing
    state["daily_limit_reached"] = True
    assert route_after_understand(state) == "daily_limit"

    state["daily_limit_reached"] = False
    state["application_stage"] = "submitted"
    assert route_after_understand(state) == "complete"

    state["application_stage"] = "application_form"
    assert route_after_understand(state) == "decide_action"

    # Decision routing
    state["current_action"] = {"action_type": "complete"}
    assert route_after_decision(state) == "complete"

    state["current_action"] = {"action_type": "ask_human"}
    assert route_after_decision(state) == "human_intervention"

    state["current_action"] = {"action_type": "scroll"}
    assert route_after_decision(state) == "execute_action"

    state["current_action"] = {"action_type": "click"}
    assert route_after_decision(state) == "resolve_element"

    # Verify routing
    state["completion_status"] = "submitted"
    assert route_after_verify(state) == "complete"

    state["completion_status"] = None
    state["action_count"] = 100
    state["max_actions"] = 50
    assert route_after_verify(state) == "human_intervention"
