from __future__ import annotations

import asyncio
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from playwright.async_api import async_playwright, BrowserContext, Page

from app.config.config import (
    AUTO_CONNECT_HIRING_TEAM,
    JOBLINK,
    USER_DATA_DIRECTORY,
    MAX_ACTIONS_PER_APPLICATION,
    MAX_RETRIES,
    validate_credentials,
)
from app.bot.handle_login import handleLogin
from app.utils.human import human_delay
from app.agent.graph import run_easy_apply
from app.profile.profile_loader import load_candidate_profile
from app.linkedin.daily_limit import (
    DailySubmissionLimitReached,
    stop_if_daily_submission_limit_visible,
)
from app.config.excluded_job import isExcludedJob
from app.bot.connect_hiring_team import connect_to_hiring_team, _get_current_job_context
from app.linkedin.application_state import ApplicationTracker
from app.utils.logging import logger


async def close_success_modal(page: Page) -> None:
    """Close the Easy Apply success confirmation modal."""
    print("🤖 Zozo: Closing success modal...")
    try:
        dismiss_btn = page.locator(
            "button[data-test-modal-close-btn]:visible, "
            "button[aria-label='Dismiss']:visible, "
            "button.artdeco-modal__dismiss:visible, "
            "button:has(svg[data-test-icon='close-medium']):visible, "
            "button:has-text('Done'):visible"
        ).first
        await dismiss_btn.wait_for(state="visible", timeout=5000)
        await dismiss_btn.click(force=True)
        await human_delay(1, 2)
    except Exception as e:
        print(f"⚠️ Zozo: Dismiss button not found or could not be clicked. ({e})")


async def connect_after_application(page: Page) -> None:
    """Connect to hiring team members if enabled in configuration."""
    if not AUTO_CONNECT_HIRING_TEAM:
        print("🤖 Zozo: Hiring-team connection requests are disabled.")
        return

    try:
        await connect_to_hiring_team(page)
    except Exception as e:
        print(f"⚠️ Zozo: Hiring team connection error: {e}")


async def stop_for_daily_limit(context: BrowserContext, error: Exception) -> None:
    """Handle daily submission limit by stopping bot gracefully."""
    print(f"\n🚨 Zozo: {error}")
    print("🛑 Zozo: Stopping the run now. Please apply again tomorrow.")
    try:
        await context.close()
    except Exception:
        pass


async def run_agentic_bot() -> None:
    """Main entry point for agentic LinkedIn Easy Apply automation."""
    validate_credentials()
    profile = load_candidate_profile()
    tracker = ApplicationTracker()

    print("\n" + "=" * 60)
    print("🤖 STARTING ZOZO-BOT (LANGGRAPH AGENTIC EASY APPLY)")
    print(f"Candidate: {profile.name} ({profile.email})")
    print(f"Search Target: {JOBLINK}")
    print("=" * 60 + "\n")

    async with async_playwright() as p:
        context: BrowserContext = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIRECTORY,
            headless=False,
            args=["--start-maximized"],
        )
        page = await context.new_page()

        print("🤖 Zozo: Verifying authentication...")
        await handleLogin(page)

        print("🤖 Zozo: Navigating to Jobs Search...")
        start = 0

        while True:
            parsed = urlparse(JOBLINK)
            query = parse_qs(parsed.query)
            query["start"] = [str(start)]
            next_url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))

            print(f"\n🌐 Opening page (start={start}): {next_url}")
            await page.goto(next_url, wait_until="load", timeout=300000)

            try:
                await stop_if_daily_submission_limit_visible(page)
            except DailySubmissionLimitReached as e:
                await stop_for_daily_limit(context, e)
                return

            # Check if this is a job search results list page
            try:
                await page.wait_for_selector(".job-card-container", timeout=5000)
                is_search_page = True
            except Exception:
                is_search_page = False

            if is_search_page:
                await human_delay(2, 4)
                try:
                    await stop_if_daily_submission_limit_visible(page)
                except DailySubmissionLimitReached as e:
                    await stop_for_daily_limit(context, e)
                    return

                job_cards = page.locator(".job-card-container")
                count = await job_cards.count()
                print(f"🤖 Zozo: Found {count} job cards on this results page.")

                for i in range(count):
                    try:
                        job_cards = page.locator(".job-card-container")
                        if i >= await job_cards.count():
                            break

                        card = job_cards.nth(i)
                        if await card.count() == 0:
                            continue

                        await card.scroll_into_view_if_needed()
                        await human_delay(1, 2)

                        # Check if already applied via UI badge
                        applied_badge = card.locator("li:has-text('Applied')")
                        if await applied_badge.count() > 0:
                            print(f"⏩ Zozo: Skipping job {i+1} — already marked 'Applied'.")
                            tracker.record_skip()
                            continue

                        print(f"\n👉 Zozo: Selecting job {i+1} of {count}...")
                        await card.click()
                        await human_delay(2, 3)
                        await stop_if_daily_submission_limit_visible(page)

                        job_title, company_name = await _get_current_job_context(page)
                        job_url = page.url
                        current_job = {"title": job_title, "company": company_name, "url": job_url}

                        print(f"📋 Job: {job_title} at {company_name}")

                        # Check exclusion list
                        if isExcludedJob(job_title, company_name):
                            tracker.record_skip()
                            continue

                        # Check session tracker to avoid duplicates
                        if tracker.is_applied(job_url):
                            print(f"⏩ Zozo: Skipping {job_title} — already recorded in tracker.")
                            tracker.record_skip()
                            continue

                        # Run the LangGraph agent for this job!
                        print("🚀 Zozo: Initiating LangGraph Easy Apply Agent...")
                        agent_result = await run_easy_apply(
                            page=page,
                            candidate_profile=profile,
                            current_job=current_job,
                            max_actions=MAX_ACTIONS_PER_APPLICATION,
                            max_retries=MAX_RETRIES,
                        )

                        completion_status = agent_result.get("completion_status")
                        if completion_status == "submitted":
                            print(f"🎉 Zozo: Successfully applied to {job_title} at {company_name}!")
                            tracker.mark_applied(job_url, job_title, company_name, status="applied")
                            await human_delay(3, 5)
                            await close_success_modal(page)
                            await connect_after_application(page)
                        else:
                            print(f"⚠️ Zozo: Application not completed (status: {completion_status})")
                            tracker.mark_applied(
                                job_url,
                                job_title,
                                company_name,
                                status="incomplete",
                                notes=f"Status: {completion_status}",
                            )

                    except DailySubmissionLimitReached as e:
                        await stop_for_daily_limit(context, e)
                        return
                    except Exception as e:
                        print(f"⚠️ Zozo: Error processing job card {i+1}: {e}")
                        tracker.record_skip()

            else:
                # Standalone single job page
                try:
                    await stop_if_daily_submission_limit_visible(page)
                    job_title, company_name = await _get_current_job_context(page)
                    current_job = {"title": job_title, "company": company_name, "url": page.url}

                    agent_result = await run_easy_apply(
                        page=page,
                        candidate_profile=profile,
                        current_job=current_job,
                        max_actions=MAX_ACTIONS_PER_APPLICATION,
                        max_retries=MAX_RETRIES,
                    )

                    if agent_result.get("completion_status") == "submitted":
                        tracker.mark_applied(page.url, job_title, company_name, status="applied")
                        await close_success_modal(page)
                        await connect_after_application(page)

                except DailySubmissionLimitReached as e:
                    await stop_for_daily_limit(context, e)
                    return

            stats = tracker.get_session_stats()
            print(f"\n📊 Current Session Stats: {stats}")
            print("🤖 Zozo: Moving to next page of job listings...")
            start += 25
            await human_delay(3, 6)
