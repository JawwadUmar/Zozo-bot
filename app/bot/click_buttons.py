from app.utils.human import human_delay
# ================================Next or Review Button =======================================

async def clickNextOrReviewButton(page):
    print("🤖 Zozo: Checking for 'Next' or 'Review' button...")
    try:
        # Use a comma-separated locator to find either the Next or Review button, whichever is visible
        button = page.locator("button[aria-label='Continue to next step']:visible, button[aria-label='Review your application']:visible").first
        
        await button.wait_for(state="visible", timeout=3000)
        
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
        submit_button = page.locator("button[aria-label='Submit application']:visible").first
        await submit_button.wait_for(state="visible", timeout=3000)
        
        # Uncheck "Follow company" if it exists and is checked
        follow_checkbox = page.locator("input#follow-company-checkbox")
        if await follow_checkbox.count() > 0 and await follow_checkbox.first.is_visible():
            is_checked = await follow_checkbox.first.is_checked()
            if is_checked:
                print("🤖 Zozo: Unchecking 'Follow company'...")
                # Best practice is to click its label since the actual checkbox input may be hidden
                follow_label = page.locator("label[for='follow-company-checkbox']").first
                if await follow_label.count() > 0:
                    await follow_label.click()
                else:
                    await follow_checkbox.first.click()
                await human_delay(0.5, 1.0)
                
        await human_delay(1, 3)
        await submit_button.click()
        print("✅ Zozo: Clicked the 'Submit application' button. Application Sent!")
        
    except Exception as e:
        print(f"🤖 Zozo: 'Submit application' button not found right now. (Log: {e})")

# ================================Review Button =======================================

async def clickReviewButton(page):
    print("🤖 Zozo: Checking for 'Review' button...")
    try:
        # Locate the button using the aria-label from the HTML snippet
        review_button = page.locator("button[aria-label='Review your application']:visible").first
        
        await review_button.wait_for(state="visible", timeout=3000)
        
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
        next_button = page.locator("button[aria-label='Continue to next step']:visible").first
        
        await next_button.wait_for(state="visible", timeout=3000)
        
        await human_delay(1, 3)
        await next_button.click()
        print("✅ Zozo: Clicked the 'Next' button.")
        
    except Exception as e:
        print(f"🤖 Zozo: 'Next' button not found right now. We might be on a different step. (Log: {e})")