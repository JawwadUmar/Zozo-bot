import asyncio
import random
from playwright.async_api import async_playwright
from app.config.config import EMAIL, PASSWORD, JOBLINK
from app.bot.handle_login import handleLogin


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await handleLogin(page)

        print("🤖 Zozo: Navigating to Jobs...")
        await page.goto(JOBLINK, wait_until="load")
        # try:
        #     await page.wait_for_selector('article.jobTuple', timeout=15000)
        # except Exception as e:
        #     print(f"🤖 JARVIS: Could not find job listings, continuing anyway... {e}")
        # await human_delay(4, 7)
        

        await asyncio.Event().wait()
asyncio.run(run())