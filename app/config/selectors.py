"""
Centralized Playwright Selectors for Zozo-bot
==============================================
Every selector extracted from the codebase, grouped by UI element/action.
Each variable is a list of selector strings, even when there is currently only one.

Usage:
    from app.config.selectors import EASY_APPLY_BUTTON
    from app.utils.locator import get_first_available_locator

    locator = await get_first_available_locator(page, EASY_APPLY_BUTTON)
"""

# ==============================================================================
# LOGIN PAGE  (source: app/bot/handle_login.py → handleLogin)
# ==============================================================================

# get_by_label("Email or phone", exact=True).locator("visible=true")
LOGIN_EMAIL_INPUT = ["get_by_label:Email or phone"]

# get_by_label("Password", exact=True).locator("visible=true")
LOGIN_PASSWORD_INPUT = ["get_by_label:Password"]

# get_by_role("button", name="Sign in", exact=True).locator("visible=true")
LOGIN_SUBMIT_BUTTON = ["get_by_role:button:Sign in"]

# page.wait_for_url pattern used after login
LOGIN_SUCCESS_URL_PATTERN = ["**/feed/**"]

# ==============================================================================
# JOB SEARCH RESULTS PAGE  (source: app/bot/bot_runner.py → run_bot)
# ==============================================================================

# CSS selector for job cards in search results list
# Used in: wait_for_selector and page.locator calls in run_bot
JOB_CARD_CONTAINER = [".job-card-container"]

# Text selector to detect "Already Applied" status on a job card
# Used in: run_bot — card.locator(...)
JOB_CARD_APPLIED_INDICATOR = ["li:has-text('Applied')"]

# ==============================================================================
# SUCCESS / DISMISS MODAL  (source: app/bot/bot_runner.py → close_success_modal, run_bot)
# ==============================================================================

# Dismiss button on the post-application success modal
# Used in both close_success_modal() and the inline block inside run_bot()
DISMISS_MODAL_BUTTON = [
    "button[data-test-modal-close-btn]:visible",
    "button[aria-label='Dismiss']:visible",
    "button.artdeco-modal__dismiss:visible",
    "button:has(svg[data-test-icon='close-medium']):visible",
]

# ==============================================================================
# EASY APPLY BUTTON  (source: app/bot/click_easy_apply.py → clickEasyApply)
# ==============================================================================

# The main "Easy Apply" button on the job detail pane
EASY_APPLY_BUTTON = [
    "button[aria-label*='Easy Apply']:visible",
    ".jobs-apply-button:visible",
]

# "Continue applying" modal button (role-based selector)
# Used via: page.get_by_role("button", name="Continue applying").locator("visible=true")
CONTINUE_APPLYING_BUTTON = ["get_by_role:button:Continue applying"]

# ==============================================================================
# FORM NAVIGATION BUTTONS  (source: app/bot/click_buttons.py)
# ==============================================================================

# "Continue to next step" / Next button
# Used in: clickNextOrReviewButton, clickNextButton, and fill_form.py fallback
NEXT_STEP_BUTTON = ["footer button:has-text('Next'):visible", "button[aria-label='Continue to next step']:visible"]

# "Review your application" button
# Used in: clickNextOrReviewButton, clickReviewButton, and fill_form.py fallback
REVIEW_APPLICATION_BUTTON = ["footer button:has-text('Review'):visible", "button[aria-label='Review your application']:visible"]

# Combined Next-or-Review selector (comma-separated in the original)
# Used in: clickNextOrReviewButton, fillForm fallback
NEXT_OR_REVIEW_BUTTON = NEXT_STEP_BUTTON + REVIEW_APPLICATION_BUTTON

# "Submit application" button
# Used in: clickSubmitButton, fillForm step-1 check
SUBMIT_APPLICATION_BUTTON = ["footer button:has-text('Submit application'):visible", "button[aria-label='Submit application']:visible"]

# "Follow company" checkbox and its label
# Used in: clickSubmitButton
FOLLOW_COMPANY_CHECKBOX = ["input#follow-company-checkbox"]
FOLLOW_COMPANY_LABEL = ["label[for='follow-company-checkbox']"]

# ==============================================================================
# DAILY SUBMISSION LIMIT  (source: app/bot/daily_limit.py)
# ==============================================================================

# The body element used to extract all visible text for limit detection
DAILY_LIMIT_BODY = ["body"]

# ==============================================================================
# FORM SECTIONS & FIELDS  (source: app/bot/fill_form.py)
# ==============================================================================

# --- Section Headers ---

# "Contact info" section header
# Used in: fillForm step-2 check, handleContactInfo
CONTACT_INFO_HEADER = ["p:text-is('Contact info'):visible","h3:has-text('Contact info'):visible", "h3:has-text('Contact info')"]

# "Be sure to include an updated resume" indicator
# Used in: fillForm step-3 check, handleResumePage
RESUME_SECTION_TEXT = [
    "p:text-is('Resume*'):visible",
    "span:has-text('Be sure to include an updated resume'):visible",
    "span:has-text('Be sure to include an updated resume')",
]

# "Additional Questions" section header
# Used in: fillForm step-4 check, handleAdditionalQuestions
ADDITIONAL_QUESTIONS_HEADER = ["p:text-is('Additional Questions'):visible","h3:has-text('Additional Questions'):visible", "h3:has-text('Additional Questions')"]

# "Work authorization" section header
# Used in: fillForm step-5 check, handleWorkAuthorization
WORK_AUTHORIZATION_HEADER = ["p:text-is('Work authorization'):visible","h3:has-text('Work authorization'):visible", "h3:has-text('Work authorization')"]

# "Work experience" section header
# Used in: fillForm step-6 check, handleWorkExperience
WORK_EXPERIENCE_HEADER = ["p:text-is('Work experience'):visible","h3:has-text('Work experience'):visible", "h3:has-text('Work experience')"]

# --- Form Input Fields ---

# Phone number input (ID ends with "-phoneNumber-nationalNumber")
# Used in: fillForm step-2.1 check, handleContactInfo, fillPhoneNumber
PHONE_NUMBER_INPUT = [
    'input[id$="-phoneNumber-nationalNumber"]:visible',
    'input[id$="-phoneNumber-nationalNumber"]',
]

# Location / Geo input
# Used in: handleContactInfo
LOCATION_INPUT = ['input[id$="-location-GEO-LOCATION"]:visible']

# Generic text inputs for Additional Questions / Work Experience
# Used in: handleAdditionalQuestions, handleWorkExperience
TEXT_INPUT_ARTDECO = ["input.artdeco-text-input--input[type='text']"]

# Select dropdowns for Additional Questions / Work Experience
# Used in: handleAdditionalQuestions, handleWorkExperience
SELECT_DROPDOWN = ["select.fb-dash-form-element__select-dropdown"]

# Dropdown <option> child elements
# Used in: handleAdditionalQuestions, handleWorkExperience
SELECT_OPTION = ["option"]

# Labels associated with dynamically identified form fields.
FORM_FIELD_LABEL = ["label[for='{id}']"]

# --- Radio Button Fieldsets ---

# Radio-button fieldset container
# Used in: handleWorkAuthorization, handleAdditionalQuestions, handleWorkExperience
RADIO_BUTTON_FIELDSET = ["fieldset[data-test-form-builder-radio-button-form-component='true']"]

# Title/question inside a radio-button fieldset
# Used in: handleWorkAuthorization, handleAdditionalQuestions, handleWorkExperience
RADIO_BUTTON_TITLE = ["span[data-test-form-builder-radio-button-form-component__title]"]

# Individual radio-button option labels
# Used in: handleWorkAuthorization, handleAdditionalQuestions, handleWorkExperience
RADIO_BUTTON_OPTION_LABEL = ["label[data-test-text-selectable-option__label]"]

# "Yes" option label inside a radio fieldset
# Used in: handleWorkAuthorization
RADIO_YES_OPTION = ["label:has-text('Yes')"]

# ==============================================================================
# JOB DETAIL — TITLE & COMPANY  (source: app/bot/connect_hiring_team.py → _get_current_job_context)
# ==============================================================================

# Job title selectors on the job detail top card
JOB_TITLE = [
    ".job-details-jobs-unified-top-card__job-title",
    ".jobs-unified-top-card__job-title",
    "h1:visible",
]

# Company name selectors on the job detail top card
COMPANY_NAME = [
    ".job-details-jobs-unified-top-card__company-name a",
    ".job-details-jobs-unified-top-card__company-name",
    ".jobs-unified-top-card__company-name a",
    ".jobs-unified-top-card__company-name",
]

# ==============================================================================
# HIRING TEAM SECTION  (source: app/bot/connect_hiring_team.py)
# ==============================================================================

# Markers used to locate the "Meet the hiring team" section
# Used in: module-level HIRING_TEAM_MARKER, _scroll_to_hiring_team, _get_hiring_team_section
HIRING_TEAM_MARKER = [
    "h2:has-text('hiring team')",
    "h3:has-text('hiring team')",
    "p:has-text('Meet the hiring team')",
    ".hirer-card__hirer-information",
]

# Profile top card scope used as a prefix for many profile-page selectors
# Used in: module-level PROFILE_TOP_CARD constant
PROFILE_TOP_CARD = ["main section:has(h1)"]

# Job detail panes to scroll through when searching for hiring team
# Used in: _scroll_to_hiring_team
JOB_DETAILS_PANE = [
    ".jobs-search__job-details--container:visible",
    ".jobs-search__right-rail:visible",
    ".jobs-details__main-content:visible",
    ".scaffold-layout__detail:visible",
]

# XPath ancestor selector used to find the hiring team section container
# Used in: _get_hiring_team_section (marker.locator("xpath=..."))
HIRING_TEAM_SECTION_XPATH = [
    "xpath=ancestor-or-self::*[(self::section or self::div) and .//a[contains(@href, '/in/')]][1]"
]

# Fallback CSS selectors for the hiring team section
# Used in: _get_hiring_team_section
HIRING_TEAM_SECTION_FALLBACK = [
    "div:has(> p:has-text('Meet the hiring team')):has(a[href*='/in/'])",
    "section:has-text('hiring team'):has(a[href*='/in/'])",
    "div:has(> h2:has-text('hiring team')):has(a[href*='/in/'])",
    "div:has(> h3:has-text('hiring team')):has(a[href*='/in/'])",
]

# Profile links inside the hiring team section
# Used in: _get_hiring_team_members
HIRING_TEAM_PROFILE_LINK = ["a[href*='/in/']"]

# ==============================================================================
# PROFILE PAGE — CONNECTION STATUS  (source: app/bot/connect_hiring_team.py)
# ==============================================================================

# "Pending" connection request indicators (scoped under PROFILE_TOP_CARD)
# Used in: _has_connection_pending
CONNECTION_PENDING = [
    "main section:has(h1) button:has-text('Pending'):visible",
    "main section:has(h1) span:has-text('Pending'):visible",
    "main section:has(h1) button[aria-label*='Pending' i]:visible",
]

# "Already connected" (1st degree) badge (scoped under PROFILE_TOP_CARD)
# Used in: _is_already_connected
ALREADY_CONNECTED = [
    "main section:has(h1) span:has-text('1st'):visible",
    "main section:has(h1) span:has-text('1st degree connection'):visible",
]

# ==============================================================================
# PROFILE PAGE — CONNECT FLOW  (source: app/bot/connect_hiring_team.py → _click_connect)
# ==============================================================================

# Direct "Connect" button variants (scoped under PROFILE_TOP_CARD)
# Used in: _click_connect
DIRECT_CONNECT_BUTTON = [
    "main section:has(h1) button[aria-label*='Invite' i][aria-label*='connect' i]:visible",
    "main section:has(h1) button:has-text('Connect'):visible",
    "main section:has(h1) [role='button'][aria-label*='Connect' i]:visible",
    "main section:has(h1) [role='button']:has-text('Connect'):visible",
    "main section:has(h1) a[href*='custom-invite']:visible",
    "main section:has(h1) a:has-text('Connect'):visible",
    "main section:has(h1) a[aria-label*='connect' i]:visible",
]

# "More actions" dropdown button (scoped under PROFILE_TOP_CARD)
# Used in: _click_connect
MORE_ACTIONS_BUTTON = [
    "main section:has(h1) button[aria-label*='More actions' i]:visible",
    "main section:has(h1) button[aria-label='More']:visible",
    "main section:has(h1) button:has-text('More'):visible",
    "main section:has(h1) [role='button'][aria-label*='More actions' i]:visible",
    "main section:has(h1) [role='button'][aria-label='More']:visible",
    "main section:has(h1) [role='button']:has-text('More'):visible",
]

# "Connect" inside the More dropdown menu
# Used in: _click_connect (after opening More menu)
MENU_CONNECT_BUTTON = [
    "[role='menuitem']:has-text('Connect'):visible",
    "[role='menu'] a[href*='custom-invite']:visible",
    "a[role='menuitem'][href*='custom-invite']:visible",
    "div[aria-label*='Invite' i][aria-label*='connect' i]:visible",
    "div[role='button']:has-text('Connect'):visible",
]

# ==============================================================================
# PROFILE PAGE — SEND INVITATION  (source: app/bot/connect_hiring_team.py → _send_connection_invite)
# ==============================================================================

# "Add a note" button on the connection invite modal
# Used in: _send_connection_invite
ADD_NOTE_BUTTON = [
    "button:has-text('Add a note'):visible",
    "button:has-text('Add note'):visible",
    "button[aria-label*='Add a note' i]:visible",
]

# Textarea for the custom connection message
# Used in: _send_connection_invite
CONNECTION_NOTE_TEXTAREA = [
    "textarea#custom-message:visible",
    ".send-invite textarea:visible",
    "div.artdeco-modal textarea:visible",
]

# "Send invitation" / "Send now" / "Send without a note" buttons
# Used in: _send_connection_invite
SEND_INVITATION_BUTTON = [
    "button:text-is('Send invitation'):visible",
    "button:text-is('Send now'):visible",
    "button:text-is('Send without a note'):visible",
    "button:text-is('Send without note'):visible",
    "button[aria-label='Send now']:visible",
    "button[aria-label*='Send invitation' i]:visible",
    "div.artdeco-modal button:has-text('Send'):visible",
    ".send-invite button:has-text('Send'):visible",
]

# ==============================================================================
# JAVASCRIPT-EVALUATED SELECTORS  (source: app/bot/connect_hiring_team.py)
# ==============================================================================

# CSS selectors used inside page.evaluate() JavaScript in _js_click_profile_action
# These run in the browser via document.querySelector / querySelectorAll
JS_PROFILE_ACTION_SCOPE = ["main h1"]
JS_PROFILE_ACTION_CANDIDATES = ["button", "[role=\"button\"]", "a"]
JS_MAIN_FALLBACK = ["main"]
JS_LIST_EXCLUSION = ["ul", "li"]
JS_CONNECT_MENU_CANDIDATES = ["[role=\"menuitem\"]", "div[role=\"button\"]"]
JS_MORE_GLOBAL_CANDIDATES = ["main button", "main [role=\"button\"]"]
JS_SIDEBAR_EXCLUSION = ["aside", ".right-rail", ".scaffold-layout__aside"]

# CSS selectors used inside page.evaluate() JavaScript in _send_connection_invite fallback
# Filters out messaging overlay elements
JS_SEND_INVITE_CANDIDATES = ["button", "[role=\"button\"]"]
JS_SEND_INVITE_EXCLUSION = [".msg-overlay-conversation-bubble", "aside[class*=\"msg-\"]"]
