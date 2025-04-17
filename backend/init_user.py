from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import sys

# Add RUPlanner (parent of backend/) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers import authenticate as auth
from scrapers.webreg import semester_code, webreg_schedule, convert_webreg_json_to_ics
from scrapers.academic_calendar import scrape_academic_calendar

# Load env and connect to MongoDB
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["authndb"]
users = db["users"]

# If no academic_calendar.json exists, scrape it and create one
if not os.path.exists("./scrapers/academic_calendar.json"):
    scrape_academic_calendar(log=True)

def create_user(user_profile, log=False):
    """
    Creates a new user record in the MongoDB 'users' collection if the user
    does not already exist.

    This function checks for the existence of a user by their 'netid' in the
    'rumad' database. If no record is found, it inserts a new user document
    with default values, including a placeholder password hash, empty schedule
    fields, and an empty friends mapping.

    Args:
        user_profile : Dictionary containing Rutgers student user information,
        expected to contain a 'netid' key.

    Notes:
    - This function is intended to be called when a user logs in for the first time.
    - Be sure to replace the placeholder password before enabling production use.
    """

    netid = user_profile.get("netid")
    if netid and not users.find_one({"netid": netid}):
        if log: print(f"[MongoDB] Creating new user record for {netid}")
        users.insert_one({
            "netid": netid,
            "password_hash": generate_password_hash("placeholder123"),  # TODO: Replace securely later
            "current_schedule": "",
            "past_schedules": [],
            "prompt_history": [],
            "friends": {}  # maps friend's netid -> latest .ics string
        })
    return user_profile

# Save the ICS string to MongoDB under current_schedule
def save_ics_to_user(netid, ics_path):
    with open(ics_path, "r") as f:
        ics_data = f.read()
    users.update_one({"netid": netid}, {"$set": {"current_schedule": ics_data}})
    print(f"[MongoDB] Updated current_schedule for {netid}")

# Initialize a user and their preliminary schedule given their username
def init_user(username, semesters=["Fall 2025"]):
    # Initialize a new user in the MongoDB database
    user_profile = auth.scrape(auth.get_user_cas_data, username=username, log=True)
    if not user_profile:
        print("Something went wrong. Try again.")
        return
    create_user(user_profile)

    # Scrape the schedule for each semester
    for semester in semesters:
        print(f"\n>>> Scraping {username} for {semester}...")
        
        # 1. Scrape WebReg and save JSON
        schedule = auth.scrape(webreg_schedule, username=username, semester=semester, log=True, save=True)
        if not schedule: continue  # skip if no schedule JSON was generated

        # 2. Convert JSON to ICS
        ics_path = f"./.users/{username}/{semester_code(semester)}_schedule.ics"
        convert_webreg_json_to_ics(schedule, ics_path)

        # 3. Save ICS to MongoDB
        save_ics_to_user(username, ics_path)

# List of usernames + semesters to scrape and store
usernames = ["am3606"]
semesters = ["Winter 2025", "Spring 2025", "Summer 2025", "Fall 2025"]

def main():
    for username in usernames:
        init_user(username, semesters)

if __name__ == "__main__":
    main()
