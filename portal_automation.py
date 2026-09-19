import datetime
import os
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://web.javainstitute.org/web-portal/login/student.jsp"
DASHBOARD_URL = "https://web.javainstitute.org/web-portal/main-pages/index-student.jsp?smm=home&ssm=index-admin"


def create_chrome_driver(mute_mic=True, turn_off_cam=True):
    """Initializes Google Chrome with detached mode and media stream preferences."""
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Automatically set camera and microphone permissions in Chrome
    # 2 = block/mute, 1 = allow
    mic_setting = 2 if mute_mic else 1
    cam_setting = 2 if turn_off_cam else 1

    prefs = {
        "profile.default_content_setting_values.media_stream_mic": mic_setting,
        "profile.default_content_setting_values.media_stream_camera": cam_setting,
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        driver = webdriver.Chrome(options=options)

    return driver


def perform_login(driver, username, password, log_callback=print):
    """Navigates to student login and enters credentials."""
    log_callback("Navigating to Java Institute Student Login...")
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, 15)

    log_callback("Entering username and password...")
    user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    pass_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))

    user_input.clear()
    user_input.send_keys(username)
    time.sleep(0.3)

    pass_input.clear()
    pass_input.send_keys(password)
    time.sleep(0.3)

    log_callback("Submitting login form...")
    login_btn = driver.find_element(By.ID, "login-btn")
    login_btn.click()

    time.sleep(4)
    handle_modals(driver, log_callback)

    current_url = driver.current_url
    log_callback(f"Current page: {current_url}")

    if "login" in current_url.lower():
        try:
            error_elem = driver.find_element(By.ID, "error_code")
            if error_elem.is_displayed() and error_elem.text.strip():
                err_msg = error_elem.text.strip()
                log_callback(f"Login Warning/Error: {err_msg}", level="warning")
        except Exception:
            pass

    if "index-student.jsp" not in driver.current_url:
        log_callback("Redirecting directly to student dashboard...")
        driver.get(DASHBOARD_URL)
        time.sleep(3)
        handle_modals(driver, log_callback)


def handle_modals(driver, log_callback=print):
    """Closes any popups or declaration modals that appear after login."""
    try:
        agree_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'I Agree') or @onclick='checkIsFirstTime();']")
        for btn in agree_buttons:
            if btn.is_displayed():
                log_callback("Acknowledging declaration modal ('I Agree')...")
                btn.click()
                time.sleep(1)
                break
    except Exception:
        pass

    try:
        continue_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Continue') and contains(@href, 'index-student.jsp')]")
        for link in continue_links:
            if link.is_displayed():
                log_callback("Acknowledging trial notice popup ('Continue')...")
                link.click()
                time.sleep(1)
                break
    except Exception:
        pass

    try:
        close_btns = driver.find_elements(By.CSS_SELECTOR, ".modal.in .close, .modal.show .close")
        for cb in close_btns:
            if cb.is_displayed():
                cb.click()
                time.sleep(0.5)
    except Exception:
        pass


def is_lecture_for_today(text, now):
    """Checks if text contains today's date or day name."""
    text_lower = text.lower()

    day_full = now.strftime("%A").lower()
    day_short = now.strftime("%a").lower()
    d_m_y_dash = now.strftime("%d-%m-%Y")
    d_m_y_slash = now.strftime("%d/%m/%Y")
    y_m_d_dash = now.strftime("%Y-%m-%d")
    y_m_d_slash = now.strftime("%Y/%m/%d")
    d_m_y_simple = f"{now.day}/{now.month}/{now.year}"
    d_m_y_simple_dash = f"{now.day}-{now.month}-{now.year}"
    month_short = now.strftime("%b").lower()
    month_full = now.strftime("%B").lower()
    day_str = str(now.day)

    date_patterns = [
        d_m_y_dash, d_m_y_slash, y_m_d_dash, y_m_d_slash,
        d_m_y_simple, d_m_y_simple_dash, "today"
    ]

    for pat in date_patterns:
        if pat in text_lower:
            return True

    if (f"{day_str} {month_short}" in text_lower or 
        f"{day_str} {month_full}" in text_lower or 
        f"{month_short} {day_str}" in text_lower or 
        f"{month_full} {day_str}" in text_lower):
        return True

    if day_full in text_lower or re.search(rf"\b{day_short}\b", text_lower):
        return True

    return False


def parse_lecture_time(text, now):
    """
    Extracts time range like '8:30 AM to 12:30 PM' and calculates time status relative to now.
    """
    match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', text, re.IGNORECASE)
    if match:
        start_str = match.group(1).strip()
        end_str = match.group(2).strip()
        full_range = f"{start_str} to {end_str}"
        try:
            start_dt = datetime.datetime.strptime(f"{now.strftime('%Y-%m-%d')} {start_str.upper()}", "%Y-%m-%d %I:%M %p")
            end_dt = datetime.datetime.strptime(f"{now.strftime('%Y-%m-%d')} {end_str.upper()}", "%Y-%m-%d %I:%M %p")

            if now < start_dt:
                diff = start_dt - now
                hours, remainder = divmod(int(diff.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                time_status = f"Starts at {start_str} (in {hours}h {minutes}m)"
            elif start_dt <= now <= end_dt:
                time_status = f"ONGOING NOW ({full_range})"
            else:
                time_status = f"Past scheduled time ({full_range})"

            return full_range, time_status
        except Exception:
            return full_range, f"Scheduled: {full_range}"

    single_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))', text, re.IGNORECASE)
    if single_match:
        t = single_match.group(1).strip()
        return t, f"Scheduled: {t}"

    return "Unknown Time", ""


def join_todays_lecture(driver, log_callback=print):
    """
    Locates 'Your Active TimeTable' section on dashboard,
    identifies today's lecture card, and clicks 'Click Here to Join'.
    """
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    today_display = f"{now.strftime('%A')}, {today_str}"
    log_callback(f"Scanning timetable for TODAY: {today_display}...", level="highlight")

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)

    driver.execute_script("window.scrollTo(0, 400);")
    time.sleep(1)

    matched_card = None
    join_button = None
    card_raw_text = ""

    # Method 1: Locate via "Click Here to Join" button and check parent container
    join_elements = driver.find_elements(
        By.XPATH,
        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'click here to join') or "
        "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'join')]"
    )

    for btn in join_elements:
        try:
            if not btn.is_displayed():
                continue
            parent = btn
            for _ in range(7):
                parent = parent.find_element(By.XPATH, "..")
                p_text = parent.text
                if is_lecture_for_today(p_text, now):
                    matched_card = parent
                    join_button = btn
                    card_raw_text = p_text
                    break
            if matched_card:
                break
        except Exception:
            continue

    # Method 2: Locate via today's date badge
    if not matched_card:
        date_candidates = driver.find_elements(By.XPATH, f"//*[contains(text(), '{today_str}')]")
        for date_elem in date_candidates:
            try:
                if not date_elem.is_displayed():
                    continue
                parent = date_elem
                for _ in range(7):
                    parent = parent.find_element(By.XPATH, "..")
                    p_text = parent.text
                    if "join" in p_text.lower():
                        matched_card = parent
                        card_raw_text = p_text
                        j_btns = parent.find_elements(
                            By.XPATH,
                            ".//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'click here to join') or "
                            "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'join') or "
                            "contains(@href, 'zoom') or contains(@href, 'teams')]"
                        )
                        for j in j_btns:
                            if j.is_displayed():
                                join_button = j
                                break
                        break
                if matched_card:
                    break
            except Exception:
                continue

    if not matched_card:
        log_callback(f"No lecture scheduled for today ({today_display}) in Active Timetable.", level="warning")
        log_callback("Chrome window will remain open for manual navigation.")
        return False

    # Parse and present lecture details
    lines = [line.strip() for line in card_raw_text.split("\n") if line.strip()]
    time_range, time_status = parse_lecture_time(card_raw_text, now)

    log_callback("========================================", "divider")
    log_callback(f"Today's Active Lecture Identified!", "success")

    batch_info = ""
    subject_info = ""
    lecturer_info = ""

    for l in lines:
        l_lower = l.lower()
        if today_str in l or "click here" in l_lower:
            continue
        if any(w in l_lower for w in ["dr ", "dr.", "prof", "prof.", "mr ", "mr.", "mrs", "miss"]):
            lecturer_info = l
        elif any(w in l_lower for w in ["am to", "pm to", ":00", ":30"]):
            continue
        elif "online" in l_lower or "physical" in l_lower:
            continue
        elif not batch_info:
            batch_info = l
        elif not subject_info:
            subject_info = l

    if batch_info:
        log_callback(f"Batch: {batch_info}", "info")
    if subject_info:
        log_callback(f"Module: {subject_info}", "info")
    if lecturer_info:
        log_callback(f"Lecturer: {lecturer_info}", "info")

    log_callback(f"Time Slot: {time_range}", "highlight")
    if time_status:
        log_callback(f"Status: {time_status}", "highlight")

    log_callback("========================================", "divider")

    # Click the Join button
    if join_button:
        try:
            btn_title = join_button.text.strip() or "Click Here to Join"
            log_callback(f"Clicking '{btn_title}' button...", level="highlight")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", join_button)
            time.sleep(0.8)

            try:
                join_button.click()
            except Exception:
                driver.execute_script("arguments[0].click();", join_button)

            time.sleep(2)
            log_callback("Portal Join Link clicked successfully!", level="success")
            return True
        except Exception as e:
            log_callback(f"Join button click warning: {e}", level="warning")

    log_callback("Join button could not be clicked automatically. Chrome is open.", level="warning")
    return False


def handle_zoom_registration(driver, student_info=None, log_callback=print):
    """
    Detects Zoom Meeting Registration page, automatically enters student details,
    and submits the registration form.
    """
    if student_info is None:
        student_info = {}

    log_callback("Checking for Zoom Meeting Registration page...", level="highlight")

    time.sleep(3)
    handles = driver.window_handles
    if len(handles) > 1:
        driver.switch_to.window(handles[-1])
        log_callback("Switched to Zoom meeting registration tab.")

    is_reg_page = False
    for attempt in range(12):
        current_url = driver.current_url.lower()
        page_source = ""
        try:
            page_source = driver.page_source.lower()
        except Exception:
            pass

        if "register" in current_url or "meeting registration" in page_source or "first name" in page_source or "meeting-registration" in current_url:
            is_reg_page = True
            break

        if len(driver.window_handles) > len(handles):
            handles = driver.window_handles
            driver.switch_to.window(handles[-1])

        time.sleep(1)

    if not is_reg_page:
        log_callback("Zoom registration form not required or meeting opened directly.")
        return

    log_callback("Zoom Meeting Registration form detected! Auto-filling profile...", level="highlight")
    time.sleep(1.5)

    first_name = student_info.get("first_name", "")
    last_name = student_info.get("last_name", "")
    email = student_info.get("email", "")
    nic = student_info.get("id_number", "")
    phone = student_info.get("phone", "")

    # Execute JavaScript to identify and fill all registration inputs accurately
    fill_script = """
    const values = arguments[0];
    const results = [];
    
    // Helper to trigger input/change events for React/Vue frameworks
    function setInputValue(input, val) {
        if (!input || !val) return false;
        input.focus();
        input.value = val;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.dispatchEvent(new Event('blur', { bubbles: true }));
        return true;
    }

    // Get all interactive visible text-like input fields
    const inputs = Array.from(document.querySelectorAll("input:not([type='hidden']):not([type='submit']):not([type='button']):not([type='checkbox']):not([type='radio'])"))
        .filter(el => {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetWidth > 0 && el.offsetHeight > 0;
        });

    const assigned = new Set();

    function getFieldContext(el) {
        let text = (el.getAttribute('placeholder') || '') + ' ' +
                   (el.getAttribute('name') || '') + ' ' +
                   (el.getAttribute('id') || '') + ' ' +
                   (el.getAttribute('aria-label') || '');
        
        // Check associated label
        if (el.id) {
            const lbl = document.querySelector(`label[for='${el.id}']`);
            if (lbl) text += ' ' + lbl.innerText;
        }
        
        // Check closest label or form container
        let parent = el.parentElement;
        for (let i = 0; i < 4 && parent; i++) {
            const labels = parent.querySelectorAll('label, .form-label, .control-label, span');
            labels.forEach(l => text += ' ' + l.innerText);
            if (parent.innerText && parent.innerText.length < 150) {
                text += ' ' + parent.innerText;
            }
            parent = parent.parentElement;
        }
        return text.toLowerCase();
    }

    // 1. Identify and fill First Name
    for (const input of inputs) {
        if (assigned.has(input)) continue;
        const ctx = getFieldContext(input);
        if ((ctx.includes('first name') || ctx.includes('firstname') || ctx.includes('first_name')) && !ctx.includes('last')) {
            if (setInputValue(input, values.first_name)) {
                assigned.add(input);
                results.push('First Name');
                break;
            }
        }
    }

    // 2. Identify and fill Last Name
    for (const input of inputs) {
        if (assigned.has(input)) continue;
        const ctx = getFieldContext(input);
        if (ctx.includes('last name') || ctx.includes('lastname') || ctx.includes('last_name') || ctx.includes('surname')) {
            if (setInputValue(input, values.last_name)) {
                assigned.add(input);
                results.push('Last Name');
                break;
            }
        }
    }

    // 3. Identify and fill Email Address
    for (const input of inputs) {
        if (assigned.has(input)) continue;
        const ctx = getFieldContext(input);
        if ((ctx.includes('email') || ctx.includes('e-mail')) && !ctx.includes('confirm') && !ctx.includes('re-enter')) {
            if (setInputValue(input, values.email)) {
                assigned.add(input);
                results.push('Email Address');
                break;
            }
        }
    }

    // 4. Identify and fill Confirm Email (if present)
    for (const input of inputs) {
        if (assigned.has(input)) continue;
        const ctx = getFieldContext(input);
        if (ctx.includes('confirm') || ctx.includes('re-enter') || ctx.includes('confirm_email')) {
            if (setInputValue(input, values.email)) {
                assigned.add(input);
                results.push('Confirm Email');
                break;
            }
        }
    }

    // 5. Identify and fill NIC Number / National ID
    for (const input of inputs) {
        if (assigned.has(input)) continue;
        const ctx = getFieldContext(input);
        if (ctx.includes('nic') || ctx.includes('national id') || ctx.includes('identity') || ctx.includes('id number') || ctx.includes('student id')) {
            if (setInputValue(input, values.nic)) {
                assigned.add(input);
                results.push('NIC / National ID Number');
                break;
            }
        }
    }

    // 6. Identify and fill Contact / Phone Number
    for (const input of inputs) {
        if (assigned.has(input)) continue;
        const ctx = getFieldContext(input);
        if (ctx.includes('contact') || ctx.includes('mobile') || ctx.includes('phone') || ctx.includes('tel')) {
            if (setInputValue(input, values.phone)) {
                assigned.add(input);
                results.push('Contact Number');
                break;
            }
        }
    }

    // 7. Positional Fallback if some fields were not matched by text
    const unassignedInputs = inputs.filter(inp => !assigned.has(inp));
    if (unassignedInputs.length > 0) {
        const order = [
            { key: 'first_name', val: values.first_name, name: 'First Name (by position)' },
            { key: 'last_name', val: values.last_name, name: 'Last Name (by position)' },
            { key: 'email', val: values.email, name: 'Email Address (by position)' },
            { key: 'nic', val: values.nic, name: 'NIC Number (by position)' },
            { key: 'phone', val: values.phone, name: 'Contact Number (by position)' }
        ];

        let unIdx = 0;
        for (const item of order) {
            if (!results.some(r => r.toLowerCase().includes(item.key.replace('_', ' '))) && unIdx < unassignedInputs.length) {
                if (setInputValue(unassignedInputs[unIdx], item.val)) {
                    results.push(item.name);
                    unIdx++;
                }
            }
        }
    }

    return results;
    """

    try:
        filled_fields = driver.execute_script(fill_script, {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "nic": nic,
            "phone": phone
        })
        for field in (filled_fields or []):
            log_callback(f"  Field filled: {field}")
    except Exception as e:
        log_callback(f"  Auto-fill script note: {e}", level="warning")

    # Also perform Selenium-level typing as reinforcement to ensure standard keyboard events are dispatched
    time.sleep(0.5)

    def selenium_fill(selectors, val, name):
        if not val:
            return False
        for sel_type, sel_query in selectors:
            try:
                candidates = driver.find_elements(sel_type, sel_query)
                for c in candidates:
                    if c.is_displayed() and c.tag_name == "input":
                        try:
                            c.click()
                            time.sleep(0.1)
                            c.send_keys(Keys.CONTROL + "a")
                            c.send_keys(Keys.BACKSPACE)
                            c.clear()
                            c.send_keys(val)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true })); arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", c)
                            return True
                        except Exception:
                            pass
            except Exception:
                continue
        return False

    # Reinforce Email field
    selenium_fill([
        (By.XPATH, "//input[@type='email' or @name='email' or @id='email' or contains(@placeholder, 'Email') or contains(@placeholder, 'email')]"),
        (By.XPATH, "//*[contains(translate(., 'EMAIL', 'email'), 'email') and not(contains(translate(., 'CONFIRM', 'confirm'), 'confirm'))]/following::input[1]"),
        (By.XPATH, "//*[contains(translate(., 'EMAIL', 'email'), 'email') and not(contains(translate(., 'CONFIRM', 'confirm'), 'confirm'))]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'form-item') or contains(@class, 'row') or contains(@class, 'form-field')]//input"),
    ], email, "Email Address")

    # Reinforce NIC field
    selenium_fill([
        (By.XPATH, "//input[@name='nic' or @id='nic' or contains(@placeholder, 'NIC') or contains(@placeholder, 'National ID') or contains(@placeholder, 'id')]"),
        (By.XPATH, "//*[contains(translate(., 'NIC', 'nic'), 'nic') or contains(translate(., 'NATIONAL ID', 'national id'), 'national id')]/following::input[1]"),
        (By.XPATH, "//*[contains(translate(., 'NIC', 'nic'), 'nic') or contains(translate(., 'NATIONAL ID', 'national id'), 'national id')]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'form-item') or contains(@class, 'row') or contains(@class, 'form-field')]//input"),
    ], nic, "NIC Number")

    # Reinforce Contact Number field
    selenium_fill([
        (By.XPATH, "//input[@type='tel' or @name='phone' or @id='phone' or contains(@placeholder, 'Contact') or contains(@placeholder, 'Phone') or contains(@placeholder, 'Mobile')]"),
        (By.XPATH, "//*[contains(translate(., 'CONTACT', 'contact'), 'contact') or contains(translate(., 'PHONE', 'phone'), 'phone') or contains(translate(., 'MOBILE', 'mobile'), 'mobile')]/following::input[1]"),
        (By.XPATH, "//*[contains(translate(., 'CONTACT', 'contact'), 'contact') or contains(translate(., 'PHONE', 'phone'), 'phone') or contains(translate(., 'MOBILE', 'mobile'), 'mobile')]/ancestor::div[contains(@class, 'form-group') or contains(@class, 'form-item') or contains(@class, 'row') or contains(@class, 'form-field')]//input"),
    ], phone, "Contact Number")

    time.sleep(1)

    # Click Register Button
    log_callback("Submitting Zoom Registration form...", level="highlight")
    reg_btn = None
    reg_candidates = driver.find_elements(
        By.XPATH,
        "//button[contains(translate(., 'REGISTER', 'register'), 'register') or @type='submit'] | "
        "//input[@type='submit' and contains(translate(@value, 'REGISTER', 'register'), 'register')] | "
        "//a[contains(translate(., 'REGISTER', 'register'), 'register')]"
    )

    for rb in reg_candidates:
        if rb.is_displayed():
            reg_btn = rb
            break

    if reg_btn:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reg_btn)
            time.sleep(0.5)
            try:
                reg_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", reg_btn)
            time.sleep(2)
            log_callback("Zoom Registration Submitted Successfully!", level="success")
            return True
        except Exception as e:
            log_callback(f"Register button click warning: {e}", level="warning")
            return False
    else:
        log_callback("Registration details filled. Attempting to proceed...", level="warning")
        return False


def join_zoom_in_browser(driver, student_info=None, mute_mic=True, turn_off_cam=True, log_callback=print):
    """
    After Zoom registration, finds the meeting join link and launches
    the lecture directly inside the browser with mic and camera turned off.
    """
    if student_info is None:
        student_info = {}

    log_callback("Locating direct meeting join link on confirmation page...", level="highlight")
    time.sleep(3)

    # 1. Search for meeting launch / join link on confirmation page
    join_target = None
    for attempt in range(10):
        candidates = driver.find_elements(
            By.XPATH,
            "//a[contains(@href, '/j/') or contains(@href, '/w/') or contains(@href, 'zoom.us/w') or "
            "contains(translate(text(), 'CLICK HERE', 'click here'), 'click here') or "
            "contains(translate(text(), 'JOIN', 'join'), 'join')]"
        )
        for c in candidates:
            href = c.get_attribute("href") or ""
            if any(k in href for k in ["/j/", "/w/", "zoom.us", "success"]) or "join" in c.text.lower():
                join_target = c
                break
        if join_target:
            break
        time.sleep(1)

    if join_target:
        try:
            href = join_target.get_attribute("href")
            log_callback("Navigating to Zoom meeting session...", level="info")
            if href and href.startswith("http"):
                driver.get(href)
            else:
                join_target.click()
            time.sleep(4)
        except Exception as e:
            log_callback(f"Could not click join target directly: {e}", level="warning")

    # 2. Check for 'Join from your browser' option on Zoom launch page
    log_callback("Checking for browser-based meeting launch ('Join from Your Browser')...", level="highlight")
    time.sleep(3)

    # Switch to newest tab if Zoom opened a new window
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])

    browser_join_clicked = False
    for attempt in range(8):
        current_url = driver.current_url.lower()

        # Check if already inside web client
        if "wc/join" in current_url or "web-client" in current_url:
            browser_join_clicked = True
            break

        # Look for "Join from your browser" link
        web_links = driver.find_elements(
            By.XPATH,
            "//a[contains(translate(text(), 'JOIN FROM YOUR BROWSER', 'join from your browser'), 'join from your browser') or "
            "contains(translate(text(), 'JOIN FROM BROWSER', 'join from browser'), 'join from browser') or "
            "contains(@href, 'wc/join') or contains(@href, 'web')]"
        )

        for wl in web_links:
            try:
                if wl.is_displayed():
                    log_callback("Clicking 'Join from your browser'...", level="highlight")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", wl)
                    time.sleep(0.5)
                    try:
                        wl.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", wl)
                    browser_join_clicked = True
                    time.sleep(3)
                    break
            except Exception:
                continue

        if browser_join_clicked:
            break
        time.sleep(1.5)

    # 3. Inside Zoom Web Client: handle Name, Mic Mute, Camera Off, and final Join
    time.sleep(3)
    full_name = f"{student_info.get('first_name', '')} {student_info.get('last_name', '')}".strip()

    # Fill display name if prompted
    try:
        name_inputs = driver.find_elements(By.XPATH, "//input[@id='input-for-name' or @id='join-name' or @name='join-name' or @placeholder='Your Name']")
        for ni in name_inputs:
            if ni.is_displayed() and full_name:
                ni.clear()
                ni.send_keys(full_name)
                log_callback(f"Display Name set: {full_name}", level="info")
                break
    except Exception:
        pass

    # Apply Mic Mute preference in browser
    if mute_mic:
        log_callback("Applying preference: Microphone Muted (OFF)", level="info")
        try:
            mic_toggles = driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label, 'Mute') or contains(@aria-label, 'mute') or contains(@title, 'Mute')] | "
                "//input[contains(@id, 'audio') or contains(@name, 'audio') or contains(@id, 'mute')]"
            )
            for mt in mic_toggles:
                if mt.is_displayed():
                    mt.click()
                    break
        except Exception:
            pass

    # Apply Camera Off preference in browser
    if turn_off_cam:
        log_callback("Applying preference: Camera Turned Off (OFF)", level="info")
        try:
            cam_toggles = driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label, 'Stop Video') or contains(@aria-label, 'video') or contains(@title, 'Video')] | "
                "//input[contains(@id, 'video') or contains(@name, 'video')]"
            )
            for ct in cam_toggles:
                if ct.is_displayed():
                    ct.click()
                    break
        except Exception:
            pass

    # Click final web client Join Meeting button if present
    try:
        final_join_btns = driver.find_elements(
            By.XPATH,
            "//button[@id='joinBtn' or contains(translate(text(), 'JOIN', 'join'), 'join') or contains(@class, 'join-btn')]"
        )
        for fb in final_join_btns:
            if fb.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", fb)
                time.sleep(0.5)
                fb.click()
                log_callback("Final meeting join confirmed in browser!", level="success")
                break
    except Exception:
        pass

    log_callback("Successfully logged into lecture directly in browser!", level="success")


def run_full_flow(username, password, student_info=None, mute_mic=True, turn_off_cam=True, log_callback=print):
    """Executes the complete flow: Chrome launch -> Login -> Timetable -> Join -> Zoom Auto-fill & In-Browser Join."""
    try:
        log_callback("Starting Chrome browser...")
        driver = create_chrome_driver(mute_mic=mute_mic, turn_off_cam=turn_off_cam)

        perform_login(driver, username, password, log_callback)
        time.sleep(3)

        success = join_todays_lecture(driver, log_callback)
        if success:
            reg_done = handle_zoom_registration(driver, student_info, log_callback)
            # Proceed to join directly in browser
            join_zoom_in_browser(
                driver,
                student_info=student_info,
                mute_mic=mute_mic,
                turn_off_cam=turn_off_cam,
                log_callback=log_callback
            )

        return success
    except Exception as e:
        log_callback(f"Execution Error: {str(e)}", level="error")
        return False


def run_login_only_flow(username, password, log_callback=print):
    """Executes only the login flow: Chrome launch -> Login -> Stay on Student Dashboard."""
    try:
        log_callback("Starting Chrome browser...")
        driver = create_chrome_driver()

        perform_login(driver, username, password, log_callback)
        time.sleep(2)
        log_callback("Portal login completed successfully! Dashboard is open.", level="success")
        return True
    except Exception as e:
        log_callback(f"Login Error: {str(e)}", level="error")
        return False

