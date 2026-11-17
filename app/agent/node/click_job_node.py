from playwright.async_api import Page

from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager
from app.utils.human import human_delay


async def click_job_node(state: ApplicationState) -> dict[str, object]:
    """Select the accepted job card so LinkedIn opens its details pane."""
    session_id = state.get("session_id")
    job = dict(state.get("current_job", {}))
    selector = job.get("selector")
    if not session_id or not selector:
        job["selected"] = False
        return {
            "current_job": job,
            "action_status": "job_selection_failed",
            "error": "Cannot select job: session or card selector is missing.",
        }

    try:
        page: Page = browser_manager.get_page(session_id)
        card = page.locator(str(selector))
        if await card.count() == 0:
            raise RuntimeError("The job card is no longer present on the page.")

        await card.click()
        await human_delay(1, 2)
        job["selected"] = True

        # TODO: invoke the future easy_apply node here. For now, continue to
        # advance_job_node and inspect the next card.
        return {"current_job": job, "action_status": "job_selected"}
    except Exception as exc:
        job["selected"] = False
        return {
            "current_job": job,
            "action_status": "job_selection_failed",
            "error": f"Could not select job card: {exc}",
        }
