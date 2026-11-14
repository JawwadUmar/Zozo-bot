"""
Locator utilities for Zozo-bot.

Provides ``get_first_available_locator`` — a single function that accepts
a Playwright Page and a *list* of selector strings (as defined in
``app.config.selectors``), waits for any of them to match, and returns a
ready-to-use Locator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.async_api import Locator, Page


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _make_locator(page: "Page | Locator", selector: str) -> "Locator":
    """Convert a single selector string into a Playwright Locator.

    Supported formats
    -----------------
    * **CSS / XPath / Playwright text pseudo-selectors**
      Anything ``page.locator()`` already understands, e.g.
      ``"button.submit:visible"``, ``"xpath=//div"``,
      ``"h3:has-text('Contact info')"``.

    * **``get_by_role:<role>:<name>``**
      Maps to ``page.get_by_role(role, name=name, exact=True)``.
      Example: ``"get_by_role:button:Sign in"``

    * **``get_by_label:<label>``**
      Maps to ``page.get_by_label(label, exact=True)``.
      Example: ``"get_by_label:Email or phone"``

    * **``get_by_text:<text>``**
      Maps to ``page.get_by_text(text, exact=True)``.
      Example: ``"get_by_text:Submit application"``

    * **``get_by_placeholder:<placeholder>``**
      Maps to ``page.get_by_placeholder(placeholder, exact=True)``.
      Example: ``"get_by_placeholder:Search jobs"``
    """
    # --- Semantic / role-based prefixes --------------------------------
    if selector.startswith("get_by_role:"):
        # Format:  get_by_role:<role>:<name>   (name is optional)
        parts = selector.split(":", 2)
        role = parts[1]
        name = parts[2] if len(parts) > 2 else None
        kwargs: dict = {"exact": True}
        if name:
            kwargs["name"] = name
        return page.get_by_role(role, **kwargs)

    if selector.startswith("get_by_label:"):
        label = selector.split(":", 1)[1]
        return page.get_by_label(label, exact=True)

    if selector.startswith("get_by_text:"):
        text = selector.split(":", 1)[1]
        return page.get_by_text(text, exact=True)

    if selector.startswith("get_by_placeholder:"):
        placeholder = selector.split(":", 1)[1]
        return page.get_by_placeholder(placeholder, exact=True)

    # --- Everything else (CSS, XPath, Playwright pseudo-selectors) -----
    return page.locator(selector)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_first_available_locator(
    page: "Page | Locator",
    selectors: list[str],
    *,
    timeout: int = 3000,
    state: str = "visible",
) -> "Locator | None":
    """Return a Locator for the first element that matches *any* selector.

    All selectors are combined with Playwright's ``.or_()`` operator so a
    **single** wait covers every candidate simultaneously — there is no
    serial per-selector penalty regardless of list length.

    Parameters
    ----------
    page : Page
        The active Playwright page to search within.
    selectors : list[str]
        One or more selector strings as stored in
        ``app.config.selectors``.  May mix CSS, XPath, and the
        ``get_by_*`` prefixed formats described in ``_make_locator``.
    timeout : int, optional
        Milliseconds to wait before giving up (default **3 000**).
    state : {"visible", "attached", "hidden", "detached"}, optional
        The element state to wait for (default **"visible"**).

    Returns
    -------
    Locator | None
        A Locator pointing to the first matched element, ready for
        ``.click()``, ``.fill()``, ``.inner_text()``, etc.
        Returns ``None`` when no selector matched within the timeout.

    Examples
    --------
    ::

        from app.config.selectors import SUBMIT_APPLICATION_BUTTON
        from app.utils.locator import get_first_available_locator

        submit = await get_first_available_locator(page, SUBMIT_APPLICATION_BUTTON)
        if submit:
            await submit.click()
        else:
            print("Submit button not found.")
    """
    if not selectors:
        return None

    # Build individual Locator objects.
    locators = [_make_locator(page, s) for s in selectors]

    # Combine them: Playwright's .or_() lets us wait for ANY match in one
    # shot instead of trying selectors one by one.
    combined = locators[0]
    for loc in locators[1:]:
        combined = combined.or_(loc)

    try:
        target = combined.first
        await target.wait_for(state=state, timeout=timeout)
        return target
    except Exception:
        return None
