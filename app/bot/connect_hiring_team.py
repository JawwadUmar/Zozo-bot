import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

from app.config.config import CONNECTION_NOTE_TEMPLATE
from app.utils.human import human_delay, human_typing


HIRING_TEAM_MARKER = (
    "h2:has-text('hiring team'), "
    "h3:has-text('hiring team'), "
    "p:has-text('Meet the hiring team'), "
    ".job-details-people-who-can-help__section--two-pane, "
    ".hirer-card__hirer-information"
)
PROFILE_TOP_CARD = "main section:has(h1)"
TRACKER_PATH = Path(__file__).resolve().parents[2] / "data" / "job_applications.md"


def _clean_linkedin_url(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))


def _clean_profile_name(raw_name):
    if not raw_name:
        return "the hiring team"

    name = raw_name.strip()
    name = re.sub(r"^View\s+", "", name, flags=re.IGNORECASE)
    name = re.sub(r"['\u2019]s verified profile graphic$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"['\u2019]s profile graphic$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"['\u2019]s profile$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "the hiring team"


async def _safe_inner_text(locator, fallback=""):
    try:
        if await locator.count() > 0:
            text = await locator.first.inner_text(timeout=2000)
            return " ".join(text.split())
    except Exception:
        pass
    return fallback


def _is_generic_name(name):
    return not name or name == "the hiring team"


def _tracker_status(status):
    if status in {"Sent", "Pending"}:
        return "Sent"
    if status == "Already connected":
        return "Accepted"
    if status in {"Could not send", "Connect button not found", "Error"}:
        return "Not Available"
    return status or "Not Available"


def _insert_entry_under_date(text, date_heading, entry):
    heading = f"### {date_heading}"

    if heading not in text:
        return text.rstrip() + f"\n\n{heading}\n\n{entry.strip()}\n"

    section_start = text.index(heading)
    next_section_start = text.find("\n### ", section_start + len(heading))

    insertion = f"\n\n{entry.strip()}\n"
    if next_section_start == -1:
        return text.rstrip() + insertion

    return text[:next_section_start].rstrip() + insertion + "\n" + text[next_section_start:].lstrip()


def _record_hiring_team_outreach(job_title, company, job_url, member, status, note):
    profile_url = member["profile_url"]
    name = member["name"]
    today = datetime.now().strftime("%Y-%m-%d")

    TRACKER_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = TRACKER_PATH.read_text(encoding="utf-8") if TRACKER_PATH.exists() else "# LinkedIn Job Application Tracker\n"

    if profile_url in text and job_url in text:
        print(f"Zozo: Hiring-team tracker already has {name} for this job.")
        return

    entry = f"""
#### {company} - {job_title}

- Application date: {today}
- Company name: {company}
- Job title: {job_title}
- LinkedIn job post URL: {job_url}
- Recruiter/Hiring Manager name: {name}
- Recruiter LinkedIn profile URL: {profile_url}
- Connection request status: {_tracker_status(status)}
- Application status: Applied
- Source log: Zozo: Opening hiring team profile: {name} ({profile_url})
- Connection note:
  ```text
  {note}
  ```
- Next action: Follow up after the connection request is accepted.
- Notes: Captured automatically by Zozo from the LinkedIn "Meet the hiring team" section. Bot status: {status}.
"""

    updated = _insert_entry_under_date(text, today, entry)
    TRACKER_PATH.write_text(updated, encoding="utf-8")
    print(f"Zozo: Recorded hiring-team outreach in {TRACKER_PATH}.")


async def _get_current_job_context(page):
    job_title = await _safe_inner_text(
        page.locator(
            ".job-details-jobs-unified-top-card__job-title, "
            ".jobs-unified-top-card__job-title, "
            "h1:visible"
        ),
        "the role",
    )
    company = await _safe_inner_text(
        page.locator(
            ".job-details-jobs-unified-top-card__company-name a, "
            ".job-details-jobs-unified-top-card__company-name, "
            ".jobs-unified-top-card__company-name a, "
            ".jobs-unified-top-card__company-name"
        ),
        "your company",
    )
    return job_title, company


async def _bring_marker_into_view(marker):
    if await marker.count() == 0:
        return False
    try:
        await marker.scroll_into_view_if_needed(timeout=2000)
    except Exception:
        pass
    return True


async def _scroll_to_hiring_team(page):
    marker = page.locator(HIRING_TEAM_MARKER).first

    try:
        await marker.wait_for(state="attached", timeout=2500)
    except Exception:
        pass

    if await _bring_marker_into_view(marker):
        return True

    details_panes = page.locator(
        ".jobs-search__job-details--container:visible, "
        ".jobs-search__right-rail:visible, "
        ".jobs-details__main-content:visible, "
        ".scaffold-layout__detail:visible"
    )

    try:
        await details_panes.first.hover(timeout=2000)
    except Exception:
        pass

    for _ in range(10):
        for index in range(await details_panes.count()):
            try:
                await details_panes.nth(index).evaluate("(el) => el.scrollBy(0, 700)")
            except Exception:
                pass

        try:
            await page.mouse.wheel(0, 700)
        except Exception:
            pass

        await human_delay(0.4, 0.8)
        if await _bring_marker_into_view(marker):
            return True

    return False


async def _get_hiring_team_section(page):
    if not await _scroll_to_hiring_team(page):
        print("Zozo: 'Meet the hiring team' section not present on this job post.")
        return None

    marker = page.locator(HIRING_TEAM_MARKER).first
    section = marker.locator(
        "xpath=ancestor-or-self::*[(self::section or self::div) and .//a[contains(@href, '/in/')]][1]"
    ).first
    if await section.count() > 0:
        return section

    fallback = page.locator(
        ".job-details-people-who-can-help__section--two-pane:has(a[href*='/in/']), "
        "div:has(> p:has-text('Meet the hiring team')):has(a[href*='/in/']), "
        "section:has-text('hiring team'):has(a[href*='/in/']), "
        "div:has(> h2:has-text('hiring team')):has(a[href*='/in/']), "
        "div:has(> h3:has-text('hiring team')):has(a[href*='/in/'])"
    ).first
    if await fallback.count() > 0:
        return fallback

    print("Zozo: Found the hiring team section but no profile links inside it.")
    return None


async def _link_display_name(link):
    aria_label = await link.get_attribute("aria-label")
    if aria_label and aria_label.strip():
        return _clean_profile_name(aria_label)

    try:
        text = await link.inner_text(timeout=2000)
    except Exception:
        return "the hiring team"

    for line in text.splitlines():
        line = line.strip()
        if line:
            return _clean_profile_name(line)
    return "the hiring team"


async def _get_hiring_team_members(page):
    section = await _get_hiring_team_section(page)
    if section is None or await section.count() == 0:
        return []

    links = section.locator("a[href*='/in/']")
    members_by_url = {}

    for index in range(await links.count()):
        link = links.nth(index)
        href = await link.get_attribute("href")
        if not href:
            continue

        profile_url = _clean_linkedin_url(urljoin(page.url, href))
        name = await _link_display_name(link)

        existing = members_by_url.get(profile_url)
        if existing is None:
            members_by_url[profile_url] = {"name": name, "profile_url": profile_url}
        elif not _is_generic_name(name) and (
            _is_generic_name(existing["name"]) or len(name) < len(existing["name"])
        ):
            members_by_url[profile_url] = {"name": name, "profile_url": profile_url}

    return list(members_by_url.values())


async def _click_first(locator, timeout=3000, label="button"):
    try:
        await locator.first.wait_for(state="visible", timeout=timeout)
        await human_delay(1, 2)
        await locator.first.click()
        print(f"Zozo: Clicked {label}.")
        return True
    except Exception:
        return False


async def _js_click_profile_action(profile_page, action_text, exact=False):
    return await profile_page.evaluate(
        """
        ({ actionText, exact }) => {
            const wanted = actionText.toLowerCase();

            // Scope to the profile top card: climb from the h1 (person's name) to the
            // nearest container that holds action buttons. Never scan the whole page,
            // or we might click Connect/Follow for someone in the sidebar.
            let scope = document.querySelector('main h1');
            while (
                scope && scope !== document.body &&
                !scope.querySelector('button, [role="button"], a[href*="custom-invite"]')
            ) {
                scope = scope.parentElement;
            }
            if (!scope || scope === document.body) {
                scope = document.querySelector('main section:has(h1)') || document.querySelector('main') || document;
            }

            const candidates = [
                ...scope.querySelectorAll('button, [role="button"], a[href*="custom-invite"]'),
                ...document.querySelectorAll('[role="menuitem"]')
            ];

            const isVisible = (el) => {
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
            };

            const textFor = (el) => `${el.innerText || ''} ${el.getAttribute('aria-label') || ''}`.toLowerCase();
            const matches = (el) => exact
                ? (el.innerText || '').trim().toLowerCase() === wanted
                : textFor(el).includes(wanted);
            const target = candidates.find((el) => isVisible(el) && matches(el));
            if (!target) return false;

            target.click();
            return true;
        }
        """,
        {"actionText": action_text, "exact": exact},
    )


async def _has_connection_pending(profile_page):
    pending = profile_page.locator(
        f"{PROFILE_TOP_CARD} button:has-text('Pending'):visible, "
        f"{PROFILE_TOP_CARD} span:has-text('Pending'):visible, "
        f"{PROFILE_TOP_CARD} button[aria-label*='Pending' i]:visible"
    )
    return await pending.count() > 0


async def _is_already_connected(profile_page):
    # NOTE: a "Message" button is NOT proof of a connection anymore — LinkedIn's
    # new profile UI shows Message for 2nd/3rd degree profiles too. Only the
    # "1st" distance badge next to the name is reliable.
    connected = profile_page.locator(
        f"{PROFILE_TOP_CARD} span:has-text('1st'):visible, "
        f"{PROFILE_TOP_CARD} span:has-text('1st degree connection'):visible"
    )
    return await connected.count() > 0


async def _click_connect(profile_page):
    await profile_page.wait_for_load_state("domcontentloaded")

    if await _has_connection_pending(profile_page):
        return "already_pending"

    direct_connect = profile_page.locator(
        f"{PROFILE_TOP_CARD} button[aria-label*='Invite' i][aria-label*='connect' i]:visible, "
        f"{PROFILE_TOP_CARD} button:has-text('Connect'):visible, "
        f"{PROFILE_TOP_CARD} [role='button'][aria-label*='Connect' i]:visible, "
        f"{PROFILE_TOP_CARD} [role='button']:has-text('Connect'):visible, "
        f"{PROFILE_TOP_CARD} a[href*='custom-invite']:visible"
    )

    if await _click_first(direct_connect, timeout=6000, label="direct Connect"):
        return "connect_clicked"

    # New profile UI usually hides Connect inside the "More" dropdown.
    more_button = profile_page.locator(
        f"{PROFILE_TOP_CARD} button[aria-label*='More actions' i]:visible, "
        f"{PROFILE_TOP_CARD} button:has-text('More'):visible, "
        f"{PROFILE_TOP_CARD} [role='button'][aria-label*='More actions' i]:visible, "
        f"{PROFILE_TOP_CARD} [role='button']:has-text('More'):visible, "
        "main button:text-is('More'):visible, "
        "main [role='button']:text-is('More'):visible"
    )

    more_opened = await _click_first(more_button, timeout=5000, label="More actions")
    if not more_opened and await _js_click_profile_action(profile_page, "more", exact=True):
        print("Zozo: Opened More menu using fallback action scan.")
        more_opened = True

    if more_opened:
        await human_delay(1, 2)

        menu_connect = profile_page.locator(
            "[role='menuitem']:has-text('Connect'):visible, "
            "[role='menu'] a[href*='custom-invite']:visible, "
            "a[role='menuitem'][href*='custom-invite']:visible, "
            "div[aria-label*='Invite' i][aria-label*='connect' i]:visible, "
            "div[role='button']:has-text('Connect'):visible"
        )

        if await _click_first(menu_connect, timeout=5000, label="More menu Connect"):
            return "connect_clicked"

        if await _js_click_profile_action(profile_page, "connect"):
            print("Zozo: Clicked Connect from More menu using fallback action scan.")
            return "connect_clicked"

    if await _js_click_profile_action(profile_page, "connect"):
        print("Zozo: Clicked Connect using fallback profile action scan.")
        return "connect_clicked"

    if await _is_already_connected(profile_page):
        return "already_connected"
    return "not_found"


async def _send_connection_invite(profile_page, note):
    if await _has_connection_pending(profile_page):
        return True

    if note:
        add_note_button = profile_page.locator(
            "button:has-text('Add a note'):visible, "
            "button:has-text('Add note'):visible, "
            "button[aria-label*='Add a note' i]:visible"
        )

        try:
            await add_note_button.first.wait_for(state="visible", timeout=4000)
            await human_delay(1, 2)
            await add_note_button.first.click()

            note_input = profile_page.locator(
                "textarea[name='message']:visible, "
                "textarea#custom-message:visible, "
                "textarea:visible"
            ).first
            await note_input.wait_for(state="visible", timeout=5000)
            await note_input.click()
            await human_typing(note_input, note[:300])
        except Exception:
            print("Zozo: Could not add a connection note. Sending without a note if possible.")

    send_button = profile_page.locator(
        "button:has-text('Send invitation'):visible, "
        "button:has-text('Send now'):visible, "
        "button:has-text('Send without a note'):visible, "
        "button:has-text('Send without note'):visible, "
        "button[aria-label='Send now']:visible, "
        "button[aria-label*='Send' i]:visible, "
        "button:has-text('Send'):visible"
    )

    if await _click_first(send_button, timeout=6000, label="Send invitation"):
        await human_delay(1, 2)
        return True

    try:
        clicked = await profile_page.evaluate(
            """
            () => {
                const candidates = [...document.querySelectorAll('button, [role="button"]')];
                const isVisible = (el) => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return style.visibility !== 'hidden' && style.display !== 'none' && rect.width > 0 && rect.height > 0;
                };
                const target = candidates.find((el) => {
                    const label = `${el.innerText || ''} ${el.getAttribute('aria-label') || ''}`.toLowerCase();
                    return isVisible(el) && !el.disabled && /send( invitation| now| without|$)/.test(label);
                });
                if (!target) return false;
                target.click();
                return true;
            }
            """
        )
        if clicked:
            print("Zozo: Clicked Send invitation using fallback action scan.")
            await human_delay(1, 2)
            return True
    except Exception:
        pass

    if await _has_connection_pending(profile_page):
        return True

    return False


async def _follow_profile(profile_page, name):
    follow_button = profile_page.locator(
        f"{PROFILE_TOP_CARD} button:text-is('Follow'):visible, "
        f"{PROFILE_TOP_CARD} [role='button']:text-is('Follow'):visible"
    )

    if await _click_first(follow_button, timeout=3000, label="Follow"):
        print(f"Zozo: Now following {name}.")
        return True

    if await _js_click_profile_action(profile_page, "follow", exact=True):
        print(f"Zozo: Now following {name} (via fallback action scan).")
        return True

    print(f"Zozo: Follow button not shown for {name} (likely already following after connect).")
    return False


async def connect_to_hiring_team(page):
    members = await _get_hiring_team_members(page)
    if not members:
        print("Zozo: No hiring team profile found for this job.")
        return []

    print(f"Zozo: Found {len(members)} hiring team member(s): {', '.join(m['name'] for m in members)}")

    job_title, company = await _get_current_job_context(page)
    job_url = page.url
    results = []

    for member in members:
        name = member["name"]
        profile_url = member["profile_url"]
        note = CONNECTION_NOTE_TEMPLATE.format(
            name=name,
            job_title=job_title,
            company=company,
        )
        print(f"Zozo: Opening hiring team profile: {name} ({profile_url})")

        profile_page = await page.context.new_page()
        try:
            await profile_page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
            await human_delay(3, 5)

            connect_state = await _click_connect(profile_page)
            if connect_state == "already_pending":
                status = "Pending"
                print(f"Zozo: Connection request is already pending for {name}.")
                _record_hiring_team_outreach(job_title, company, job_url, member, status, note)
                results.append({**member, "status": status})
                continue

            if connect_state == "already_connected":
                status = "Already connected"
                print(f"Zozo: Already connected with {name}.")
                _record_hiring_team_outreach(job_title, company, job_url, member, status, note)
                results.append({**member, "status": status})
                continue

            if connect_state != "connect_clicked":
                status = "Connect button not found"
                print(f"Zozo: {status} for {name}.")
                _record_hiring_team_outreach(job_title, company, job_url, member, status, note)
                results.append({**member, "status": status})
                continue

            sent = await _send_connection_invite(profile_page, note)
            status = "Sent" if sent else "Could not send"
            print(f"Zozo: Connection request status for {name}: {status}")
            if sent:
                await _follow_profile(profile_page, name)
            _record_hiring_team_outreach(job_title, company, job_url, member, status, note)
            results.append({**member, "status": status})
        except Exception as exc:
            status = "Error"
            print(f"Zozo: Error connecting with {name}: {exc}")
            _record_hiring_team_outreach(job_title, company, job_url, member, status, note)
            results.append({**member, "status": status})
        finally:
            await human_delay(1, 2)
            await profile_page.close()

    return results
