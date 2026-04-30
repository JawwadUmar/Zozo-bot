from app.utils.human import human_delay, human_typing
from app.config.config import PHONE_NUMBER

async def fillForm(page):
    await fillPhoneNumber(page)
    await clickNextOrReviewButton(page)
    await handleResumePage(page)
    await clickNextOrReviewButton(page)
    await handleAdditionalQuestions(page)
    await clickNextOrReviewButton(page)
    await handleWorkAuthorization(page)
    await clickNextOrReviewButton(page)
    await clickSubmitButton(page)

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
        
        
        
    except Exception as e:
        print("🤖 Zozo: 'Work authorization' section not found right now.")

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
        print("🤖 Zozo: Neither 'Next' nor 'Review' button found right now.")

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
        print("🤖 Zozo: 'Submit application' button not found right now.")

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
        
    except Exception as e:
        print("🤖 Zozo: 'Additional Questions' section not found right now.")


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
        print("🤖 Zozo: 'Review' button not found right now.")

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
