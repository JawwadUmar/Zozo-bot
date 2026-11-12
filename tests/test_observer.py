from __future__ import annotations

import pytest
from unittest.mock import AsyncMock
from app.browser.observer import PageObserver


@pytest.mark.asyncio
async def test_observe_page_structure(mock_page):
    observer = PageObserver()

    # Mock evaluate response
    mock_page.evaluate.return_value = {
        "hasModal": True,
        "dialogs": [{"title": "Apply to Software Engineer", "role": "dialog"}],
        "progressIndicator": "Step 2 of 4",
        "errorMessages": [],
        "interactiveElements": [
            {
                "tag": "button",
                "role": "button",
                "name": "Next",
                "text": "Next",
                "is_visible": True,
                "is_enabled": True,
                "is_required": False,
            },
            {
                "tag": "input",
                "role": "textbox",
                "name": "Phone",
                "input_type": "text",
                "label": "Phone",
                "value": "1234567890",
                "is_visible": True,
                "is_enabled": True,
                "is_required": True,
            },
        ],
        "visibleText": "Apply to Software Engineer Step 2 of 4",
    }

    obs = await observer.observe_page(mock_page)

    assert obs.has_modal is True
    assert len(obs.dialogs) == 1
    assert obs.dialogs[0]["title"] == "Apply to Software Engineer"
    assert obs.progress_indicator == "Step 2 of 4"
    assert len(obs.interactive_elements) == 2
    assert len(obs.buttons) == 1
    assert obs.buttons[0].name == "Next"
    assert len(obs.form_fields) == 1
    assert obs.form_fields[0].name == "Phone"


@pytest.mark.asyncio
async def test_observe_detects_validation_errors(mock_page):
    observer = PageObserver()

    mock_page.evaluate.return_value = {
        "hasModal": True,
        "dialogs": [{"title": "Apply", "role": "dialog"}],
        "progressIndicator": "Step 1 of 3",
        "errorMessages": ["Please enter a valid phone number", "This field is required"],
        "interactiveElements": [],
        "visibleText": "Errors present",
    }

    obs = await observer.observe_page(mock_page)
    assert len(obs.error_messages) == 2
    assert "Please enter a valid phone number" in obs.error_messages


@pytest.mark.asyncio
async def test_observe_handles_dropdown_and_radio_elements(mock_page):
    observer = PageObserver()

    mock_page.evaluate.return_value = {
        "hasModal": True,
        "dialogs": [{"title": "Additional Questions", "role": "dialog"}],
        "progressIndicator": "Step 3 of 4",
        "errorMessages": [],
        "interactiveElements": [
            {
                "tag": "select",
                "role": "combobox",
                "name": "Notice Period",
                "label": "Notice Period",
                "input_type": "select",
                "options": ["Immediate", "15 days", "30 days"],
                "is_visible": True,
                "is_enabled": True,
            },
            {
                "tag": "input",
                "role": "radio",
                "name": "Authorized to work",
                "label": "Yes",
                "input_type": "radio",
                "value": "Yes",
                "is_visible": True,
                "is_enabled": True,
            },
            {
                "tag": "input",
                "role": "checkbox",
                "name": "Follow company",
                "label": "Follow company",
                "input_type": "checkbox",
                "value": "true",
                "is_visible": True,
                "is_enabled": True,
            },
        ],
        "visibleText": "Additional Questions",
    }

    obs = await observer.observe_page(mock_page)
    assert len(obs.form_fields) == 3

    select_field = next(f for f in obs.form_fields if f.tag == "select")
    assert select_field.options == ["Immediate", "15 days", "30 days"]

    radio_field = next(f for f in obs.form_fields if f.input_type == "radio")
    assert radio_field.role == "radio"
    assert radio_field.value == "Yes"

    checkbox_field = next(f for f in obs.form_fields if f.input_type == "checkbox")
    assert checkbox_field.role == "checkbox"


@pytest.mark.asyncio
async def test_observe_identifies_easy_apply_with_arbitrary_css(mock_page):
    """Verify Easy Apply button is captured cleanly regardless of dynamic CSS classes."""
    observer = PageObserver()

    mock_page.evaluate.return_value = {
        "hasModal": False,
        "dialogs": [],
        "progressIndicator": None,
        "errorMessages": [],
        "interactiveElements": [
            {
                "tag": "button",
                "role": "button",
                "name": "Easy Apply to Senior Software Engineer",
                "text": "Easy Apply",
                "is_visible": True,
                "is_enabled": True,
                "selector_hint": '[aria-label="Easy Apply to Senior Software Engineer"]',
            }
        ],
        "visibleText": "Senior Software Engineer at Anthropic. Easy Apply available.",
    }

    obs = await observer.observe_page(mock_page)
    assert len(obs.buttons) == 1
    assert "Easy Apply" in obs.buttons[0].name


@pytest.mark.asyncio
async def test_observe_handles_evaluation_failure(mock_page):
    observer = PageObserver()
    mock_page.evaluate.side_effect = Exception("DOM crashed")

    obs = await observer.observe_page(mock_page)
    assert obs.interactive_elements == []
    assert obs.has_modal is False
    assert obs.error_messages == []
