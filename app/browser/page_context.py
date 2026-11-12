from __future__ import annotations

import asyncio
import hashlib
from typing import Any, Dict, Optional
from app.utils.human import human_delay


class PageContextManager:
    """Manages page stability, fingerprinting, and observation caching."""

    def __init__(self):
        self._cached_fingerprint: Optional[str] = None
        self._cached_observation: Optional[Dict[str, Any]] = None

    async def wait_for_page_stable(self, page: Any, timeout_ms: int = 3000) -> None:
        """Wait for page load, animations, and DOM to settle."""
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass

        # Brief settle delay
        await human_delay(0.5, 1.2)

    async def get_page_fingerprint(self, page: Any) -> str:
        """Compute a quick lightweight fingerprint of current URL, modal state, and input counts."""
        try:
            url = page.url
            title = await page.title()
            modal_count = await page.locator("div[role='dialog'], .artdeco-modal").count()
            input_count = await page.locator("input:visible, select:visible, button:visible").count()
            raw = f"{url}|{title}|modals:{modal_count}|inputs:{input_count}"
            return hashlib.md5(raw.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    async def detect_page_change(
        self,
        page: Any,
        previous_url: Optional[str],
        previous_title: Optional[str],
    ) -> bool:
        """Check if the current page has changed materially from previous state."""
        try:
            curr_url = page.url
            curr_title = await page.title()
            return curr_url != previous_url or curr_title != previous_title
        except Exception:
            return True

    def get_cached_observation(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        if self._cached_fingerprint == fingerprint and self._cached_observation is not None:
            return self._cached_observation
        return None

    def set_cached_observation(self, fingerprint: str, observation: Dict[str, Any]) -> None:
        self._cached_fingerprint = fingerprint
        self._cached_observation = observation

    def clear_cache(self) -> None:
        self._cached_fingerprint = None
        self._cached_observation = None
