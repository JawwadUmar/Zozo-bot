import asyncio
import random
from playwright.async_api import async_playwright

async def human_typing(element, text):
    for char in text:
        await element.type(char, delay=random.randint(40, 120))
        if random.random() < 0.07:
            await asyncio.sleep(random.uniform(0.1, 0.3))

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://www.linkedin.com/login")

        # ✅ Target elements
        # username = page.locator("#username")
        # password = page.locator("#password")

        # # Optional: click first to focus
        # await username.click()
        # await human_typing(username, "your_email_here")

        # await password.click()
        # await human_typing(password, "your_password_here")

        # # Click login
        # page.get_by_role("button", name="Sign in", exact=True).click()

        # await asyncio.sleep(5)
        await page.goto("https://www.linkedin.com/login")

        # Wait properly
        await page.wait_for_load_state("domcontentloaded")

        # Better selectors
        username = page.get_by_label("Email or phone")
        password = page.get_by_label("Password")

        await username.click()
        await human_typing(username, "your_email")

        await password.click()
        await human_typing(password, "your_password")

        await page.locator("button[type='submit']").click()
        # await browser.close()

asyncio.run(run())