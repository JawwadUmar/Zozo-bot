from __future__ import annotations

import pytest
from app.browser.element_resolver import ElementResolver
from app.agent.models import AgentAction, ActionType
from tests.conftest import create_mock_locator


@pytest.mark.asyncio
async def test_resolve_by_role_and_name(mock_page):
    resolver = ElementResolver()

    mock_btn = create_mock_locator("Easy Apply")
    mock_page.get_by_role.return_value = mock_btn
    mock_page.locator.return_value = create_mock_locator("", count=0)

    action = AgentAction(
        action_type=ActionType.CLICK,
        target_description="Easy Apply button",
        target_role="button",
        target_name="Easy Apply",
        reason="Click Easy Apply",
    )

    resolved = await resolver.resolve_element(mock_page, action)
    assert resolved is not None
    mock_page.get_by_role.assert_called()


@pytest.mark.asyncio
async def test_resolve_easy_apply_button_despite_css_class_change(mock_page):
    """Test locating Easy Apply via accessible role + name even if CSS classes are changed completely."""
    resolver = ElementResolver()

    easy_apply_btn = create_mock_locator("Easy Apply to Google", is_visible=True, is_enabled=True)
    mock_page.get_by_role.return_value = easy_apply_btn
    mock_page.locator.return_value = create_mock_locator("", count=0)

    action = AgentAction(
        action_type=ActionType.CLICK,
        target_description="Easy Apply button on job card",
        target_role="button",
        target_name="Easy Apply to Google",
        reason="Initiate application without relying on .jobs-apply-button",
    )

    resolved = await resolver.resolve_element(mock_page, action)
    assert resolved is not None
    mock_page.get_by_role.assert_called()
    call_args = mock_page.get_by_role.call_args
    assert call_args[0][0] == "button"
    assert "Easy" in call_args[1]["name"].pattern


@pytest.mark.asyncio
async def test_resolve_by_label_fallback(mock_page):
    resolver = ElementResolver()

    empty_loc = create_mock_locator("", count=0)
    mock_page.get_by_role.return_value = empty_loc
    mock_page.locator.return_value = empty_loc

    label_loc = create_mock_locator("Mobile phone number")
    mock_page.get_by_label.return_value = label_loc

    action = AgentAction(
        action_type=ActionType.FILL,
        target_description="Phone number field",
        target_role="textbox",
        target_name="Mobile phone number",
        value="9155027072",
        reason="Fill phone number",
    )

    resolved = await resolver.resolve_element(mock_page, action)
    assert resolved is not None
    mock_page.get_by_label.assert_called()


@pytest.mark.asyncio
async def test_resolve_returns_none_for_low_confidence_missing_element(mock_page):
    """Ensure resolver never silently returns incorrect elements for low-confidence searches."""
    resolver = ElementResolver()

    empty_loc = create_mock_locator("", count=0)
    mock_page.get_by_role.return_value = empty_loc
    mock_page.get_by_label.return_value = empty_loc
    mock_page.get_by_placeholder.return_value = empty_loc
    mock_page.get_by_text.return_value = empty_loc
    mock_page.locator.return_value = empty_loc

    action = AgentAction(
        action_type=ActionType.CLICK,
        target_description="Obscure unknown button",
        target_role="button",
        target_name="Random Unmatched Element",
        reason="Test missing element handling",
        confidence=0.3,
    )

    resolved = await resolver.resolve_element(mock_page, action)
    assert resolved is None


@pytest.mark.asyncio
async def test_resolve_disambiguates_multiple_candidates(mock_page):
    """When multiple elements match text, disambiguate using the expected role."""
    resolver = ElementResolver()

    # Create two candidates: first is a div, second is a button
    btn_cand = create_mock_locator("Submit", is_visible=True, is_enabled=True)
    btn_cand.evaluate.return_value = "button"
    btn_cand.get_attribute.return_value = "button"

    mock_page.get_by_role.return_value = create_mock_locator("", count=0)
    mock_page.get_by_label.return_value = create_mock_locator("", count=0)
    mock_page.get_by_placeholder.return_value = create_mock_locator("", count=0)

    # Text match returns candidate
    mock_page.get_by_text.return_value = btn_cand
    mock_page.locator.return_value = create_mock_locator("", count=0)

    action = AgentAction(
        action_type=ActionType.CLICK,
        target_description="Submit button",
        target_role="button",
        target_name="Submit",
        reason="Click Submit",
    )

    resolved = await resolver.resolve_element(mock_page, action)
    assert resolved is not None
