from langgraph.graph import END, START, StateGraph

from app.agent.node.handle_login_node import handle_login
from app.agent.node.initialize_browser import initialize_browser
from app.agent.node.load_job_page_node import load_jobs_page
from app.agent.node.extract_jobs_node import extract_jobs_node
from app.agent.node.should_apply_node import should_apply_node
from app.agent.node.click_job_node import click_job_node
from app.agent.node.advance_job_node import advance_job_node
from app.agent.node.next_page_node import next_page_node
from app.agent.node.click_easy_apply_node import click_easy_apply_node
from app.agent.node.inspect_contact_info_node import inspect_contact_info_node
from app.agent.node.fill_contact_info_node import fill_contact_info_node
from app.agent.node.click_next_node import click_next_node
from app.agent.state import ApplicationState
from app.config.config import JOBLINK


def _route_after_extract(state: ApplicationState) -> str:
    if state.get("action_status") == "job_extraction_failed":
        return "end"
    return "evaluate" if state.get("current_page_jobs") else "paginate"


def _route_after_evaluation(state: ApplicationState) -> str:
    return "click" if state.get("should_apply") else "advance"


def _route_after_advance(state: ApplicationState) -> str:
    if state.get("current_card_index", 0) < len(state.get("current_page_jobs", [])):
        return "evaluate"
    return "paginate"


def _route_after_pagination(state: ApplicationState) -> str:
    return "extract" if state.get("has_next_page") else "end"


builder = StateGraph(ApplicationState)
builder.add_node("initialize_browser", initialize_browser)
builder.add_node("handle_login", handle_login)
builder.add_node("load_jobs_page", load_jobs_page)
builder.add_node("extract_jobs_node", extract_jobs_node)
builder.add_node("should_apply_node", should_apply_node)
builder.add_node("click_job_node", click_job_node)
builder.add_node("advance_job_node", advance_job_node)
builder.add_node("next_page_node", next_page_node)
builder.add_node("click_easy_apply_node", click_easy_apply_node)
builder.add_node("inspect_contact_info_node", inspect_contact_info_node)
builder.add_node("fill_contact_info_node", fill_contact_info_node)
builder.add_node("click_next_node", click_next_node)


builder.add_edge(START, "initialize_browser")
builder.add_edge("initialize_browser", "handle_login")
builder.add_conditional_edges(
    "handle_login",
    lambda state: "load_jobs_page" if state.get("is_logged_in") else "end",
    {"load_jobs_page": "load_jobs_page", "end": END},
)
builder.add_edge("load_jobs_page", "extract_jobs_node")
builder.add_conditional_edges(
    "extract_jobs_node",
    _route_after_extract,
    {"evaluate": "should_apply_node", "paginate": "next_page_node", "end": END},
)
builder.add_conditional_edges(
    "should_apply_node",
    _route_after_evaluation,
    {"click": "click_job_node", "advance": "advance_job_node"},
)
builder.add_conditional_edges(
    "click_job_node", lambda state: "apply" if state.get("action_status") == "job_selected" else "advance",
    {"apply": "click_easy_apply_node", "advance": "advance_job_node"},
)
builder.add_conditional_edges(
    "click_easy_apply_node", lambda state: "inspect" if state.get("action_status") == "easy_apply_opened" else "end",
    {"inspect": "inspect_contact_info_node", "end": END},
)
builder.add_conditional_edges(
    "inspect_contact_info_node", lambda state: "fill" if state.get("action_status") == "contact_info_inspected" else "end",
    {"fill": "fill_contact_info_node", "end": END},
)
builder.add_conditional_edges(
    "fill_contact_info_node", lambda state: "next" if state.get("action_status") == "contact_info_filled" else "end",
    {"next": "click_next_node", "end": END},
)
builder.add_edge("click_next_node", END)
builder.add_conditional_edges(
    "advance_job_node",
    _route_after_advance,
    {"evaluate": "should_apply_node", "paginate": "next_page_node"},
)
builder.add_conditional_edges(
    "next_page_node",
    _route_after_pagination,
    {"extract": "extract_jobs_node", "end": END},
)

graph = builder.compile()


if __name__ == "__main__":
    import asyncio
    from pprint import pprint

    from app.config.session_manager import browser_manager

    async def main():
        job_link = JOBLINK
        initial_state: ApplicationState = {
            "session_id": "",
            "job_link": job_link,
            "start": 0,
            "current_page": 1,
            "is_search_page": False,
            "total_cards_on_page": 0,
            "current_card_index": 0,
            "current_page_jobs": [],
            "processed_jobs": [],
            "should_apply": False,
            "has_next_page": False,
            "current_job_title": None,
            "current_company": None,
            "applied_count": 0,
            "daily_limit_reached": False,
            "user_profile": {},
            "resume_path": "",
            "is_logged_in": False,
            "search_query": "",
            "jobs": [],
            "current_job": {},
            "current_form_step": None,
            "form_fields": [],
            "contact_info_fields": [],
            "application_answers": {},
            "recovery_request": None,
            "recovery_result": None,
            "action_status": "starting",
            "application_status": "not_started",
            "error": None,
        }

        final_state = dict(initial_state)
        existing_sessions = set(browser_manager.sessions)
        try:
            final_state = await graph.ainvoke(initial_state)
        except Exception as exc:
            final_state["action_status"] = "graph_failed"
            final_state["error"] = str(exc)
        finally:
            session_ids_to_close = set(browser_manager.sessions) - existing_sessions
            if final_state.get("session_id") and final_state["session_id"] not in existing_sessions:
                session_ids_to_close.add(final_state["session_id"])
            if session_ids_to_close and not final_state.get("session_id"):
                final_state["session_id"] = next(iter(session_ids_to_close))

            print("\nApplication State before browser shutdown:")
            pprint(final_state, sort_dicts=False)

            for session_id in session_ids_to_close:
                try:
                    await browser_manager.close(session_id)
                except Exception as exc:
                    print(f"Browser shutdown encountered an error: {exc}")
            print("Application stopped.")

    asyncio.run(main())
