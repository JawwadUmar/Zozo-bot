
from app.utils.human import human_delay
from app.bot.daily_limit import DailySubmissionLimitReached, stop_if_daily_submission_limit_visible
from app.config.selectors import EASY_APPLY_BUTTON, CONTINUE_APPLYING_BUTTON
from app.utils.locator import get_first_available_locator

async def clickEasyApply(page):
    await stop_if_daily_submission_limit_visible(page)

    try:
        # We use the class .jobs-apply-button and filter by visible to ensure we target the right one
        apply_button = await get_first_available_locator(page, EASY_APPLY_BUTTON, timeout=15000)
        if apply_button is None:
            raise TimeoutError("Easy Apply button not found")
        
        # Add a slight delay before clicking to act human
        await human_delay(1, 3)
        await apply_button.click()
        print("✅ Zozo: Clicked 'Easy Apply'!")
        await stop_if_daily_submission_limit_visible(page)
        
    except DailySubmissionLimitReached:
        raise
    except Exception as e:
        await stop_if_daily_submission_limit_visible(page)
        print(f"⚠️ Zozo: Could not find or click the Easy Apply button: {e}")
        return False
        
    # Wait to see if the "Continue applying" warning modal pops up
    try:
        # Use a short timeout because this modal won't always appear
        continue_button = await get_first_available_locator(page, CONTINUE_APPLYING_BUTTON)
        if continue_button is not None:
            await human_delay(1, 2)
            await continue_button.click()
            print("✅ Zozo: Clicked 'Continue applying'!")
            await stop_if_daily_submission_limit_visible(page)
    except DailySubmissionLimitReached:
        raise
    except Exception:
        # If it times out, that means the modal didn't pop up, which is perfectly fine.
        pass
    
    await human_delay(3, 6)
    await stop_if_daily_submission_limit_visible(page)
    return True
