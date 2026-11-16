from contextlib import suppress
from uuid import uuid4
from playwright.async_api import async_playwright

from app.config.config import USER_DATA_DIRECTORY
from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager


async def initialize_browser(_state: ApplicationState) -> dict[str, str]:
    """Start a persistent Chromium context and register its live handles.

    Playwright objects stay in the process-local session manager; only the
    serializable session ID is returned to LangGraph state.
    """
    session_id = str(uuid4())
    playwright = await async_playwright().start()
    context = None

    try:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIRECTORY,
            headless=False
        )

        # A persistent context may start with a page already open.
        page = context.pages[0] if context.pages else await context.new_page()

        browser_manager.register(
            session_id=session_id,
            playwright=playwright,
            context=context,
            page=page
        )

        return {
            "session_id": session_id,
            "action_status": "browser_initialized"
        }

    except Exception:
        # Clean up partially initialized resources before propagating the
        # error so LangGraph can apply its normal retry/error policy.
        if context is not None:
            with suppress(Exception):
                await context.close()
        with suppress(Exception):
            await playwright.stop()
        raise
