from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["authndb"]
users = db["users"]

netid = "am3606"
password = "test123"

user_doc = {
    "netid": netid,
    "password_hash": generate_password_hash(password),
    "current_schedule": "",         # only ONE .ics string
    "past_schedules": [],           # list of .ics strings
    "prompt_history": [],           # list of prompt → response
    "friends": {}                   # netid → ics schedule mapping
}

existing = users.find_one({"netid": netid})
if not existing:
    users.insert_one(user_doc)
    print(f"✅ User {netid} created.")
else:
    print(f"⚠️ User {netid} already exists.")
