from app.utils.human import human_delay, human_typing
from app.config.config import PHONE_NUMBER
from app.bot.click_buttons import clickNextOrReviewButton, clickSubmitButton, clickNextButton
from app.bot.daily_limit import stop_if_daily_submission_limit_visible
from app.agent.ai_answer import getAiAnswer
from app.config.selectors import (
    SUBMIT_APPLICATION_BUTTON, CONTACT_INFO_HEADER, PHONE_NUMBER_INPUT, RESUME_SECTION_TEXT,
    ADDITIONAL_QUESTIONS_HEADER, WORK_AUTHORIZATION_HEADER, WORK_EXPERIENCE_HEADER,
    NEXT_OR_REVIEW_BUTTON, LOCATION_INPUT, RADIO_BUTTON_FIELDSET, RADIO_BUTTON_TITLE,
    RADIO_BUTTON_OPTION_LABEL, RADIO_YES_OPTION, TEXT_INPUT_ARTDECO, SELECT_DROPDOWN,
    SELECT_OPTION, FORM_FIELD_LABEL,
)
from app.utils.locator import get_first_available_locator

async def fillForm(page):
    print("🤖 Zozo: Starting dynamic form filling...")
    max_steps = 15 # safety limit to prevent infinite loops
    
    for step in range(max_steps):
        await stop_if_daily_submission_limit_visible(page)
        print(f"\n--- Form Step {step+1} ---")
        await human_delay(1, 2)
        await stop_if_daily_submission_limit_visible(page)
        
        # 1. Check if we are on the final Review page with a Submit button
        submit_btn = await get_first_available_locator(page, SUBMIT_APPLICATION_BUTTON)
        if submit_btn is not None:
            print("🤖 Zozo: 'Submit' button found. Attempting to submit...")
            submitted = await clickSubmitButton(page)
            await stop_if_daily_submission_limit_visible(page)
            return submitted
            
        # 2. Check for Contact info section
        contact_info_header = await get_first_available_locator(page, CONTACT_INFO_HEADER)
        if contact_info_header is not None:
            await handleContactInfo(page)
            continue
            
        # 2.1 Check for Phone Number section (fallback)
        phone_input = await get_first_available_locator(page, PHONE_NUMBER_INPUT)
        if phone_input is not None:
            await fillPhoneNumber(page)
            continue
            
        # 3. Check for Resume section
        resume_text = await get_first_available_locator(page, RESUME_SECTION_TEXT)
        if resume_text is not None:
            await handleResumePage(page)
            continue
            
        # 4. Check for Additional Questions
        add_q_header = await get_first_available_locator(page, ADDITIONAL_QUESTIONS_HEADER)
        if add_q_header is not None:
            await handleAdditionalQuestions(page)
            continue
            
        # 5. Check for Work Authorization
        work_auth_header = await get_first_available_locator(page, WORK_AUTHORIZATION_HEADER)
        if work_auth_header is not None:
            await handleWorkAuthorization(page)
            continue
            
        # 6. Check for Work Experience
        work_exp_header = await get_first_available_locator(page, WORK_EXPERIENCE_HEADER)
        if work_exp_header is not None:
            await handleWorkExperience(page)
            continue
            
        # 6. Fallback: If it's a page we don't explicitly handle, just try to click Next or Review
        print("🤖 Zozo: Unknown section or nothing to fill. Trying to click Next/Review...")
        try:
            # Check if there's actually a next/review button
            btn = await get_first_available_locator(page, NEXT_OR_REVIEW_BUTTON)
            if btn is not None:
                await clickNextOrReviewButton(page)
            else:
                print("⚠️ Zozo: Stuck on form. No Next/Review/Submit buttons visible.")
                break
        except Exception as e:
            print(f"⚠️ Zozo: Error proceeding: {e}")
            break
            
    print("⚠️ Zozo: Form filling ended (max steps reached or got stuck).")
    return False

async def handleContactInfo(page):
    print("🤖 Zozo: Checking for 'Contact info' section...")
    try:
        header = await get_first_available_locator(page, CONTACT_INFO_HEADER)
        await header.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Contact info' section found. Checking fields...")
        
        # 1. Fill Phone Number
        if PHONE_NUMBER:
            phone_input = await get_first_available_locator(page, PHONE_NUMBER_INPUT)
            if phone_input is not None:
                current_value = await phone_input.input_value()
                if not current_value.strip():
                    print(f"🤖 Zozo: Phone number field is empty. Filling it with {PHONE_NUMBER}...")
                    await phone_input.click()
                    await human_typing(phone_input.first, PHONE_NUMBER)
                    print("✅ Zozo: Filled the phone number.")
                else:
                    print(f"✅ Zozo: Phone number already filled with '{current_value}'.")
        
        # 2. Fill Location
        location_input = await get_first_available_locator(page, LOCATION_INPUT)
        if location_input is not None:
            current_value = await location_input.input_value()
            if not current_value.strip():
                print("🤖 Zozo: Location field is empty. Filling it...")
                await location_input.click()
                await human_typing(location_input.first, "Kolkata, West Bengal, India")
                await human_delay(2, 3) # Wait for typeahead options to appear
                
                # Press ArrowDown and Enter to select the first option from dropdown
                await location_input.press("ArrowDown")
                await human_delay(0.5, 1)
                await location_input.press("Enter")
                print("✅ Zozo: Filled the location.")
            else:
                print(f"✅ Zozo: Location already filled with '{current_value}'.")
                
        await clickNextOrReviewButton(page)
        
    except Exception as e:
        print("🤖 Zozo: 'Contact info' section not found right now.")


async def fillPhoneNumber(page):
    if not PHONE_NUMBER:
        print("⚠️ Zozo: PHONE_NUMBER not found in .env, skipping phone number check.")
        return

    print("🤖 Zozo: Checking for phone number field...")
    try:
        # The ID contains dynamic parts, so we match the end of the ID which is consistent
        phone_input = await get_first_available_locator(page, PHONE_NUMBER_INPUT)
        
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
        resume_text = await get_first_available_locator(page, RESUME_SECTION_TEXT)
        await resume_text.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Resume' section found. Resume already attached, clicking Next...")
        await clickNextOrReviewButton(page)
    except Exception:
        print("🤖 Zozo: 'Resume' section not found right now.")

async def handleWorkAuthorization(page):
    print("🤖 Zozo: Checking for 'Work authorization' section...")
    try:
        # Check if the header exists
        header = await get_first_available_locator(page, WORK_AUTHORIZATION_HEADER)
        await header.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Work authorization' section found. Filling answers...")
        
        # Handle Radio Buttons (Fieldsets)
        fieldsets = page.locator(RADIO_BUTTON_FIELDSET[0])
        fs_count = await fieldsets.count()
        for i in range(fs_count):
            fs_el = fieldsets.nth(i)
            if await fs_el.is_visible():
                # Extract question text
                title_el = fs_el.locator(RADIO_BUTTON_TITLE[0])
                question_text = "Unknown Radio Question"
                if await title_el.count() > 0:
                    question_text = await title_el.first.inner_text()
                    question_text = " ".join(question_text.split())
                
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract options
                options_loc = fs_el.locator(RADIO_BUTTON_OPTION_LABEL[0])
                options_count = await options_loc.count()
                
                available_options = []
                for j in range(options_count):
                    opt_text = await options_loc.nth(j).inner_text()
                    if opt_text.strip():
                        available_options.append(opt_text.strip())
                
                print(f"   Options: {available_options}")
                
                # Select the 'Yes' option or first option
                if options_count > 0:
                    yes_option = await get_first_available_locator(fs_el, RADIO_YES_OPTION)
                    if yes_option is not None:
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
        header = await get_first_available_locator(page, ADDITIONAL_QUESTIONS_HEADER)
        await header.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Additional Questions' section found. Filling answers...")
        
        # 1. Handle Text Inputs
        text_inputs = page.locator(TEXT_INPUT_ARTDECO[0])
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
                        label = await get_first_available_locator(page, [FORM_FIELD_LABEL[0].format(id=input_id)])
                        if label is not None:
                            question_text = await label.first.inner_text()
                    
                    # Clean up the text (removes extra newlines/spaces)
                    question_text = " ".join(question_text.split())
                    print(f"\n🤖 Zozo detected question: {question_text}")
                    
                    if "numeric" in input_id.lower():
                        # Integer required
                        answer = await getAiAnswer(None, question_text, True)
                        await input_el.click()
                        await human_typing(input_el, answer)
                        print(f"✅ Zozo answer: {answer}")
                    else:
                        # Random text value
                        answer = await getAiAnswer(None, question_text, False)
                        await input_el.click()
                        await human_typing(input_el, answer)
                        print(f"✅ Zozo answer: {answer}")
        
        # 2. Handle Select Dropdowns
        selects = page.locator(SELECT_DROPDOWN[0])
        select_count = await selects.count()
        for i in range(select_count):
            select_el = selects.nth(i)
            if await select_el.is_visible():
                select_id = await select_el.get_attribute("id") or ""
                
                # Extract question text from label
                question_text = "Unknown Question"
                if select_id:
                    label = await get_first_available_locator(page, [FORM_FIELD_LABEL[0].format(id=select_id)])
                    if label is not None:
                        question_text = await label.first.inner_text()
                
                question_text = " ".join(question_text.split())
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract and print options
                options_loc = select_el.locator(SELECT_OPTION[0])
                options_count = await options_loc.count()
                
                available_options = []
                for j in range(options_count):
                    opt_text = await options_loc.nth(j).inner_text()
                    if opt_text.strip() and opt_text.strip() != "Select an option":
                        available_options.append(opt_text.strip())
                
                print(f"   Options: {available_options}")
                
                # We want to select the first valid option (index 1). 
                if options_count > 1:
                    await select_el.click()
                    # answer = await getAiAnswer(available_options, question_text, False)
                    # await select_el.select_option(answer)
                    await select_el.select_option(index=1)
                    answer_text = await options_loc.nth(1).inner_text()
                    print(f"✅ Zozo answer: {answer_text}")
        # 3. Handle Radio Buttons (Fieldsets)
        fieldsets = page.locator(RADIO_BUTTON_FIELDSET[0])
        fs_count = await fieldsets.count()
        for i in range(fs_count):
            fs_el = fieldsets.nth(i)
            if await fs_el.is_visible():
                # Extract question text
                title_el = fs_el.locator(RADIO_BUTTON_TITLE[0])
                question_text = "Unknown Radio Question"
                if await title_el.count() > 0:
                    question_text = await title_el.first.inner_text()
                    question_text = " ".join(question_text.split())
                
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract options
                options_loc = fs_el.locator(RADIO_BUTTON_OPTION_LABEL[0])
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


async def handleWorkExperience(page):
    print("🤖 Zozo: Checking for 'Work experience' section...")
    try:
        # Check if the header exists
        header = await get_first_available_locator(page, WORK_EXPERIENCE_HEADER)
        await header.wait_for(state="visible", timeout=3000)
        print("🤖 Zozo: 'Work experience' section found. Filling answers...")
        
        # 1. Handle Text Inputs
        text_inputs = page.locator(TEXT_INPUT_ARTDECO[0])
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
                        label = await get_first_available_locator(page, [FORM_FIELD_LABEL[0].format(id=input_id)])
                        if label is not None:
                            question_text = await label.first.inner_text()
                    
                    # Clean up the text (removes extra newlines/spaces)
                    question_text = " ".join(question_text.split())
                    print(f"\n🤖 Zozo detected question: {question_text}")
                    
                    if "numeric" in input_id.lower():
                        # Integer required
                        answer = await getAiAnswer(None, question_text, True)
                        await input_el.click()
                        await human_typing(input_el, answer)
                        print(f"✅ Zozo answer: {answer}")
                    else:
                        # Random text value
                        answer = await getAiAnswer(None, question_text, False)
                        await input_el.click()
                        await human_typing(input_el, answer)
                        print(f"✅ Zozo answer: {answer}")

        # 2. Handle Select Dropdowns
        selects = page.locator(SELECT_DROPDOWN[0])
        select_count = await selects.count()
        for i in range(select_count):
            select_el = selects.nth(i)
            if await select_el.is_visible():
                select_id = await select_el.get_attribute("id") or ""
                
                # Extract question text from label
                question_text = "Unknown Question"
                if select_id:
                    label = await get_first_available_locator(page, [FORM_FIELD_LABEL[0].format(id=select_id)])
                    if label is not None:
                        question_text = await label.first.inner_text()
                
                question_text = " ".join(question_text.split())
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract and print options
                options_loc = select_el.locator(SELECT_OPTION[0])
                options_count = await options_loc.count()
                
                available_options = []
                for j in range(options_count):
                    opt_text = await options_loc.nth(j).inner_text()
                    if opt_text.strip() and opt_text.strip() != "Select an option":
                        available_options.append(opt_text.strip())
                
                print(f"   Options: {available_options}")
                
                # We want to select the option generated by AI 
                if options_count > 1:
                    await select_el.click()
                    answer = await getAiAnswer(available_options, question_text, False)
                    try:
                        await select_el.select_option(answer)
                        print(f"✅ Zozo answer: {answer}")
                    except Exception as e:
                        print(f"⚠️ Zozo: AI answer '{answer}' not found in options, selecting first valid option.")
                        await select_el.select_option(index=1)
                        answer_text = await options_loc.nth(1).inner_text()
                        print(f"✅ Zozo fallback answer: {answer_text}")

        # 3. Handle Radio Buttons (Fieldsets)
        fieldsets = page.locator(RADIO_BUTTON_FIELDSET[0])
        fs_count = await fieldsets.count()
        for i in range(fs_count):
            fs_el = fieldsets.nth(i)
            if await fs_el.is_visible():
                # Extract question text
                title_el = fs_el.locator(RADIO_BUTTON_TITLE[0])
                question_text = "Unknown Radio Question"
                if await title_el.count() > 0:
                    question_text = await title_el.first.inner_text()
                    question_text = " ".join(question_text.split())
                
                print(f"\n🤖 Zozo detected question: {question_text}")
                
                # Extract options
                options_loc = fs_el.locator(RADIO_BUTTON_OPTION_LABEL[0])
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
                        
        print("\n✅ Zozo: Finished filling work experience.")
        await clickNextOrReviewButton(page)
        
    except Exception as e:
        print("🤖 Zozo: 'Work experience' section not found right now.")

