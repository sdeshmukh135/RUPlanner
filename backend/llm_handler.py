# llm_handler.py
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai
from schedule_utils import merge_schedule, update_prompt_history


# Load environment variables and set up LLM
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Set up MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["authndb"]
users = db["users"]

# 🔬 Send a prompt to Gemini and return the plain JSON string response
def get_llm_response(prompt):
    try:
        full_prompt = (
            "You are a scheduling assistant. Given the user's natural language request, "
            "return ONLY a JSON array of schedule objects with the fields: "
            "commitment, day, start_time (24hr), end_time (24hr), location. "
            "No extra explanation, just valid JSON.\n\nUser input: " + prompt
        )
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# 🤖 Parse LLM output into a Python dictionary list (schedule entries)
def parse_schedule_from_llm_response(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return []

# ⚙️ Core: Take user prompt ➔ get LLM schedule JSON ➔ update DB

def update_schedule_from_prompt(netid, prompt):
    llm_response = get_llm_response(prompt)
    parsed_schedule = parse_schedule_from_llm_response(llm_response)

    update_prompt_history(netid, prompt, llm_response)
    updated_ics = merge_schedule(netid, parsed_schedule)
    return updated_ics
