from flask import Flask, request, jsonify
from pymongo import MongoClient 
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import certifi
from schedule_utils import (
    get_user_by_netid, update_prompt_history,
    update_current_schedule, confirm_schedule_update,
    merge_schedule, update_friend_schedule
)
from llm_handler import update_schedule_from_prompt


# === Setup ===
load_dotenv()
app = Flask(__name__)
CORS(app)

username = "sanikadeshmukh135"
password = "Snehnil16"
uri = f'mongodb+srv://{username}:{password}@cluster1.jo3fsmz.mongodb.net/?retryWrites=true&w=majority'

client = MongoClient(uri, tls=True, tlsCAFile=certifi.where())
db = client['authndb']
users_collection = db['users']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# === Auth Routes ===

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    netid = data.get('netid')
    password = data.get('password')

    if not netid or not password:
        return jsonify({'status': 'error', 'message': 'Missing netid or password'}), 400

    if users_collection.find_one({'netid': netid}):
        return jsonify({'status': 'error', 'message': 'NetID already exists'}), 400

    hashed_password = generate_password_hash(password)
    user_doc = {
        "netid": netid,
        "password": hashed_password,
        "current_schedule": "",
        "past_schedules": [],
        "prompt_history": [],
        "friends": {}
    }
    users_collection.insert_one(user_doc)
    return jsonify({'status': 'success', 'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    netid = data.get('netid')
    password = data.get('password')
    user = users_collection.find_one({'netid': netid})

    if user and check_password_hash(user['password'], password):
        return jsonify({'status': 'success', 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid netid or password'}), 401

# === Schedule Management Routes ===

# ✅ Update prompt history
@app.route('/update_prompt', methods=['POST'])
def log_prompt():
    data = request.get_json()
    netid = data['netid']
    prompt = data['prompt']
    response = data['response']
    update_prompt_history(netid, prompt, response)
    return jsonify({'status': 'success', 'message': 'Prompt logged'})

# ✅ Merge new schedule entries and update MongoDB
@app.route('/merge_schedule', methods=['POST'])
def merge_user_schedule():
    data = request.get_json()
    netid = data['netid']
    entries = data['entries']
    updated_ics = merge_schedule(netid, entries)
    return jsonify({'status': 'success', 'updated_schedule': updated_ics})

# ✅ Use LLM to update schedule from natural language input
@app.route('/update_schedule_with_prompt', methods=['POST'])
def update_schedule_with_prompt():
    data = request.get_json()
    netid = data.get('netid')
    prompt = data.get('prompt')
    
    try:
        updated_ics = update_schedule_from_prompt(netid, prompt)
        return jsonify({'status': 'success', 'updated_schedule': updated_ics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ✅ Finalize schedule: current → past, clear current
@app.route('/finalize_schedule', methods=['POST'])
def finalize_schedule():
    data = request.get_json()
    netid = data['netid']
    success = confirm_schedule_update(netid)
    if success:
        return jsonify({'status': 'success', 'message': 'Schedule finalized'})
    else:
        return jsonify({'status': 'error', 'message': 'No schedule to finalize'})

# ✅ Manually update friend’s shared schedule
@app.route('/update_friend_schedule', methods=['POST'])
def update_friend():
    data = request.get_json()
    netid = data['netid']
    friend_netid = data['friend_netid']
    ics_string = data['ics_schedule']
    update_friend_schedule(netid, friend_netid, ics_string)
    return jsonify({'status': 'success', 'message': 'Friend schedule updated'})

# ✅ Get user document
@app.route('/get_user', methods=['GET'])
def get_user():
    netid = request.args.get('netid')
    user = get_user_by_netid(netid)
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return jsonify({'status': 'success', 'user': user})
    return jsonify({'status': 'error', 'message': 'User not found'})

# === Default route ===
@app.route("/")
def index():
    return "RUPlanner backend is running!"

@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({'status': 'success', 'message': 'Test route is working'})


if __name__ == '__main__':
    app.run(debug=True)
