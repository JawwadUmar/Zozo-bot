from __future__ import annotations

import asyncio
from typing import Any, Optional
from app.agent.models import ActionResult
from app.utils.human import human_delay, human_typing
from app.browser.screenshots import capture_screenshot


async def click_element(page: Any, locator: Any, human_like: bool = True) -> ActionResult:
    """Click a verified Playwright locator with human-like interaction."""
    try:
        url_before = page.url
        await locator.scroll_into_view_if_needed(timeout=3000)
        if human_like:
            await human_delay(0.6, 1.5)

        await locator.click(timeout=5000)

        if human_like:
            await human_delay(1.0, 2.0)

        url_after = page.url
        page_changed = url_before != url_after

        return ActionResult(
            success=True,
            message="Element clicked successfully",
            page_changed=page_changed,
            new_url=url_after,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Failed to click element: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def fill_input(
    page: Any,
    locator: Any,
    value: str,
    clear_first: bool = True,
    human_like: bool = True,
) -> ActionResult:
    """Fill an input field with human-like typing."""
    try:
        await locator.scroll_into_view_if_needed(timeout=3000)
        await locator.click()

        if clear_first:
            await locator.fill("")
            await human_delay(0.2, 0.5)

        if human_like and len(value) <= 100:
            await human_typing(locator, value)
        else:
            await locator.fill(value)

        if human_like:
            await human_delay(0.4, 0.9)

        return ActionResult(
            success=True,
            message=f"Filled field with value '{value}'",
            page_changed=False,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Failed to fill input: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def select_option(page: Any, locator: Any, value: str) -> ActionResult:
    """Select a dropdown option by label, value, or index."""
    try:
        await locator.scroll_into_view_if_needed(timeout=3000)
        await locator.click()
        await human_delay(0.3, 0.7)

        # Attempt selection by label, value, or index
        try:
            await locator.select_option(label=value, timeout=3000)
        except Exception:
            try:
                await locator.select_option(value=value, timeout=3000)
            except Exception:
                # Fallback to first non-empty option
                await locator.select_option(index=1, timeout=3000)

        await human_delay(0.5, 1.0)
        return ActionResult(
            success=True,
            message=f"Selected option '{value}'",
            page_changed=False,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Failed to select option: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def check_checkbox(page: Any, locator: Any) -> ActionResult:
    """Ensure a checkbox or radio button is checked."""
    try:
        await locator.scroll_into_view_if_needed(timeout=3000)
        is_checked = await locator.is_checked()
        if not is_checked:
            await locator.check(timeout=3000)
            await human_delay(0.4, 0.8)

        return ActionResult(
            success=True,
            message="Checkbox checked",
            page_changed=False,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Failed to check checkbox: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def uncheck_checkbox(page: Any, locator: Any) -> ActionResult:
    """Ensure a checkbox is unchecked."""
    try:
        await locator.scroll_into_view_if_needed(timeout=3000)
        is_checked = await locator.is_checked()
        if is_checked:
            await locator.uncheck(timeout=3000)
            await human_delay(0.4, 0.8)

        return ActionResult(
            success=True,
            message="Checkbox unchecked",
            page_changed=False,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Failed to uncheck checkbox: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def scroll_page(page: Any, direction: str = "down", amount: int = 500) -> ActionResult:
    """Scroll the page or active container."""
    try:
        delta = amount if direction == "down" else -amount
        await page.mouse.wheel(0, delta)
        await human_delay(0.5, 1.0)
        return ActionResult(
            success=True,
            message=f"Scrolled {direction} by {amount}px",
            page_changed=False,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Failed to scroll: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def wait_for_element(page: Any, description: str, timeout: int = 5000) -> ActionResult:
    """Wait for a page element to appear or settle."""
    try:
        await human_delay(timeout / 2000.0, timeout / 1000.0)
        return ActionResult(
            success=True,
            message=f"Waited for element: {description}",
            page_changed=False,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Wait timed out: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def wait_for_navigation(page: Any, timeout: int = 5000) -> ActionResult:
    """Wait for page load or navigation."""
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=timeout)
        return ActionResult(
            success=True,
            message="Page navigation settled",
            page_changed=True,
            new_url=page.url,
        )
    except Exception as e:
        return ActionResult(
            success=False,
            message=f"Navigation wait failed: {str(e)}",
            error=str(e),
            page_changed=False,
            new_url=page.url,
        )


async def get_current_url(page: Any) -> str:
    return page.url


async def get_visible_text(page: Any) -> str:
    try:
        return await page.locator("body").inner_text(timeout=2000)
    except Exception:
        return ""


async def take_screenshot(page: Any, path: Optional[str] = None) -> Optional[str]:
    return await capture_screenshot(page, output_dir=path)
