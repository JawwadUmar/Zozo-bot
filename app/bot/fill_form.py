from app.utils.human import human_delay, human_typing
from app.config.config import PHONE_NUMBER
from app.bot.click_buttons import clickNextOrReviewButton, clickSubmitButton, clickNextButton

async def fillForm(page):
    print("🤖 Zozo: Starting dynamic form filling...")
    max_steps = 15 # safety limit to prevent infinite loops
    
    for step in range(max_steps):
        print(f"\n--- Form Step {step+1} ---")
        await human_delay(1, 2)
        
        # 1. Check if we are on the final Review page with a Submit button
        submit_btn = page.locator("button[aria-label='Submit application']:visible")
        if await submit_btn.count() > 0:
            print("🤖 Zozo: 'Submit' button found. Attempting to submit...")
            await clickSubmitButton(page)
            return  # Successfully applied!
            
        # 2. Check for Phone Number section
        phone_input = page.locator('input[id$="-phoneNumber-nationalNumber"]:visible')
        if await phone_input.count() > 0:
            await fillPhoneNumber(page)
            continue
            
        # 3. Check for Resume section
        resume_text = page.locator("span:has-text('Be sure to include an updated resume'):visible")
        if await resume_text.count() > 0:
            await handleResumePage(page)
            continue
            
        # 4. Check for Additional Questions
        add_q_header = page.locator("h3:has-text('Additional Questions'):visible")
        if await add_q_header.count() > 0:
            await handleAdditionalQuestions(page)
            continue
            
        # 5. Check for Work Authorization
        work_auth_header = page.locator("h3:has-text('Work authorization'):visible")
        if await work_auth_header.count() > 0:
            await handleWorkAuthorization(page)
            continue
            
        # 6. Fallback: If it's a page we don't explicitly handle, just try to click Next or Review
        print("🤖 Zozo: Unknown section or nothing to fill. Trying to click Next/Review...")
        try:
            # Check if there's actually a next/review button
            btn = page.locator("button[aria-label='Continue to next step']:visible, button[aria-label='Review your application']:visible")
            if await btn.count() > 0:
                await clickNextOrReviewButton(page)
            else:
                print("⚠️ Zozo: Stuck on form. No Next/Review/Submit buttons visible.")
                break
        except Exception as e:
            print(f"⚠️ Zozo: Error proceeding: {e}")
            break
            
    print("⚠️ Zozo: Form filling ended (max steps reached or got stuck).")

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
        await clickNextOrReviewButton(page)
            
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
        await clickNextOrReviewButton(page)
    except Exception:
        print("🤖 Zozo: 'Resume' section not found right now.")

async def handleWorkAuthorization(page):
    print("🤖 Zozo: Checking for 'Work authorization' section...")
    try:
        # Check if the header exists
        header = page.locator("h3:has-text('Work authorization')").first
        await header.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Work authorization' section found. Filling answers...")
        
        # Handle Radio Buttons (Fieldsets)
        fieldsets = page.locator("fieldset[data-test-form-builder-radio-button-form-component='true']")
        fs_count = await fieldsets.count()
        for i in range(fs_count):
            fs_el = fieldsets.nth(i)
            if await fs_el.is_visible():
                # Extract question text
                title_el = fs_el.locator("span[data-test-form-builder-radio-button-form-component__title]")
                question_text = "Unknown Radio Question"
                if await title_el.count() > 0:
                    question_text = await title_el.first.inner_text()
                    question_text = " ".join(question_text.split())
                
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract options
                options_loc = fs_el.locator("label[data-test-text-selectable-option__label]")
                options_count = await options_loc.count()
                
                available_options = []
                for j in range(options_count):
                    opt_text = await options_loc.nth(j).inner_text()
                    if opt_text.strip():
                        available_options.append(opt_text.strip())
                
                print(f"   Options: {available_options}")
                
                # Select the 'Yes' option or first option
                if options_count > 0:
                    yes_option = fs_el.locator("label:has-text('Yes')").first
                    if await yes_option.count() > 0:
                        await yes_option.click()
                        print(f"✅ Zozo answer: Yes")
                    else:
                        first_option_label = options_loc.first
                        await first_option_label.click()
                        answer_text = available_options[0] if available_options else "First Option"
                        print(f"✅ Zozo answer: {answer_text}")
                    await human_delay(0.5, 1.5)
                    
        print("\n✅ Zozo: Finished filling work authorization.")
        await clickNextOrReviewButton(page)
        
        
        
    except Exception as e:
        print("🤖 Zozo: 'Work authorization' section not found right now.")





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
        # 3. Handle Radio Buttons (Fieldsets)
        fieldsets = page.locator("fieldset[data-test-form-builder-radio-button-form-component='true']")
        fs_count = await fieldsets.count()
        for i in range(fs_count):
            fs_el = fieldsets.nth(i)
            if await fs_el.is_visible():
                # Extract question text
                title_el = fs_el.locator("span[data-test-form-builder-radio-button-form-component__title]")
                question_text = "Unknown Radio Question"
                if await title_el.count() > 0:
                    question_text = await title_el.first.inner_text()
                    question_text = " ".join(question_text.split())
                
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract options
                options_loc = fs_el.locator("label[data-test-text-selectable-option__label]")
                options_count = await options_loc.count()
                
                available_options = []
                for j in range(options_count):
                    opt_text = await options_loc.nth(j).inner_text()
                    if opt_text.strip():
                        available_options.append(opt_text.strip())
                
                print(f"   Options: {available_options}")
                
                # Select the first option
                if options_count > 0:
                    first_option_label = options_loc.first
                    await first_option_label.click()
                    answer_text = available_options[0] if available_options else "First Option"
                    print(f"✅ Zozo answer: {answer_text}")
                    await human_delay(0.5, 1.5)
                    
        print("\n✅ Zozo: Finished filling additional questions.")
        await clickNextOrReviewButton(page)
        
    except Exception as e:
        print("🤖 Zozo: 'Additional Questions' section not found right now.")
