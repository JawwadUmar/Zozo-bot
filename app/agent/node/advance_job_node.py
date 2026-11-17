from app.agent.state import ApplicationState


async def advance_job_node(state: ApplicationState) -> dict[str, object]:
    """Record the decision for the current card and advance its page index."""
    job = dict(state.get("current_job", {}))
    processed_jobs = list(state.get("processed_jobs", []))

    if job:
        job.setdefault("accepted", bool(state.get("should_apply", False)))
        job.setdefault("selected", False)
        processed_jobs.append(job)

    return {
        "processed_jobs": processed_jobs,
        "current_card_index": state.get("current_card_index", 0) + 1,
        "current_job": {},
        "should_apply": False,
        "action_status": "job_advanced",
    }
