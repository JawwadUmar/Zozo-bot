from playwright.async_api import Page
from app.config.config import EMAIL, PASSWORD
from app.utils.human import human_delay, human_mouse_move,human_typing

async def handleLogin(page: Page):
    await page.goto("https://www.linkedin.com/login")

    # Wait properly
    await page.wait_for_load_state("domcontentloaded")

    # Selectors
    username = page.get_by_label("Email or phone", exact=True).locator("visible=true").first
    password = page.get_by_label("Password", exact=True).locator("visible=true").first
    submitButton = page.get_by_role("button", name="Sign in", exact=True).locator("visible=true").first

    await username.click()
    await human_typing(username, EMAIL)

    await password.click()
    await human_typing(password, PASSWORD)
    await submitButton.click()
    await human_delay()

    print("Login complete. Press Ctrl+C in the terminal to close the browser.")
 