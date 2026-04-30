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
    
    print("🤖 Zozo: Waiting for login to complete (please solve 2FA if prompted)...")
    try:
        # Wait up to 2 minutes for the URL to change to the LinkedIn feed, confirming login is successful
        await page.wait_for_url("**/feed/**", timeout=120000)
        print("✅ Zozo: Login confirmed!")
    except Exception as e:
        print("⚠️ Zozo: Login timed out or failed. Check the browser.")
        
    await human_delay(2, 4)