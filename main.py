import asyncio
import random
from playwright.async_api import async_playwright
from app.config.config import EMAIL, PASSWORD
from app.bot.handle_login import handleLogin

async def human_typing(element, text):
    for char in text:
        await element.type(char, delay=random.randint(40, 120))
        if random.random() < 0.07:
            await asyncio.sleep(random.uniform(0.1, 0.3))

async def human_mouse_move(page):
    await page.mouse.move(
        random.randint(100, 800),
        random.randint(100, 600),
        steps=15
    )
async def human_delay(min_sec=2, max_sec=5):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await handleLogin(page)
        await asyncio.Event().wait()
asyncio.run(run())