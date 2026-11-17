import asyncio

from app.agent.state import ApplicationState


async def wait_for_human_input_node(state: ApplicationState) -> dict[str, object]:
    """Pause the workflow while the existing browser session remains active."""
    if state.get("error"):
        print(f"Workflow failed in {state.get('failed_node') or 'unknown node'}: {state['error']}", flush=True)
    elif state.get("action_status") in ("unsupported_section", "section_detected"):
        print(f"Paused at application section: {state.get('current_form_step', 'other')}.", flush=True)
    else:
        print(f"Workflow completed its current task ({state.get('action_status', 'finished')}).", flush=True)
    try:
        await asyncio.to_thread(input, "Inspect the browser, then press Enter to finish the workflow: ")
    except EOFError:
        print("Terminal input is unavailable; waiting for confirmation.", flush=True)
        await asyncio.Event().wait()
    return {}
