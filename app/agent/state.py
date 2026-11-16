from typing import TypedDict, Optional, Any

class ApplicationState(TypedDict):
    # Browser reference
    session_id: str

    # Pagination & Page State
    job_link: str
    start: int
    is_search_page: bool
    total_cards_on_page: int
    current_card_index: int

    # Current Job Context
    current_job_title: Optional[str]
    current_company: Optional[str]
    applied_count: int

    # Control Flags
    daily_limit_reached: bool

    # Application data
    user_profile: dict
    resume_path: str
    is_logged_in: bool
    search_query: str
    jobs: list
    current_job: dict

    # Form data
    current_form_step: Optional[str]
    form_fields: list
    application_answers: dict

    # Recovery
    recovery_request: Optional[dict]
    recovery_result: Optional[dict]

    # Execution tracking
    action_status: str
    application_status: str
    error: Optional[str]
