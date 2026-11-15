
# app/agent/nodes/browser.py

from uuid import uuid4
from playwright.async_api import async_playwright

from app.config.config import USER_DATA_DIRECTORY
from app.agent.state import ApplicationState
from app.config.session_manager import browser_manager


async def initialize_browser(state: ApplicationState):

    session_id = str(uuid4())

    # Start Playwright without an async context manager.
    playwright = await async_playwright().start()

    try:
        # Launch persistent browser context.
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIRECTORY,
            headless=False
        )

        # Persistent context may already contain an open page.
        pages = context.pages

        if pages:
            page = pages[0]
        else:
            page = await context.new_page()

        # Register live objects outside LangGraph state.
        await browser_manager.register(
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
        await playwright.stop()
        raise
