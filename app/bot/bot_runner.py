import asyncio
import random
from playwright.async_api import async_playwright
from app.config.config import AUTO_CONNECT_HIRING_TEAM, JOBLINK
from app.bot.handle_login import handleLogin
from app.utils.human import human_delay
from app.bot.click_easy_apply import clickEasyApply
from app.bot.fill_form import fillForm
from app.bot.connect_hiring_team import connect_to_hiring_team
from app.bot.daily_limit import DailySubmissionLimitReached, stop_if_daily_submission_limit_visible
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from app.bot.connect_hiring_team import _get_current_job_context
from app.config.excluded_job import isExcludedJob


async def close_success_modal(page):
    print("Zozo: Closing success modal...")
    try:
        dismiss_btn = page.locator("button[data-test-modal-close-btn]:visible, button[aria-label='Dismiss']:visible, button.artdeco-modal__dismiss:visible, button:has(svg[data-test-icon='close-medium']):visible").first
        await dismiss_btn.wait_for(state="visible", timeout=5000)
        await dismiss_btn.click(force=True)
        await human_delay(1, 2)
    except Exception as e:
        print(f"Zozo: Dismiss button not found or could not be clicked. (Log: {e})")


async def connect_after_application(page):
    if not AUTO_CONNECT_HIRING_TEAM:
        print("Zozo: Hiring-team connection requests are disabled. Set AUTO_CONNECT_HIRING_TEAM=true to enable them.")
        return

    await connect_to_hiring_team(page)


async def stop_for_daily_limit(browser, error):
    print(f"Zozo: {error}")
    print("Zozo: Stopping the run now. Please apply again tomorrow.")
    await browser.close()


async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("🤖 Zozo: Handling Login...")
        await handleLogin(page)

        print("🤖 Zozo: Navigating to Jobs...")
        start = 0
        while True:
            parsed = urlparse(JOBLINK)
            query = parse_qs(parsed.query)
            query["start"] = [str(start)]
            next_url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
            print(f"Opening: {next_url}")
            await page.goto(next_url, wait_until="load", timeout=300000)
            try:
                await stop_if_daily_submission_limit_visible(page)
            except DailySubmissionLimitReached as e:
                await stop_for_daily_limit(browser, e)
                return
            
            # Check if we are on a search page with multiple job cards
            try:
                await page.wait_for_selector(".job-card-container", timeout=5000)
                is_search_page = True
            except Exception:
                is_search_page = False
                
            if is_search_page:
                await human_delay(2, 4) # Give React a moment to finish rendering the list
                try:
                    await stop_if_daily_submission_limit_visible(page)
                except DailySubmissionLimitReached as e:
                    await stop_for_daily_limit(browser, e)
                    return

                job_cards = page.locator(".job-card-container")
                count = await job_cards.count()
                print(f"🤖 Zozo: Found {count} jobs on this page.")
                
                for i in range(count):
                    try:
                        # Re-evaluate the locator in case the DOM changed
                        job_cards = page.locator(".job-card-container")
                        card = job_cards.nth(i)
                        
                        # Wait for the specific card to be attached and visible
                        if await card.count() == 0:
                            print(f"⚠️ Zozo: Job card {i+1} is no longer available in the list.")
                            continue
                            
                        await card.scroll_into_view_if_needed()
                        await human_delay(1, 2)
                        
                        # Check if already applied
                        applied_text = card.locator("li:has-text('Applied')")
                        if await applied_text.count() > 0:
                            print(f"🤖 Zozo: Skipping job {i+1} because it is already 'Applied'.")
                            continue

                        print(f"🤖 Zozo: Selecting job {i+1}...")
                        await card.click()
                        await human_delay(2, 4)
                        await stop_if_daily_submission_limit_visible(page)

                        job_title, company_name = await _get_current_job_context(page)
                        print(f"🤖 Zozo: Found job {i+1}: {job_title} at {company_name}")
                        
                        if isExcludedJob(job_title, company_name):
                            continue
                        
                        success = await clickEasyApply(page)
                        if success:
                            submitted = await fillForm(page)
                            await human_delay(10,15)
                            
                            # After applying, click dismiss on the success modal
                            print("🤖 Zozo: Closing success modal...")
                            try:
                                # Find the dismiss button by data attribute, aria-label, class, or its inner SVG icon
                                dismiss_btn = page.locator("button[data-test-modal-close-btn]:visible, button[aria-label='Dismiss']:visible, button.artdeco-modal__dismiss:visible, button:has(svg[data-test-icon='close-medium']):visible").first
                                await dismiss_btn.wait_for(state="visible", timeout=5000)
                                await dismiss_btn.click(force=True)
                                await human_delay(1, 2)
                            except Exception as e:
                                print(f"⚠️ Zozo: Dismiss button not found or could not be clicked. (Log: {e})")
                            if submitted:
                                await connect_after_application(page)
                    except DailySubmissionLimitReached as e:
                        await stop_for_daily_limit(browser, e)
                        return
                    except Exception as e:
                        print(f"⚠️ Zozo: Error processing job {i+1}: {e}. Skipping to next job...")

            else:
                # Single job page fallback
                try:
                    await stop_if_daily_submission_limit_visible(page)
                    success = await clickEasyApply(page)
                    if success:
                        submitted = await fillForm(page)
                        if submitted:
                            await close_success_modal(page)
                            await connect_after_application(page)
                except DailySubmissionLimitReached as e:
                    await stop_for_daily_limit(browser, e)
                    return
            
            print("🤖 Zozo: All done with current jobs!")
            start+=25
            await human_delay(3,6)
