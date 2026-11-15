from typing import TypedDict, Optional, Any

class ApplicationState(TypedDict):
    # Browser reference
    session_id: str

    # Application data
    user_profile: dict
    resume_path: str

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