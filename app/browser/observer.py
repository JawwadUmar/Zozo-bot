from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from app.agent.models import ElementInfo, PageObservation


# Efficient single-turn JavaScript evaluation to extract all interactive elements and page metadata
EXTRACTION_JS = """
() => {
    const isVisible = (el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    };

    const cleanText = (str) => {
        if (!str) return '';
        return str.replace(/\\s+/g, ' ').trim();
    };

    // Find any active modal/dialog
    const dialogElements = Array.from(document.querySelectorAll('div[role="dialog"], .artdeco-modal, .jobs-easy-apply-modal, [aria-modal="true"]')).filter(isVisible);
    const hasModal = dialogElements.length > 0;
    const activeContainer = hasModal ? dialogElements[dialogElements.length - 1] : document.body;

    const dialogs = dialogElements.map(d => {
        const titleEl = d.querySelector('h1, h2, h3, [id*="header"], [id*="title"]');
        return {
            title: titleEl ? cleanText(titleEl.innerText) : '',
            id: d.id || '',
            role: d.getAttribute('role') || 'dialog'
        };
    });

    // Detect progress indicators
    let progressIndicator = null;
    const progressEl = activeContainer.querySelector('[role="progressbar"], [data-test-easy-apply-progress], .artdeco-completeness-meter');
    if (progressEl) {
        progressIndicator = cleanText(progressEl.getAttribute('aria-valuenow') || progressEl.getAttribute('aria-valuetext') || progressEl.innerText);
    }
    if (!progressIndicator) {
        // Fallback: look for "Step X of Y" or percentage text
        const stepMatch = activeContainer.innerText.match(/Step \\d+ of \\d+|\\d+% complete/i);
        if (stepMatch) {
            progressIndicator = stepMatch[0];
        }
    }

    // Detect validation errors
    const errorElements = Array.from(activeContainer.querySelectorAll(
        '.artdeco-inline-feedback--error, [aria-invalid="true"], [id*="error"]:not(:empty), .fb-dash-form-element__error-field'
    )).filter(isVisible);
    const errorMessages = Array.from(new Set(errorElements.map(e => cleanText(e.innerText)).filter(t => t.length > 0)));

    // Extract interactive elements from the active container
    const selector = 'button, input, select, textarea, a[role="button"], [role="button"], [role="checkbox"], [role="radio"], [role="combobox"], [role="listbox"], [role="menuitem"], [role="option"], [role="tab"]';
    const rawElements = Array.from(activeContainer.querySelectorAll(selector));

    const interactive = [];

    rawElements.forEach((el) => {
        if (!isVisible(el)) return;

        const tag = el.tagName.toLowerCase();
        const type = el.getAttribute('type') || (tag === 'textarea' ? 'textarea' : tag === 'select' ? 'select' : null);
        const role = el.getAttribute('role') || (tag === 'button' ? 'button' : tag === 'select' ? 'combobox' : type === 'checkbox' ? 'checkbox' : type === 'radio' ? 'radio' : null);
        
        // Find associated label
        let label = '';
        if (el.id) {
            const labelEl = document.querySelector(`label[for="${el.id}"]`);
            if (labelEl) label = cleanText(labelEl.innerText);
        }
        if (!label) {
            const parentLabel = el.closest('label');
            if (parentLabel) label = cleanText(parentLabel.innerText);
        }
        if (!label) {
            const fieldset = el.closest('fieldset');
            if (fieldset) {
                const legend = fieldset.querySelector('legend');
                if (legend) label = cleanText(legend.innerText);
            }
        }

        const ariaLabel = cleanText(el.getAttribute('aria-label') || '');
        const ariaDescribedBy = cleanText(el.getAttribute('aria-describedby') || '');
        const placeholder = cleanText(el.getAttribute('placeholder') || '');
        const innerText = cleanText(el.innerText || '');
        const nameAttr = el.getAttribute('name') || '';
        const idAttr = el.id || '';

        // Accessible name resolution
        const name = ariaLabel || label || innerText || placeholder || nameAttr;

        // Options for select elements
        let options = null;
        if (tag === 'select') {
            options = Array.from(el.querySelectorAll('option'))
                .map(o => cleanText(o.innerText || o.value))
                .filter(t => t.length > 0);
        }

        const rect = el.getBoundingClientRect();

        interactive.push({
            tag: tag,
            role: role,
            name: name ? name.substring(0, 150) : null,
            text: innerText ? innerText.substring(0, 150) : null,
            placeholder: placeholder || null,
            input_type: type,
            is_visible: true,
            is_enabled: !el.disabled && el.getAttribute('aria-disabled') !== 'true',
            is_required: el.required || el.getAttribute('aria-required') === 'true',
            label: label ? label.substring(0, 200) : null,
            value: el.value !== undefined ? String(el.value).substring(0, 100) : null,
            options: options,
            selector_hint: idAttr ? `#${idAttr}` : (el.getAttribute('data-test-modal-close-btn') ? '[data-test-modal-close-btn]' : (ariaLabel ? `[aria-label="${ariaLabel}"]` : nameAttr ? `[name="${nameAttr}"]` : null)),
            bounding_box: {
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height)
            }
        });
    });

    // Extract visible text summary (cleaned, max 4000 characters)
    let visibleText = cleanText(activeContainer.innerText || '');
    if (visibleText.length > 4000) {
        visibleText = visibleText.substring(0, 4000) + '... [truncated]';
    }

    return {
        hasModal: hasModal,
        dialogs: dialogs,
        progressIndicator: progressIndicator,
        errorMessages: errorMessages,
        interactiveElements: interactive,
        visibleText: visibleText
    };
}
"""


class PageObserver:
    """Extracts structured, token-efficient representations of the active browser page."""

    async def observe_page(self, page: Any) -> PageObservation:
        """Inspect the current page and return structured PageObservation."""
        url = page.url
        try:
            title = await page.title()
        except Exception:
            title = ""

        try:
            data = await page.evaluate(EXTRACTION_JS)
        except Exception as e:
            print(f"⚠️ PageObserver evaluation failed: {e}. Using fallback.")
            data = {
                "hasModal": False,
                "dialogs": [],
                "progressIndicator": None,
                "errorMessages": [],
                "interactiveElements": [],
                "visibleText": "",
            }

        interactive_elements = [
            ElementInfo(**el) for el in data.get("interactiveElements", [])
        ]

        # Separate form fields and buttons
        form_fields = [
            el for el in interactive_elements
            if el.tag in ("input", "select", "textarea") or el.role in ("textbox", "combobox", "checkbox", "radio", "listbox")
        ]

        buttons = [
            el for el in interactive_elements
            if el.tag == "button" or el.role in ("button", "menuitem", "tab") or el.input_type in ("button", "submit")
        ]

        return PageObservation(
            url=url,
            title=title,
            page_type="modal" if data.get("hasModal") else "page",
            interactive_elements=interactive_elements,
            visible_text=data.get("visibleText", ""),
            form_fields=form_fields,
            buttons=buttons,
            dialogs=data.get("dialogs", []),
            progress_indicator=data.get("progressIndicator"),
            error_messages=data.get("errorMessages", []),
            has_modal=data.get("hasModal", False),
        )
