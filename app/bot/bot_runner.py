import asyncio
import random
from playwright.async_api import async_playwright
from app.config.config import EMAIL, PASSWORD, JOBLINK
from app.bot.handle_login import handleLogin
from app.utils.human import human_delay
from app.bot.click_easy_apply import clickEasyApply
from app.bot.fill_form import fillForm

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("🤖 Zozo: Handling Login...")
        await handleLogin(page)

        print("🤖 Zozo: Navigating to Jobs...")
        await page.goto(JOBLINK, wait_until="load", timeout=300000)
        
        # Check if we are on a search page with multiple job cards
        try:
            await page.wait_for_selector(".job-card-container", timeout=5000)
            is_search_page = True
        except Exception:
            is_search_page = False
            
        if is_search_page:
            job_cards = page.locator(".job-card-container")
            count = await job_cards.count()
            print(f"🤖 Zozo: Found {count} jobs on this page.")
            
            for i in range(count):
                card = job_cards.nth(i)
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
                
                success = await clickEasyApply(page)
                if success:
                    await fillForm(page)
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
        else:
            # Single job page fallback
            success = await clickEasyApply(page)
            if success:
                await fillForm(page)
        
        print("🤖 Zozo: All done with current jobs!")
        await asyncio.Event().wait()