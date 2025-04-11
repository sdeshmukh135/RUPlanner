from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time as time_module
import json
import re
import os
import login_with_selenium as login
from ics import Calendar, Event
from ics.grammar.parse import ContentLine
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

# Load academic calendar data
with open("academic_calendar.json") as f:
    ACADEMIC_CALENDAR = json.load(f)

# Define semester code
def semester_code(semester):
    """ Converts a semester string like 'Fall 2025' to its Rutgers semester code (e.g., '92025'). """
    term_map = {"Winter": "0", "Spring": "1", "Summer": "7", "Fall": "9"}
    term, year = semester.strip().title().split()
    if term not in term_map:
        raise ValueError(f"Unknown semester term: {term}")
    return term_map[term] + year

def time_to_minutes(t):
    """Converts a time string like '10:20 AM' to minutes after midnight."""
    dt = datetime.strptime(t, '%I:%M %p')
    return dt.hour * 60 + dt.minute

def select_webreg_semester(driver, semester):
    """
    Selects the appropriate semester radio button in WebReg based on visible semester text.

    Args:
        driver (webdriver.Chrome): Selenium WebDriver instance.
        semester (str): Semester name (e.g., "Fall 2025").

    Raises:
        ValueError: If the semester name is not found in the list.
    """
    target = semester.strip().lower()

    # Find all list items in the semester selection list
    list_items = driver.find_elements(By.CSS_SELECTOR, "ul.choose li")

    for li in list_items:
        label_text = li.text.strip().lower()
        if label_text == target:
            # Click the corresponding input element
            input_element = li.find_element(By.TAG_NAME, "input")
            input_element.click()
            return
    print("Success")
    raise ValueError(f"Semester '{semester}' not found in the semester selection list.")

def webreg_schedule_view_table(driver, username, semester="Fall 2025", log=False):
    """
    Scrapes a user's Rutgers WebReg schedule and saves it to a JSON file with semester metadata.

    Parameters:
    - driver: Selenium WebDriver instance.
    - username (str): NetID username.
    - semester (str): Semester to scrape (default: "Fall 2025").
    - log (bool): If True, prints debug output.

    Returns:
    - dict: Schedule including courses and semester metadata.
    """
    # Navigate to semester selection page
    driver.get("https://sims.rutgers.edu/webreg/chooseSemester.htm?login=cas")

    # Select the specified semester
    try:
        select_webreg_semester(driver, semester)
    except ValueError:
        return None  # Exit if semester selection fails
    driver.find_element(By.CLASS_NAME, "btn-submit").click()

    # Wait until the <h2> element is present and visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h2")))
    driver.get("https://sims.rutgers.edu/webreg/viewScheduleByCourse.htm")

    # Extract semester from page header
    h2_text = driver.find_element(By.CSS_SELECTOR, "h2").text.strip()
    semester_text = h2_text.split("»")[-1].strip()  # e.g., "Fall 2025"

    # Locate all course blocks within the new HTML structure
    course_blocks = driver.find_elements(By.CSS_SELECTOR, "div.list-course table tbody")
    courses = []

    for course_block in course_blocks:
        # Get the header row (first <tr>) containing course title and details
        header_tr = course_block.find_element(By.TAG_NAME, "tr")
        th = header_tr.find_element(By.TAG_NAME, "th")

        # Extract course title using JavaScript to get text before the <span>
        title = driver.execute_script("return arguments[0].childNodes[0].nodeValue", th).strip()

        # Extract course number, section, and index from the <span>
        span = th.find_element(By.TAG_NAME, "span")
        span_text = span.text.strip()  # e.g., "(01:198:461) Section 03 | [22508]"

        # Use regex to parse span text
        number_match = re.search(r'\((\d{2}:\d{3}:\d{3})\)', span_text)
        section_match = re.search(r'Section (\d+)', span_text)
        index_match = re.search(r'\[(\d{5})\]', span_text)

        course_number = number_match.group(1) if number_match else ''
        section_number = section_match.group(1) if section_match else ''
        index = index_match.group(1) if index_match else ''
        credits = 0.0  # TODO: Update if credits are available elsewhere on the page

        # Initialize list of meeting times
        meeting_trs = course_block.find_elements(By.TAG_NAME, "tr")[1:]
        meeting_times = []

        # Check for special cases (asynchronous/arranged courses)
        text_blob = course_block.text.lower()
        if "asynchronous" in text_blob or "hours by arrangement" in text_blob:
            pass  # Leave meeting_times as an empty list
        else:
            # Parse meeting times from all <tr> elements after the header
            for m in meeting_trs:
                tds = m.find_elements(By.TAG_NAME, "td")
                if len(tds) == 4:
                    day = tds[0].text.strip()
                    time_str = tds[1].text.strip()

                    if " - " not in time_str:
                        if log:
                            print(f"[WARN] Malformed time string in {title}: '{time_str}'")
                        continue

                    start_str, end_str = time_str.split(" - ")
                    start = time_to_minutes(start_str.strip())
                    end = time_to_minutes(end_str.strip())

                    try:
                        building = tds[2].find_element(By.TAG_NAME, "a").text.strip()
                    except:
                        building = ""

                    campus = tds[3].text.strip()

                    meeting_times.append({
                        "day": day,
                        "range": (start, end),
                        "building": building,
                        "campus": campus
                    })

        # Compile course details into dictionary
        courses.append({
            "title": title,
            "course_number": course_number,
            "section_number": section_number,
            "index": index,
            "credits": credits,
            "meeting_times": meeting_times
        })

    # Construct schedule data
    schedule_data = {
        "semester": semester_text,
        "courses": courses
    }

    # Save to JSON file
    json_filename = f"{username}/{semester_code(semester)}_schedule.json"
    with open(json_filename, "w") as f:
        json.dump(schedule_data, f, indent=2)
    if log: print(f"Saved schedule to {json_filename}.")

    return schedule_data

def get_current_semester(driver, log=False):
    user_profile = login.get_user_cas_data(driver, log)
    if log: print(user_profile)

    driver.get("https://sims.rutgers.edu/webreg/chooseSemester.htm?login=cas")
    driver.find_element(By.CLASS_NAME, "btn-submit").click()
    
    # Wait until the <h2> element is present and visible
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h2")))
    # Extract semester title from page
    h2_text = driver.find_element(By.CSS_SELECTOR, "h2").text.strip()
    semester_text = h2_text.split("»")[-1].strip()  # e.g., "Fall 2025"
    return semester_text

def webreg_schedule_register_table(driver, username, semester, log=False):
    """
    Scrapes a user's Rutgers WebReg schedule and saves it to a JSON file with semester metadata.

    Parameters:
    - driver: Selenium WebDriver instance.
    - username (str): NetID username.
    - log (bool): If True, prints debug output.

    Returns:
    - dict: Schedule including courses and semester metadata.
    """
    # Locate all course blocks on the page
    course_blocks = driver.find_elements(By.CSS_SELECTOR, "dl.courses")
    courses = []

    for course in course_blocks:
        # Extract header and body HTML
        header = course.find_element(By.TAG_NAME, "dt").text
        body = course.find_element(By.TAG_NAME, "dd")

        # Extract title, course number, section, index, credits using regex
        title_match = re.search(r'\b([A-Z].*?)\s+\(', header)
        number_match = re.search(r'\((\d{2}:\d{3}:\d{3})\)', header)
        section_match = re.search(r'Section (\d+)', header)
        index_match = re.search(r'\[(\d{5})\]', header)
        credit_match = re.search(r'Credits:\s*([\d.]+)', header)

        title = title_match.group(1) if title_match else ''
        course_number = number_match.group(1) if number_match else ''
        section_number = section_match.group(1) if section_match else ''
        index = index_match.group(1) if index_match else ''
        credits = float(credit_match.group(1)) if credit_match else 0.0

        # Initialize list of meeting times
        meeting_divs = body.find_elements(By.CSS_SELECTOR, ".meeting2")
        meeting_times = []

        # Check for special cases (asynchronous/arranged courses)
        text_blob = body.text.lower()
        if "asynchronous" in text_blob or "hours by arrangement" in text_blob:
            pass  # Leave meeting_times as an empty list
        else:
            # Parse all meeting times
            for m in meeting_divs:
                day = m.find_element(By.CLASS_NAME, "dayname3").text
                time_str = m.find_element(By.CLASS_NAME, "timestring3").text

                if " - " not in time_str:
                    if log:
                        print(f"[WARN] Malformed time string in {title}: '{time_str}'")
                    continue

                start_str, end_str = time_str.split(" - ")
                start = time_to_minutes(start_str.strip())
                end = time_to_minutes(end_str.strip())

                try:
                    building = m.find_element(By.CLASS_NAME, "buildingroom3").text.strip()
                except:
                    building = ""

                campus = m.find_element(By.CLASS_NAME, "campus3").text.strip()

                meeting_times.append({
                    "day": day,
                    "range": (start, end),
                    "building": building,
                    "campus": campus
                })

        # Compile course details into dictionary
        courses.append({
            "title": title,
            "course_number": course_number,
            "section_number": section_number,
            "index": index,
            "credits": credits,
            "meeting_times": meeting_times
        })

    # Construct schedule data
    schedule_data = {
        "semester": semester,
        "courses": courses
    }

    # Save to JSON file
    json_filename = f"{username}/{semester_code(semester)}_schedule.json"
    with open(json_filename, "w") as f:
        json.dump(schedule_data, f, indent=2)
    if log: print(f"Saved schedule to {json_filename}.")

    return schedule_data

def webreg_schedule(driver, username, semester="Fall 2025", log=False):
    semester_text = get_current_semester(driver, log=False)
    schedule_data = {}  # empty JSON object
    if semester_text == semester:  # current semester matches
        schedule_data = webreg_schedule_register_table(driver, username, semester, log=log)
    else:  # assuming the semester matches "Fall 2025" format
        schedule_data = webreg_schedule_view_table(driver, username, semester, log=log)
    return schedule_data



def minutes_to_time(minutes):
    """Converts minutes after midnight to a datetime.time object."""
    return (datetime.min + timedelta(minutes=minutes)).time()

def next_weekday(start_date, target_weekday):
    """Finds the next date from start_date that falls on the target_weekday."""
    days_ahead = (target_weekday - start_date.weekday() + 7) % 7
    return start_date + timedelta(days=days_ahead)

def generate_vtimezone_block():
    """Generates a VTIMEZONE block for America/New_York to handle DST transitions."""
    return (
        "BEGIN:VTIMEZONE\n"
        "TZID:America/New_York\n"
        "X-LIC-LOCATION:America/New_York\n"
        "BEGIN:DAYLIGHT\n"
        "TZOFFSETFROM:-0500\n"
        "TZOFFSETTO:-0400\n"
        "TZNAME:EDT\n"
        "DTSTART:19700308T020000\n"
        "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU\n"
        "END:DAYLIGHT\n"
        "BEGIN:STANDARD\n"
        "TZOFFSETFROM:-0400\n"
        "TZOFFSETTO:-0500\n"
        "TZNAME:EST\n"
        "DTSTART:19701101T020000\n"
        "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU\n"
        "END:STANDARD\n"
        "END:VTIMEZONE\n"
    )

def convert_webreg_json_to_ics(json_path, ics_output_path):
    """
    Convert a Rutgers WebReg schedule JSON file into an iCalendar (.ics) file.

    This function reads a JSON file containing course schedule data, generates
    recurring events for each course meeting based on the semester start and end
    dates from academic_calendar.json, and excludes dates within recess periods.
    The resulting calendar is saved as an .ics file compatible with standard
    calendar applications.

    Args:
        json_path (str): Path to the input JSON file containing the WebReg schedule.
        ics_output_path (str): Path where the output .ics file will be saved.

    Raises:
        FileNotFoundError: If the JSON file at json_path does not exist.
        ValueError: If the semester specified in the JSON is not found in academic_calendar.json.
        json.JSONDecodeError: If the JSON file is malformed.

    Examples:
        >>> convert_webreg_json_to_ics(f"am3606_schedule.json", "am3606_schedule.ics")
        .ics calendar saved to: am3606_schedule.ics
    """
    from_zone = ZoneInfo("America/New_York")  # Use US Eastern Time for event times

    # Mapping of day strings to Python weekday integers
    DAY_TO_WEEKDAY = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }

    # Load the user's schedule JSON
    with open(json_path, "r") as f:
        schedule_data = json.load(f)

    semester = schedule_data.get("semester")
    calendar = Calendar()
    courses = schedule_data["courses"]

    # Get the start and end of the semester
    semester_info = ACADEMIC_CALENDAR.get(semester)
    if not semester_info:
        raise ValueError(f"Semester '{semester}' not found in academic calendar.")

    # Set semester start and end as timezone-aware dates
    semester_start = datetime.strptime(semester_info["start"], "%Y-%m-%d").replace(tzinfo=from_zone)
    semester_end = datetime.strptime(semester_info["end"], "%Y-%m-%d").replace(tzinfo=from_zone)

    # Define the semester end time in local time (23:59:59 America/New_York)
    # This ensures the RRULE UNTIL reflects the local end date, adjusting for DST
    until_dt_local = datetime.combine(semester_end.date(), time(23, 59, 59)).replace(tzinfo=from_zone)

    # Parse recesses as ranges of dates to exclude from recurring events
    skip_ranges = [
        (
            datetime.strptime(r["start"], "%Y-%m-%d").replace(tzinfo=from_zone),
            datetime.strptime(r["end"], "%Y-%m-%d").replace(tzinfo=from_zone)
        )
        for r in semester_info.get("recesses", [])
    ]

    # Loop through each course and its meeting times
    for course in courses:
        for meeting in course["meeting_times"]:
            weekday = DAY_TO_WEEKDAY[meeting["day"]]
            start_minutes, end_minutes = meeting["range"]
            start_time = minutes_to_time(start_minutes)
            end_time = minutes_to_time(end_minutes)

            # Find the first valid date on/after semester_start that matches the weekday
            first_date = next_weekday(semester_start, weekday)
            
            # Define start and end datetimes in local time with America/New_York timezone
            start_dt = datetime.combine(first_date.date(), start_time).replace(tzinfo=from_zone)
            end_dt = datetime.combine(first_date.date(), end_time).replace(tzinfo=from_zone)

            # Create an event object for the first occurrence of the course
            e = Event()
            e.name = f"{course['title']} ({course['course_number']})"
            # Explicitly set DTSTART and DTEND with TZID to ensure DST handling
            # Format: DTSTART;TZID=America/New_York:20250122T121000
            e.extra.append(ContentLine(
                name="DTSTART",
                params={"TZID": "America/New_York"},
                value=start_dt.strftime("%Y%m%dT%H%M%S")
            ))
            e.extra.append(ContentLine(
                name="DTEND",
                params={"TZID": "America/New_York"},
                value=end_dt.strftime("%Y%m%dT%H%M%S")
            ))
            e.location = f"{meeting['building']} ({meeting['campus']})" if meeting["building"] else meeting["campus"]
            e.description = f"Section {course['section_number']} | Index {course['index']} | Credits: {course['credits']}"

            # Add a weekly recurrence rule with UNTIL in local time, adjusted for DST
            # Since DTSTART uses TZID, UNTIL is in local time without Z suffix
            e.extra.append(ContentLine(
                name="RRULE",
                value=f"FREQ=WEEKLY;UNTIL={until_dt_local.strftime('%Y%m%dT%H%M%S')}"
            ))

            # Add EXDATEs to skip dates during semester recesses, in local time with TZID
            for skip_start, skip_end in skip_ranges:
                d = next_weekday(skip_start, weekday)
                while d <= skip_end:
                    skip_time = datetime.combine(d.date(), start_time).replace(tzinfo=from_zone)
                    e.extra.append(ContentLine(
                        name="EXDATE",
                        params={"TZID": "America/New_York"},
                        value=skip_time.strftime("%Y%m%dT%H%M%S")
                    ))
                    d += timedelta(days=7)

            # Add the event to the calendar
            calendar.events.add(e)

    # Write calendar with VTIMEZONE prepended manually
    ical_body = str(calendar)
    vtimezone = generate_vtimezone_block()
    ical_with_timezone = ical_body.replace("BEGIN:VEVENT", f"{vtimezone}BEGIN:VEVENT", 1)

    with open(ics_output_path, "w") as f:
        f.write(ical_with_timezone)

    print(f".ics calendar saved to: {ics_output_path}")
