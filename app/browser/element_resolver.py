from __future__ import annotations

import re
from typing import Any, List, Optional
from app.agent.models import AgentAction


class ElementResolver:
    """Robust, multi-strategy Playwright element locator without brittle hardcoded CSS selectors."""

    async def resolve_element(self, page: Any, action: AgentAction) -> Optional[Any]:
        """Locate element on the page following strict priority order and safety validations."""
        # 1. Scope to active modal if open to prevent clicking background elements
        active_scope = page
        try:
            modal = page.locator("div[role='dialog']:visible, .artdeco-modal:visible").last
            if await modal.count() > 0:
                active_scope = modal
        except Exception:
            pass

        target_name = (action.target_name or "").strip()
        target_role = (action.target_role or "").strip().lower()
        target_desc = (action.target_description or "").strip()

        # Strategy 1: Accessible role + Accessible name
        if target_role and target_name:
            locator = active_scope.get_by_role(target_role, name=re.compile(re.escape(target_name), re.IGNORECASE))
            resolved = await self._validate_and_disambiguate(locator, action)
            if resolved:
                return resolved

        # Strategy 2: By associated label text
        if target_name:
            locator = active_scope.get_by_label(re.compile(re.escape(target_name), re.IGNORECASE))
            resolved = await self._validate_and_disambiguate(locator, action)
            if resolved:
                return resolved

        # Strategy 3: By placeholder text
        if target_name:
            locator = active_scope.get_by_placeholder(re.compile(re.escape(target_name), re.IGNORECASE))
            resolved = await self._validate_and_disambiguate(locator, action)
            if resolved:
                return resolved

        # Strategy 4: Stable semantic attributes (aria-label, data-test-*)
        if target_name:
            attr_locators = [
                active_scope.locator(f"[aria-label*='{target_name}' i]"),
                active_scope.locator(f"[name*='{target_name}' i]"),
                active_scope.locator(f"[title*='{target_name}' i]"),
            ]
            for loc in attr_locators:
                resolved = await self._validate_and_disambiguate(loc, action)
                if resolved:
                    return resolved

        # Strategy 5: Visible text match
        if target_name:
            locator = active_scope.get_by_text(re.compile(re.escape(target_name), re.IGNORECASE))
            resolved = await self._validate_and_disambiguate(locator, action)
            if resolved:
                return resolved

        # Strategy 6: Target description matching
        if target_desc and target_desc != target_name:
            # Try role with description
            if target_role:
                locator = active_scope.get_by_role(target_role, name=re.compile(re.escape(target_desc), re.IGNORECASE))
                resolved = await self._validate_and_disambiguate(locator, action)
                if resolved:
                    return resolved

            # Try text with description
            locator = active_scope.get_by_text(re.compile(re.escape(target_desc), re.IGNORECASE))
            resolved = await self._validate_and_disambiguate(locator, action)
            if resolved:
                return resolved

        # Strategy 7: Fallback to global page scope if modal scope was too restrictive
        if active_scope != page:
            if target_role and target_name:
                locator = page.get_by_role(target_role, name=re.compile(re.escape(target_name), re.IGNORECASE))
                resolved = await self._validate_and_disambiguate(locator, action)
                if resolved:
                    return resolved

            if target_name:
                locator = page.get_by_text(re.compile(re.escape(target_name), re.IGNORECASE))
                resolved = await self._validate_and_disambiguate(locator, action)
                if resolved:
                    return resolved

        print(f"⚠️ ElementResolver: Could not confidently resolve element '{target_name}' ({target_role})")
        return None

    async def _validate_and_disambiguate(self, locator: Any, action: AgentAction) -> Optional[Any]:
        """Verify element exists, is visible and enabled, and safely disambiguate duplicates."""
        try:
            count = await locator.count()
            if count == 0:
                return None

            visible_locators = []
            for i in range(count):
                candidate = locator.nth(i)
                if await candidate.is_visible():
                    visible_locators.append(candidate)

            if not visible_locators:
                return None

            if len(visible_locators) == 1:
                target = visible_locators[0]
                if await target.is_enabled():
                    return target
                return target  # Even if disabled, return for inspection

            # Disambiguate multiple matches
            return await self._disambiguate(visible_locators, action)
        except Exception as e:
            return None

    async def _disambiguate(self, candidates: List[Any], action: AgentAction) -> Optional[Any]:
        """Disambiguate among multiple visible candidates based on role and context."""
        expected_role = (action.target_role or "").lower()

        for cand in candidates:
            try:
                # Check tag name and role
                tag_name = await cand.evaluate("el => el.tagName.toLowerCase()")
                role = await cand.get_attribute("role") or ""

                if expected_role:
                    if expected_role == "button" and (tag_name == "button" or role == "button"):
                        return cand
                    if expected_role in ("textbox", "input") and tag_name in ("input", "textarea"):
                        return cand
                    if expected_role in ("combobox", "select") and tag_name == "select":
                        return cand
                    if expected_role == "checkbox" and (await cand.get_attribute("type") == "checkbox" or role == "checkbox"):
                        return cand
                    if expected_role == "radio" and (await cand.get_attribute("type") == "radio" or role == "radio"):
                        return cand
            except Exception:
                continue

        # If none specifically matched role, return the first visible enabled one
        for cand in candidates:
            try:
                if await cand.is_enabled():
                    return cand
            except Exception:
                continue

        return candidates[0] if candidates else None
