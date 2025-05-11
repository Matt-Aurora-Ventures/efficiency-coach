# This is /home/ubuntu/copri_app/src/main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify # Added jsonify
from flask_sqlalchemy import SQLAlchemy

# Import integration modules (example for Trello)
from src.integrations.trello_integration import TrelloIntegration
# from src.services.coaching_service import CoachingService # Will be used later

app = Flask(__name__)

# Database Configuration - Using SQLite for prototype simplicity
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, "..", "instance")
if not os.path.exists(INSTANCE_FOLDER_PATH):
    os.makedirs(INSTANCE_FOLDER_PATH)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_FOLDER_PATH, "copri_prototype.db")}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "a_very_secret_key_for_prototype") # Added for session management if needed later

db = SQLAlchemy(app)

# Import models here to avoid circular imports, after db is initialized
from src.models.copri_models import User, PlatformConnection, TrelloCard, Email, CalendarEvent, Project, CoachingInteraction, FinancialNote, ApplicationTracking

@app.route("/")
def hello_world():
    return "Hello from CoPri App Prototype!"

# --- Test Routes for Integrations ---
@app.route("/test-trello-boards")
def test_trello_boards():
    # IMPORTANT: For actual use, API key and token must be securely obtained from the user/database
    # These are placeholders and will not work with the live Trello API.
    # The user would need to go through an OAuth flow to grant access.
    placeholder_api_key = "YOUR_TRELLO_API_KEY_PLACEHOLDER"
    placeholder_token = "YOUR_TRELLO_TOKEN_PLACEHOLDER"

    # Check if the placeholder keys are still placeholders
    if placeholder_api_key == "YOUR_TRELLO_API_KEY_PLACEHOLDER" or placeholder_token == "YOUR_TRELLO_TOKEN_PLACEHOLDER":
        return jsonify({
            "message": "Trello API key and token are placeholders. Live API call will not work.",
            "note": "To test live, replace placeholders or implement OAuth flow and secure token storage.",
            "simulated_data_info": "The TrelloIntegration class currently returns simulated data or errors if keys are not live."
        }), 400

    trello_client = TrelloIntegration(api_key=placeholder_api_key, token=placeholder_token)
    member_info = trello_client.get_member_info() # Test authentication
    if not member_info:
        return jsonify({"error": "Failed to authenticate with Trello or fetch member info. Check TrelloIntegration logs."}), 500
    
    boards = trello_client.get_boards()
    if boards is None: # Check for None specifically if the method can return it on error
        return jsonify({"error": "Failed to fetch Trello boards. Check TrelloIntegration logs."}), 500
    
    return jsonify({"authenticated_user": member_info.get("fullName", "N/A"), "boards": boards})

# Function to create database tables
def create_tables():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created (if they didn_t exist).")

if __name__ == "__main__":
    create_tables() # Create tables when app starts for the prototype
    app.run(debug=True, host="0.0.0.0", port=5000)

