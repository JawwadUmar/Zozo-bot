import asyncio
import random
from playwright.async_api import async_playwright
from app.config.config import EMAIL, PASSWORD, JOBLINK
from app.bot.handle_login import handleLogin
from app.utils.human import human_delay
from app.bot.click_easy_apply import clickEasyApply
from app.bot.fill_form import fillPhoneNumber


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("🤖 Zozo: Handling Login...")
        await handleLogin(page)

        print("🤖 Zozo: Navigating to Jobs...")
        await page.goto(JOBLINK, wait_until="load")
        
        await clickEasyApply(page)
        await fillPhoneNumber(page)
        
        await asyncio.Event().wait()
asyncio.run(run())