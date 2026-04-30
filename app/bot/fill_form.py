from app.utils.human import human_delay, human_typing
from app.config.config import PHONE_NUMBER

async def fillForm(page):
    await fillPhoneNumber(page)
    await clickNextButton(page)
    await handleResumePage(page)
    await handleAdditionalQuestions(page)

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

async def handleResumePage(page):
    print("🤖 Zozo: Checking for 'Resume' section...")
    try:
        # Check if the specific text/span exists
        resume_text = page.locator("span:has-text('Be sure to include an updated resume')").first
        await resume_text.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Resume' section found. Resume already attached, clicking Next...")
        await clickNextButton(page)
    except Exception:
        print("🤖 Zozo: 'Resume' section not found right now.")

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

async def handleAdditionalQuestions(page):
    print("🤖 Zozo: Checking for 'Additional Questions' section...")
    try:
        # Check if the header exists
        header = page.locator("h3:has-text('Additional Questions')").first
        await header.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Additional Questions' section found. Filling answers...")
        
        # 1. Handle Text Inputs
        text_inputs = page.locator("input.artdeco-text-input--input[type='text']")
        count = await text_inputs.count()
        for i in range(count):
            input_el = text_inputs.nth(i)
            if await input_el.is_visible():
                current_val = await input_el.input_value()
                if not current_val.strip():
                    input_id = await input_el.get_attribute("id") or ""
                    
                    # Extract question text from label
                    question_text = "Unknown Question"
                    if input_id:
                        label = page.locator(f"label[for='{input_id}']")
                        if await label.count() > 0:
                            question_text = await label.first.inner_text()
                    
                    # Clean up the text (removes extra newlines/spaces)
                    question_text = " ".join(question_text.split())
                    print(f"\n🤖 Zozo detected question: {question_text}")
                    
                    if "numeric" in input_id.lower():
                        # Integer required
                        await input_el.click()
                        await human_typing(input_el, "1")
                        print("✅ Zozo answer: 1")
                    else:
                        # Random text value
                        await input_el.click()
                        await human_typing(input_el, "val")
                        print("✅ Zozo answer: val")
        
        # 2. Handle Select Dropdowns
        selects = page.locator("select.fb-dash-form-element__select-dropdown")
        select_count = await selects.count()
        for i in range(select_count):
            select_el = selects.nth(i)
            if await select_el.is_visible():
                select_id = await select_el.get_attribute("id") or ""
                
                # Extract question text from label
                question_text = "Unknown Question"
                if select_id:
                    label = page.locator(f"label[for='{select_id}']")
                    if await label.count() > 0:
                        question_text = await label.first.inner_text()
                
                question_text = " ".join(question_text.split())
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract and print options
                options_loc = select_el.locator("option")
                options_count = await options_loc.count()
                
                available_options = []
                for j in range(options_count):
                    opt_text = await options_loc.nth(j).inner_text()
                    if opt_text.strip() and opt_text.strip() != "Select an option":
                        available_options.append(opt_text.strip())
                
                print(f"   Options: {available_options}")
                
                # We want to select the first valid option (index 1). 
                if options_count > 1:
                    await select_el.select_option(index=1)
                    answer_text = await options_loc.nth(1).inner_text()
                    print(f"✅ Zozo answer: {answer_text.strip()}")
                    await human_delay(0.5, 1.5)
                    
        print("\n✅ Zozo: Finished filling additional questions.")
        
    except Exception as e:
        print("🤖 Zozo: 'Additional Questions' section not found right now.")
