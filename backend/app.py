from flask import Flask, request, jsonify
from pymongo import MongoClient 
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# using mongodb for database management
# creating a client through MongoClient (client-server architecture)

app = Flask(__name__)
CORS(app) # connecting the frontend to the backend

# creating the client
url = "mongodb://localhost:27017/"
client = MongoClient(url) # with unique url
db = client['authndb']
users_collection = db['users']

# two versions, whether they login or signup
@app.route('/login', methods=['POST']) # HTTP request
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username':username})
    if user and check_password_hash(user['password'], password): # if it exists and the password is correct
        return jsonify({'status': 'success', 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password: # if they didn't enter a username or a password (from the frontend)
        return jsonify({'status': 'error', 'message': 'Missing username or password'}), 400
    
    # check if the user exists
    existing_user = users_collection.find_one({'username':username})
    if existing_user:
        return jsonify({'status': 'error', 'message': 'Existing username or password, try againnnnnn'}), 400
    
    # otherwise, store the username and password in the database (hash them first for security purposes)
    hash_password = generate_password_hash(password)
    users_collection.insert_one({'username': username, 'password': hash_password})

    return jsonify({'status': 'success', 'message': 'User created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)



