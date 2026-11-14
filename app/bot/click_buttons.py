from app.utils.human import human_delay
from app.config.selectors import NEXT_OR_REVIEW_BUTTON, SUBMIT_APPLICATION_BUTTON, FOLLOW_COMPANY_CHECKBOX, FOLLOW_COMPANY_LABEL, REVIEW_APPLICATION_BUTTON, NEXT_STEP_BUTTON
from app.utils.locator import get_first_available_locator
# ================================Next or Review Button =======================================

async def clickNextOrReviewButton(page):
    print("🤖 Zozo: Checking for 'Next' or 'Review' button...")
    try:
        # Use a comma-separated locator to find either the Next or Review button, whichever is visible
        button = await get_first_available_locator(page, NEXT_OR_REVIEW_BUTTON)
        if button is None:
            raise TimeoutError("Next or Review button not found")
        
        btn_text = await button.inner_text()
        await human_delay(1, 3)
        await button.click()
        print(f"✅ Zozo: Clicked the '{btn_text.strip()}' button.")
        
    except Exception as e:
        print(f"🤖 Zozo: 'Next' or 'Review' button not found right now. (Log: {e})")

# ================================Submit Button =======================================

async def clickSubmitButton(page):
    print("🤖 Zozo: Checking for 'Submit application' button...")
    try:
        # Locate the Submit application button by aria-label from the user's snippet
        submit_button = await get_first_available_locator(page, SUBMIT_APPLICATION_BUTTON)
        if submit_button is None:
            raise TimeoutError("Submit button not found")
        
        # Uncheck "Follow company" if it exists and is checked
        follow_checkbox = await get_first_available_locator(page, FOLLOW_COMPANY_CHECKBOX, state="attached")
        if follow_checkbox is not None and await follow_checkbox.is_visible():
            is_checked = await follow_checkbox.is_checked()
            if is_checked:
                print("🤖 Zozo: Unchecking 'Follow company'...")
                # Best practice is to click its label since the actual checkbox input may be hidden
                follow_label = await get_first_available_locator(page, FOLLOW_COMPANY_LABEL, state="attached")
                if follow_label is not None:
                    await follow_label.click()
                else:
                    await follow_checkbox.click()
                await human_delay(0.5, 1.0)
                
        await human_delay(1, 3)
        await submit_button.click()
        print("✅ Zozo: Clicked the 'Submit application' button. Application Sent!")
        return True
        
    except Exception as e:
        print(f"🤖 Zozo: 'Submit application' button not found right now. (Log: {e})")
        return False

# ================================Review Button =======================================

async def clickReviewButton(page):
    print("🤖 Zozo: Checking for 'Review' button...")
    try:
        # Locate the button using the aria-label from the HTML snippet
        review_button = await get_first_available_locator(page, REVIEW_APPLICATION_BUTTON)
        if review_button is None:
            raise TimeoutError("Review button not found")
        
        await human_delay(1, 3)
        await review_button.click()
        print("✅ Zozo: Clicked the 'Review' button.")
        
    except Exception as e:
        print(f"🤖 Zozo: 'Review' button not found right now. (Log: {e})")

# ================================Next Button =======================================

async def clickNextButton(page):
    print("🤖 Zozo: Checking for 'Next' button...")
    try:
        # Locate the button using the aria-label from the HTML snippet
        next_button = await get_first_available_locator(page, NEXT_STEP_BUTTON)
        if next_button is None:
            raise TimeoutError("Next button not found")
        
        await human_delay(1, 3)
        await next_button.click()
        print("✅ Zozo: Clicked the 'Next' button.")
        
    except Exception as e:
        print(f"🤖 Zozo: 'Next' button not found right now. We might be on a different step. (Log: {e})")
