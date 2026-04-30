from app.utils.human import human_delay, human_typing
from app.config.config import PHONE_NUMBER

async def fillPhoneNumber(page):
    if not PHONE_NUMBER:
        print("⚠️ Zozo: PHONE_NUMBER not found in .env, skipping phone number check.")
        return

    print("🤖 Zozo: Checking for phone number field...")
    try:
        # The ID contains dynamic parts, so we match the end of the ID which is consistent
        phone_input = page.locator('input[id$="-phoneNumber-nationalNumber"]')
        
        # Wait a short time for the field to appear on the modal
        await phone_input.wait_for(state="visible", timeout=5000)
        
        # Check if the field is empty
        current_value = await phone_input.input_value()
        if not current_value.strip():
            print(f"🤖 Zozo: Phone number field is empty. Filling it with {PHONE_NUMBER}...")
            await phone_input.click()
            await human_typing(phone_input, PHONE_NUMBER)
            print("✅ Zozo: Filled the phone number.")
        else:
            print(f"✅ Zozo: Phone number already filled with '{current_value}'. Leaving it as is.")
            
    except Exception as e:
        # If it doesn't appear or times out, it's fine, we just move on
        print("🤖 Zozo: Phone number field not found or not required right now.")

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
        print("🤖 Zozo: 'Next' button not found right now. We might be on a different step.")
