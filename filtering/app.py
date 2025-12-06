from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Import your logic
from recommendations import get_recommendations

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello, World! Backend is running.'

@app.route('/recommend/user/<user_id>', methods=['POST'])
def get_user_recommendation(user_id):
    print(f"\n--- NEW REQUEST: User Recommendation ---")
    print(f"Received User ID from URL: {user_id} (Type: {type(user_id)})")

    try:
        # 1. Get the JSON payload (image/emotion data)
        # force=True ensures we read it even if the content-type header is missing
        request_json = request.get_json(force=True)

        # 2. Call the logic
        # CRITICAL FIX: We pass user_id as a STRING. 
        # Do not cast to int() because Steam IDs are often stored as strings in CSVs.
        result = get_recommendations(request_json, str(user_id), is_user=True)
        
        # 3. Return as proper JSON
        return jsonify(result)
        
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


@app.route('/recommend/game/<steam_id>', methods=['POST'])
def get_game_recommendation(steam_id):
    print(f"\n--- NEW REQUEST: Game Recommendation ---")
    print(f"Received Game ID from URL: {steam_id}")

    try:
        request_json = request.get_json(force=True)

        # Pass False for is_user
        # We also pass steam_id as string to be safe
        result = get_recommendations(request_json, str(steam_id), is_user=False)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    # Run on port 5000 (Standard for Flask)
    # Ensure this port matches what your Frontend is calling
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port)