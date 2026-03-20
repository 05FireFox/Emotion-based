from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import random
import csv
from datetime import datetime

# IMPORT BOTH FUNCTIONS NOW
from recommendations import get_recommendations, get_valid_matrix_id

app = Flask(__name__)
CORS(app)

# =========================================
# DATABASE SETUP (Creates CSV files if missing)
# =========================================
USERS_FILE = 'users_data.csv'
HISTORY_FILE = 'recommendation_history.csv'

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['user_id', 'name', 'email', 'phone', 'password'])

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(['timestamp', 'user_id', 'emotion', 'recommended_games'])

# Temporary dictionary to store OTPs
mock_otp_storage = {}

@app.route('/')
def hello():
    return 'Hello, World! Backend is running.'

# =========================================
# AUTHENTICATION ROUTES
# =========================================
@app.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json(force=True)
        email = data.get('email')
        
        # Generate a random 4-digit OTP
        otp = str(random.randint(1000, 9999))
        mock_otp_storage[email] = otp
        
        # PRETEND TO SEND EMAIL/SMS (Prints to console)
        print(f"\n" + "="*40)
        print(f"📧 EMAIL/SMS SIMULATOR")
        print(f"Sending OTP to {email} and Phone...")
        print(f"Your OTP is: {otp}")
        print("="*40 + "\n")
        
        return jsonify({"message": "OTP sent successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        user_otp = data.get('otp')

        # 1. Verify OTP
        if mock_otp_storage.get(email) != user_otp:
            return jsonify({"error": "Invalid OTP!"}), 400

        # 2. Check if user already exists
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['email'] == email:
                    return jsonify({"error": "Email already registered!"}), 400

        # ====================================================
        # 3. GENERATE A VALID USER ID FROM THE ML MATRIX
        # ====================================================
        new_user_id = get_valid_matrix_id()

        # 4. Save to CSV
        with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([new_user_id, name, email, phone, password])
            
        # Clear OTP
        del mock_otp_storage[email]

        # 5. Return the full user profile so React can display the Avatar
        return jsonify({
            "message": "Registration successful!", 
            "user": {
                "user_id": new_user_id, 
                "name": name, 
                "email": email, 
                "phone": phone
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True)
        identifier = data.get('identifier') # Can be Email OR UserID
        password = data.get('password')

        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row['email'] == identifier or row['user_id'] == identifier) and row['password'] == password:
                    # Return the full user profile so React can display the Avatar
                    return jsonify({
                        "message": "Login successful", 
                        "user": {
                            "user_id": row['user_id'], 
                            "name": row['name'], 
                            "email": row['email'], 
                            "phone": row['phone']
                        }
                    })
                    
        return jsonify({"error": "Invalid Credentials!"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# HISTORY LOGGING ROUTE
# =========================================
@app.route('/save_history', methods=['POST'])
def save_history():
    try:
        data = request.get_json(force=True)
        user_id = data.get('user_id')
        emotion = data.get('emotion')
        games = data.get('games') 
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(HISTORY_FILE, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([timestamp, user_id, emotion, games])
            
        return jsonify({"message": "History saved!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# RECOMMENDATION ROUTES
# =========================================
@app.route('/recommend/user/<user_id>', methods=['POST'])
def get_user_recommendation(user_id):
    try:
        request_json = request.get_json(force=True)
        result = get_recommendations(request_json, str(user_id), is_user=True)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@app.route('/recommend/game/<steam_id>', methods=['POST'])
def get_game_recommendation(steam_id):
    try:
        request_json = request.get_json(force=True)
        result = get_recommendations(request_json, str(steam_id), is_user=False)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8082))
    print(f"Starting server on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port)