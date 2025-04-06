#VERY IMPORTANT : This file is the methods that render changes to the 
#user's calendar.  This is the step after the LLM recognizes what the user said
#processing it into json dictonary form, and then renders it to each time the user 
#hits enter on the chat.
#once they click finalzie schedule button, then it is rendered to the dashboard page.
#otherwise each response the chatbot gives you is the one after the edits
#the user requests in the chat.
#these are the functionalities of this python file
#there will be another for getting the user input into json format for this code to process and then render

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["rumad"]
users = db["users"]

# 🔍 Fetches a single user document from the database by their NetID
def get_user_by_netid(netid):
    return users.find_one({"netid": netid})

# 📝 Adds a user's prompt and the LLM's response to their prompt history
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

# 🔄 Replaces the user's current working schedule in the database with a new one
def update_current_schedule(netid, new_schedule):
    users.update_one(
        {"netid": netid},
        {"$set": {"current_schedule": new_schedule}}
    )

# 💾 Saves the current schedule into the user's past_schedules list as a snapshot
def save_schedule_as_past(netid, schedule):
    users.update_one(
        {"netid": netid},
        {"$push": {
            "past_schedules": {
                "schedule": schedule,
                "saved_at": datetime.utcnow()
            }
        }}
    )

# ✅ Confirms the current schedule, moves it into past_schedules
def confirm_schedule_update(netid):
    user = get_user_by_netid(netid)
    if user and "current_schedule" in user:
        save_schedule_as_past(netid, user["current_schedule"])
        return True
    return False

# 🔐 Builds and returns a Google Calendar API service object for an authenticated user
def get_google_calendar_service(token_dict):
    cred = Credentials.from_authorized_user_info(token_dict, ["https://www.googleapis.com/auth/calendar"])
    return build("calendar", "v3", credentials=cred)

# 📆 Builds a single Google Calendar event body based on a schedule entry
def create_event_body(entry): 
    weekdays = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2,
        "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
    }

    today = datetime.now()
    target_date = today + timedelta((weekdays[entry["day"]] - today.weekday()) % 7)

    start = datetime.strptime(entry["start_time"], "%H:%M").time()
    end = datetime.strptime(entry["end_time"], "%H:%M").time()

    start_dt = datetime.combine(target_date, start).isoformat()
    end_dt = datetime.combine(target_date, end).isoformat()

    return {
        "summary": entry["commitment"],
        "location": entry["location"],
        "start": {
            "dateTime": start_dt,
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": end_dt,
            "timeZone": "America/New_York"
        }
    }

# ⚔️ Checks if two events overlap in time on the same day (conflict detection)
def is_conflict(event1, event2):
    if event1["day"] != event2["day"]:
        return False

    start1 = datetime.strptime(event1["start_time"], "%H:%M")
    end1 = datetime.strptime(event1["end_time"], "%H:%M")
    start2 = datetime.strptime(event2["start_time"], "%H:%M")
    end2 = datetime.strptime(event2["end_time"], "%H:%M")

    return start1 < end2 and start2 < end1

# 🧹 Filters out conflicting events from a schedule based on a new entry
def remove_conflicts_from_schedule(existing_schedule, new_entry):
    return [event for event in existing_schedule if not is_conflict(event, new_entry)]

# 🔁 Merges new entries into a user's schedule, removing conflicts, then pushes to DB + calendar
def merge_schedule(netid, incoming_entries):
    user = get_user_by_netid(netid)
    current_schedule = user.get("current_schedule", [])
    
    for new_entry in incoming_entries:
        current_schedule = remove_conflicts_from_schedule(current_schedule, new_entry)
        current_schedule.append(new_entry)

    update_current_schedule(netid, current_schedule)
    push_schedule_to_calendar(netid, incoming_entries)

    return current_schedule

# 📤 Pushes all new entries to the user's Google Calendar
def push_schedule_to_calendar(netid, schedule):
    user = get_user_by_netid(netid)
    if not user or "google_credentials" not in user:
        print(f"[!] No Google credentials found for user {netid}")
        return
    
    service = get_google_calendar_service(user["google_credentials"])
    for entry in schedule:
        event = create_event_body(entry)
        try:
            service.events().insert(calendarId="primary", body=event).execute()
        except Exception as e:
            print(f"Failed to add event to calendar: {e}")
