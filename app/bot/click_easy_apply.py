
from app.utils.human import human_delay

async def clickEasyApply(page):
    try:
        # We use the class .jobs-apply-button and filter by visible to ensure we target the right one
        apply_button = page.locator(".jobs-apply-button:visible").first
        await apply_button.wait_for(state="visible", timeout=15000)
        
        # Add a slight delay before clicking to act human
        await human_delay(1, 3)
        await apply_button.click()
        print("✅ Zozo: Clicked 'Easy Apply'!")
        
    except Exception as e:
        print(f"⚠️ Zozo: Could not find or click the Easy Apply button: {e}")
        return
        
    # Wait to see if the "Continue applying" warning modal pops up
    try:
        # Use a short timeout because this modal won't always appear
        continue_button = page.get_by_role("button", name="Continue applying").locator("visible=true").first
        await continue_button.wait_for(state="visible", timeout=3000)
        
        await human_delay(1, 2)
        await continue_button.click()
        print("✅ Zozo: Clicked 'Continue applying'!")
    except Exception:
        # If it times out, that means the modal didn't pop up, which is perfectly fine.
        pass
    
    await human_delay(3, 6)