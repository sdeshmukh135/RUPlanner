import login_with_selenium as login
from scrape_services import semester_code, webreg_schedule, convert_webreg_json_to_ics
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load env and connect to MongoDB
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["authndb"]
users = db["users"]

# Save the ICS string to MongoDB under current_schedule
def save_ics_to_user(netid, ics_path):
    with open(ics_path, "r") as f:
        ics_data = f.read()
    users.update_one({"netid": netid}, {"$set": {"current_schedule": ics_data}})
    print(f"[MongoDB] Updated current_schedule for {netid}")

# ✅ List of usernames + semesters to scrape and store
usernames = ["am3606", "yc1376"]
semesters = ["Spring 2025", "Summer 2025", "Fall 2025"]

def main():
    for username in usernames:
        for semester in semesters:
            print(f"\n>>> Scraping {username} for {semester}...")
            
            # 1. Scrape WebReg and save JSON
            login.scrape(webreg_schedule, username=username, semester=semester, log=True)
            
            # 2. Convert JSON to ICS
            json_path = f"{username}/{semester_code(semester)}_schedule.json"
            ics_path = f"{username}/{semester_code(semester)}_schedule.ics"
            convert_webreg_json_to_ics(json_path, ics_path)

            # 3. Save ICS to MongoDB
            save_ics_to_user(username, ics_path)

if __name__ == "__main__":
    main()
