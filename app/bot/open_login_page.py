from playwright.async_api import Page
from app.config.config import EMAIL, PASSWORD
from app.utils.human import human_delay, human_mouse_move,human_typing

async def handleLogin(page: Page):
    print("🤖 JARVIS: Initiating Human Sequence...")
    await page.goto("https://www.linkedin.com/login/", wait_until="networkidle")
    await human_delay(2, 4)

    # login
    page.fill("#username", "your_email@gmail.com")
    page.fill("#password", "your_password")
    page.get_by_role("button", name="Sign in").click()
    await human_delay(1, 2)

    

    await human_typing(
        page.locator("//input[@placeholder='Enter your active Email ID / Username']"),
        EMAIL
    )

    await human_typing(
        page.locator("//input[@placeholder='Enter your password']"),
        PASSWORD
    )

    await page.click("//button[@type='submit']")

    await page.wait_for_selector('.nI-gNb-header__logo', timeout=15000)
    print("✅ JARVIS: Logged in. Cooling down...")
    await human_mouse_move(page)
    await human_delay(6, 10)