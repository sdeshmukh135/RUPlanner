import login_with_selenium as login
from scrape_services import semester_code, webreg_schedule, convert_webreg_json_to_ics

usernames = ["am3606", "yc1376"]
semesters = ["Spring 2025", "Summer 2025", "Fall 2025"]

def main():
    # For each username and semester, scrape the webreg schedule and convert it to ics
    for username in usernames:
        for semester in semesters:
            # Scrape webreg schedule to JSON file
            login.scrape(webreg_schedule, username=username, semester=semester, log=True)
            # Generate ICS based on semester string only
            convert_webreg_json_to_ics(f"{username}/{semester_code(semester)}_schedule.json",
                f"{username}/{semester_code(semester)}_schedule.ics")

if __name__ == "__main__":
    main()

# RUN python3 driver.py in the console