from __future__ import annotations

import uuid
from typing import Any, Dict, Optional
from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState, create_initial_state
from app.agent.nodes import (
    observe_page_node,
    understand_page_node,
    decide_action_node,
    resolve_element_node,
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
from app.agent.checkpoints import get_checkpointer
from app.linkedin.daily_limit import DailySubmissionLimitReached


def build_easy_apply_graph() -> Any:
    """Build and compile the LangGraph StateGraph for Easy Apply automation."""
    workflow = StateGraph(AgentState)

    # Add workflow nodes
    workflow.add_node("observe_page", observe_page_node)
    workflow.add_node("understand_page", understand_page_node)
    workflow.add_node("decide_action", decide_action_node)
    workflow.add_node("resolve_element", resolve_element_node)
    workflow.add_node("execute_action", execute_action_node)
    workflow.add_node("verify_action", verify_action_node)
    workflow.add_node("human_intervention", handle_human_intervention_node)

    # Connect nodes
    workflow.add_edge(START, "observe_page")
    workflow.add_edge("observe_page", "understand_page")

    workflow.add_conditional_edges(
        "understand_page",
        route_after_understand,
        {
            "daily_limit": END,
            "human_intervention": "human_intervention",
            "complete": END,
            "decide_action": "decide_action",
        },
    )

    workflow.add_conditional_edges(
        "decide_action",
        route_after_decision,
        {
            "complete": END,
            "daily_limit": END,
            "human_intervention": "human_intervention",
            "execute_action": "execute_action",
            "resolve_element": "resolve_element",
        },
    )

    workflow.add_conditional_edges(
        "resolve_element",
        route_after_resolve,
        {
            "execute_action": "execute_action",
            "human_intervention": "human_intervention",
            "decide_action": "decide_action",
        },
    )

    workflow.add_edge("execute_action", "verify_action")

    workflow.add_conditional_edges(
        "verify_action",
        route_after_verify,
        {
            "complete": END,
            "daily_limit": END,
            "human_intervention": "human_intervention",
            "observe_page": "observe_page",
        },
    )

    workflow.add_edge("human_intervention", "observe_page")

    checkpointer = get_checkpointer()
    compiled_app = workflow.compile(checkpointer=checkpointer)
    return compiled_app


async def run_easy_apply(
    page: Any,
    candidate_profile: Any,
    current_job: Optional[Dict[str, Any]] = None,
    max_actions: int = 50,
    max_retries: int = 3,
) -> Dict[str, Any]:
    """Execute the end-to-end agentic Easy Apply workflow on the current page."""
    app = build_easy_apply_graph()

    profile_dict = (
        candidate_profile.model_dump()
        if hasattr(candidate_profile, "model_dump")
        else dict(candidate_profile)
    )

    initial_state = create_initial_state(
        page=page,
        candidate_profile=profile_dict,
        current_job=current_job,
        max_retries=max_retries,
        max_actions=max_actions,
    )

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    final_state = await app.ainvoke(initial_state, config=config)

    # Check if daily limit stopped the flow
    if final_state.get("daily_limit_reached"):
        raise DailySubmissionLimitReached(
            "LinkedIn daily application limit reached. Save jobs and apply tomorrow."
        )

    return final_state
