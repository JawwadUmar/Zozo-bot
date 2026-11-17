from app.agent.state import ApplicationState


def evaluate_job(*, title: str, location: str, posting_time: str) -> bool:
    """Return whether a job should be selected.

    Keep filtering policy in this helper so keyword, location, and posting-age
    rules can be added without changing graph routing. Current behavior accepts
    every extracted job.
    """
    # Metadata is passed explicitly so future rules can inspect these values.
    _ = (title, location, posting_time)
    return True


async def should_apply_node(state: ApplicationState) -> dict[str, object]:
    jobs = state.get("current_page_jobs", [])
    index = state.get("current_card_index", 0)

    if index < 0 or index >= len(jobs):
        return {
            "current_job": {},
            "should_apply": False,
            "action_status": "job_list_exhausted",
        }

    job = dict(jobs[index])
    decision = evaluate_job(
        title=str(job.get("title", "")),
        location=str(job.get("location", "")),
        posting_time=str(job.get("posting_time", "")),
    )
    job["accepted"] = decision

    return {
        "current_job": job,
        "should_apply": decision,
        "action_status": "job_accepted" if decision else "job_skipped",
    }
