# ✅ Updated schedule_utils.py (ICS-only backend logic)


from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from ics import Calendar, Event
from pymongo import MongoClient 
from flask_cors import CORS
import certifi
from pymongo.server_api import ServerApi


#load_dotenv()
#client = MongoClient(os.getenv("MONGO_URI"))
username = "sanikadeshmukh135"
password = "Snehnil16"
#uri = f'mongodb+srv://{username}:{password}@cluster1.jo3fsmz.mongodb.net/?retryWrites=true&w=majority'

url = 'mongodb+srv://' + username + ':' + password + '@' + 'cluster1.jo3fsmz.mongodb.net/?retryWrites=true&w=majority'
#&appName=Cluster1'
#'&tlsAllowInvalidCertificates=true'

client = MongoClient(url, tls=True, tlsCAFile=certifi.where(), server_api=ServerApi('1'))

db = client["authndb"]
users = db["users"]

# 🔍 Fetch user document from MongoDB by NetID
def get_user_by_netid(netid):
    return users.find_one({"netid": netid})

# 📝 Logs a user prompt and its Gemini response
def update_prompt_history(netid, prompt, response):
    users.update_one(
        {"netid": netid},
        {"$push": {
            "prompt_history": {
                "timestamp": datetime.utcnow(),
                "prompt": prompt,
                "response": response
            }
        }}
    )

# 🔄 Replaces the user's current working schedule (as ICS)
def update_current_schedule(netid, ics_schedule_str):
    users.update_one(
        {"netid": netid},
        {"$set": {"current_schedule": ics_schedule_str}}
    )

# 💾 Pushes old current_schedule to top of past_schedules list and clears current_schedule
def confirm_schedule_update(netid):
    user = get_user_by_netid(netid)
    current = user.get("current_schedule")
    if not current:
        return False

    users.update_one(
        {"netid": netid},
        {
            "$push": {
                "past_schedules": {
                    "$each": [current],
                    "$position": 0
                }
            },
            "$unset": {"current_schedule": ""}
        }
    )
    return True

# 🔄 Convert JSON-formatted list of schedule entries into a .ics calendar string
def convert_schedule_to_ics(schedule):
    calendar = Calendar()
    for entry in schedule:
        event = Event()
        event.name = entry.get("commitment", "Untitled")
        event.location = entry.get("location", "")
        event.begin = f"{entry['day']} {entry['start_time']}"
        event.end = f"{entry['day']} {entry['end_time']}"
        calendar.events.add(event)
    return str(calendar)

# ⚔️ Detect conflict between two events (same day, overlapping time)
def is_conflict(event1, event2):
    if event1["day"] != event2["day"]:
        return False

    s1 = datetime.strptime(event1["start_time"], "%H:%M")
    e1 = datetime.strptime(event1["end_time"], "%H:%M")
    s2 = datetime.strptime(event2["start_time"], "%H:%M")
    e2 = datetime.strptime(event2["end_time"], "%H:%M")
    return s1 < e2 and s2 < e1

# 🧹 Remove existing conflicting events before adding a new one
def remove_conflicts_from_schedule(existing_schedule, new_entry):
    return [event for event in existing_schedule if not is_conflict(event, new_entry)]

# 🔁 Process LLM entries: resolve conflicts, build .ics, update MongoDB
def merge_schedule(netid, incoming_entries):
    user = get_user_by_netid(netid)
    existing_schedule = user.get("current_schedule", "")

    # Start from scratch if there's no current_schedule
    parsed_schedule = []
    if existing_schedule:
        try:
            c = Calendar(existing_schedule)
            for e in c.events:
                parsed_schedule.append({
                    "commitment": e.name,
                    "day": e.begin.format("dddd"),
                    "start_time": e.begin.format("YYYY-MM-DD"),
                    "end_time": e.end.format("YYYY-MM-DD")
                })
        except:
            pass

    for new_entry in incoming_entries:
        parsed_schedule = remove_conflicts_from_schedule(parsed_schedule, new_entry)
        parsed_schedule.append(new_entry)

    ics_string = convert_schedule_to_ics(parsed_schedule)
    update_current_schedule(netid, ics_string)
    return ics_string

# 🔁 Updates a friend’s latest shared schedule as an ICS string
def update_friend_schedule(netid, friend_netid, ics_string):
    users.update_one(
        {"netid": netid},
        {"$set": {f"friends.{friend_netid}": ics_string}}
    )
