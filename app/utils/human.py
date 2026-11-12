import asyncio
import os
import random


async def human_delay(min_sec=2, max_sec=5):
    if os.getenv("TESTING") == "1":
        return
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def human_typing(element, text):
    if os.getenv("TESTING") == "1":
        await element.fill(text)
        return

    for char in text:
        await element.type(char, delay=random.randint(40, 120))
        if random.random() < 0.07:
            await asyncio.sleep(random.uniform(0.1, 0.3))


async def human_mouse_move(page):
    if os.getenv("TESTING") == "1":
        return
    await page.mouse.move(
        random.randint(100, 800),
        random.randint(100, 600),
        steps=15
    )
