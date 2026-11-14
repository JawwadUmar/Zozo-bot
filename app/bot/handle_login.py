from playwright.async_api import Page
from app.config.config import EMAIL, PASSWORD
from app.utils.human import human_delay, human_mouse_move,human_typing
from app.config.selectors import LOGIN_EMAIL_INPUT, LOGIN_PASSWORD_INPUT, LOGIN_SUBMIT_BUTTON, LOGIN_SUCCESS_URL_PATTERN
from app.utils.locator import get_first_available_locator

async def handleLogin(page: Page):
    await page.goto("https://www.linkedin.com/login/")

    # Wait properly
    await page.wait_for_load_state("domcontentloaded")

    if "feed" in page.url:
        print("✅ Zozo: Already logged in (session restored)!")
        return

    # Selectors
    username = await get_first_available_locator(page, LOGIN_EMAIL_INPUT)
    password = await get_first_available_locator(page, LOGIN_PASSWORD_INPUT)
    submitButton = await get_first_available_locator(page, LOGIN_SUBMIT_BUTTON)

    await username.click()
    await human_typing(username, EMAIL)

    await password.click()
    await human_typing(password, PASSWORD)
    await submitButton.click()
    
    print("🤖 Zozo: Waiting for login to complete (please solve 2FA if prompted)...")
    try:
        # Wait up to 2 minutes for the URL to change to the LinkedIn feed, confirming login is successful
        await page.wait_for_url(LOGIN_SUCCESS_URL_PATTERN[0], timeout=120000)
        print("✅ Zozo: Login confirmed!")
    except Exception as e:
        print("⚠️ Zozo: Login timed out or failed. Check the browser.")
        
    await human_delay(2, 4)
