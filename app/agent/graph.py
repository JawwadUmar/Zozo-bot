from langgraph.graph import END, START, StateGraph

from app.agent.node.wait_for_human_input_node import wait_for_human_input_node

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
from app.agent.node.detect_application_section_node import detect_application_section_node
from app.agent.node.handle_resume_section_node import handle_resume_section_node
from app.agent.node.inspect_additional_questions_node import inspect_additional_questions_node
from app.agent.node.handle_additional_questions_node import handle_additional_questions_node
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


def _guard_node(name, node):
    async def guarded(state):
        try:
            result = await node(state)
            status = str(result.get("action_status", ""))
            if status.endswith("_failed") or result.get("error"):
                return {**result, "failed_node": name,
                        "error": result.get("error") or f"{name} failed: {status}"}
            return result
        except Exception as exc:
            return {"action_status": "node_failed", "failed_node": name,
                    "error": f"{type(exc).__name__}: {exc}"}
    return guarded


def _route(route):
    def guarded_route(state):
        return "checkpoint" if state.get("failed_node") else route(state)
    return guarded_route


builder = StateGraph(ApplicationState)
nodes = {
    "initialize_browser": initialize_browser, "handle_login": handle_login,
    "load_jobs_page": load_jobs_page, "extract_jobs_node": extract_jobs_node,
    "should_apply_node": should_apply_node, "click_job_node": click_job_node,
    "advance_job_node": advance_job_node, "next_page_node": next_page_node,
    "click_easy_apply_node": click_easy_apply_node,
    "inspect_contact_info_node": inspect_contact_info_node,
    "fill_contact_info_node": fill_contact_info_node, "click_next_node": click_next_node,
    "detect_application_section_node": detect_application_section_node,
    "handle_resume_section_node": handle_resume_section_node,
    "inspect_additional_questions_node": inspect_additional_questions_node,
    "handle_additional_questions_node": handle_additional_questions_node,
}
for name, node in nodes.items():
    builder.add_node(name, _guard_node(name, node))
builder.add_node("wait_for_human_input_node", wait_for_human_input_node)
builder.add_edge(START, "initialize_browser")


def connect(name, route, destinations):
    builder.add_conditional_edges(name, _route(route),
                                  {**destinations, "checkpoint": "wait_for_human_input_node"})

connect("initialize_browser", lambda s: "next", {"next": "handle_login"})
connect("handle_login", lambda s: "next" if s.get("is_logged_in") else "checkpoint", {"next": "load_jobs_page"})
connect("load_jobs_page", lambda s: "next", {"next": "extract_jobs_node"})
connect("extract_jobs_node", _route_after_extract, {"evaluate": "should_apply_node", "paginate": "next_page_node", "end": "wait_for_human_input_node"})
connect("should_apply_node", _route_after_evaluation, {"click": "click_job_node", "advance": "advance_job_node"})
connect("click_job_node", lambda s: "next", {"next": "click_easy_apply_node"})
connect("click_easy_apply_node", lambda s: "next", {"next": "inspect_contact_info_node"})
connect("inspect_contact_info_node", lambda s: "next", {"next": "fill_contact_info_node"})
connect("fill_contact_info_node", lambda s: "next", {"next": "click_next_node"})
connect("click_next_node", lambda s: "detect", {"detect": "detect_application_section_node"})
connect("detect_application_section_node", lambda s: s.get("current_form_step", "other"),
        {"resume": "handle_resume_section_node", "additional_questions": "inspect_additional_questions_node",
         "work_experience": "wait_for_human_input_node", "contact_info": "wait_for_human_input_node", "other": "wait_for_human_input_node"})
connect("handle_resume_section_node", lambda s: "next", {"next": "click_next_node"})
connect("inspect_additional_questions_node", lambda s: "fill", {"fill": "handle_additional_questions_node"})
connect("handle_additional_questions_node", lambda s: "next", {"next": "click_next_node"})
connect("advance_job_node", _route_after_advance, {"evaluate": "should_apply_node", "paginate": "next_page_node"})
connect("next_page_node", _route_after_pagination, {"extract": "extract_jobs_node", "end": "wait_for_human_input_node"})
builder.add_edge("wait_for_human_input_node", END)

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

        try:
            final_state = await graph.ainvoke(initial_state)
        except Exception as exc:
            final_state = {**initial_state, "failed_node": "graph", "error": f"{type(exc).__name__}: {exc}"}
            await wait_for_human_input_node(final_state)
        print("\nWorkflow state:")
        pprint(final_state, sort_dicts=False)
        print("Browser session remains active. Stop this process when you are finished.")
        await asyncio.Event().wait()

    asyncio.run(main())
