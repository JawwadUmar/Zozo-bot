from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class PageType(str, Enum):
    JOB_DETAILS = "job_details"
    APPLICATION_FORM = "application_form"
    RESUME_PAGE = "resume_page"
    REVIEW_PAGE = "review_page"
    SUCCESS_PAGE = "success_page"
    WARNING_MODAL = "warning_modal"
    LOGIN_PAGE = "login_page"
    SEARCH_RESULTS = "search_results"
    DAILY_LIMIT = "daily_limit"
    UNKNOWN = "unknown"


class ActionType(str, Enum):
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    SCROLL = "scroll"
    WAIT = "wait"
    INSPECT = "inspect"
    COMPLETE = "complete"
    ASK_HUMAN = "ask_human"
    STOP = "stop"


class ElementInfo(BaseModel):
    tag: str = Field(description="HTML tag name (button, input, select, etc.)")
    role: Optional[str] = Field(default=None, description="Accessible ARIA role or deduced role")
    name: Optional[str] = Field(default=None, description="Accessible name or label")
    text: Optional[str] = Field(default=None, description="Visible inner text content")
    placeholder: Optional[str] = Field(default=None, description="Placeholder text for inputs")
    input_type: Optional[str] = Field(default=None, description="Input type (text, radio, checkbox, etc.)")
    is_visible: bool = Field(default=True, description="Whether the element is currently visible")
    is_enabled: bool = Field(default=True, description="Whether the element is enabled and not disabled")
    is_required: bool = Field(default=False, description="Whether the field is required")
    label: Optional[str] = Field(default=None, description="Associated label text from label tag or legend")
    value: Optional[str] = Field(default=None, description="Current value of the input or select")
    options: Optional[List[str]] = Field(default=None, description="Available options if this is a select or radio group")
    selector_hint: Optional[str] = Field(default=None, description="DOM attribute hint (id, data-test-*, name)")
    bounding_box: Optional[dict] = Field(default=None, description="Element bounding box {x, y, width, height}")


class PageObservation(BaseModel):
    url: str = Field(description="Current page URL")
    title: str = Field(description="Current page title")
    page_type: str = Field(default="unknown", description="Preliminary page type classification")
    interactive_elements: List[ElementInfo] = Field(default_factory=list, description="All visible interactive elements")
    visible_text: str = Field(default="", description="Cleaned visible text content of the page")
    form_fields: List[ElementInfo] = Field(default_factory=list, description="Extracted form fields (inputs, selects, textareas)")
    buttons: List[ElementInfo] = Field(default_factory=list, description="Extracted buttons and clickable actions")
    dialogs: List[dict] = Field(default_factory=list, description="Active dialogs or modal windows")
    progress_indicator: Optional[str] = Field(default=None, description="Application progress text (e.g., 'Step 2 of 4')")
    error_messages: List[str] = Field(default_factory=list, description="Visible validation error messages")
    has_modal: bool = Field(default=False, description="Whether a modal or dialog is currently open")


class PageUnderstanding(BaseModel):
    page_type: PageType = Field(description="Understood page or dialog type")
    description: str = Field(description="High-level description of what is displayed on the screen")
    available_actions: List[str] = Field(default_factory=list, description="List of valid logical actions candidate can take")
    current_step_description: str = Field(default="", description="Description of the current application step")
    can_proceed: bool = Field(default=True, description="Whether the automation can safely proceed")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score of this understanding")


class AgentAction(BaseModel):
    action_type: ActionType = Field(description="The type of action to perform")
    target_description: str = Field(description="Natural language description of the target element")
    target_role: Optional[str] = Field(default=None, description="Expected accessibility role (button, textbox, combobox, radio, checkbox)")
    target_name: Optional[str] = Field(default=None, description="Expected accessible name or visible text")
    value: Optional[str] = Field(default=None, description="Value to type or select if applicable")
    reason: str = Field(description="Detailed reason explaining why this action is chosen")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this action (0.0 to 1.0)")
    requires_confirmation: bool = Field(default=False, description="Whether human confirmation is requested before executing")


class ActionResult(BaseModel):
    success: bool = Field(description="Whether the action was executed successfully without error")
    message: str = Field(description="Description of what happened during execution")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    page_changed: bool = Field(default=False, description="Whether the page URL or title changed after execution")
    new_url: Optional[str] = Field(default=None, description="Page URL after action execution")


class VerificationResult(BaseModel):
    action_succeeded: bool = Field(description="Whether the previous action succeeded in moving the workflow forward")
    page_state_changed: bool = Field(description="Whether the visible page state changed meaningfully")
    expected_outcome_met: bool = Field(description="Whether the expected outcome occurred")
    details: str = Field(description="Explanation of the verification assessment")
    should_retry: bool = Field(default=False, description="Whether the action should be retried")
    should_inspect: bool = Field(default=False, description="Whether the page should be re-inspected first")
