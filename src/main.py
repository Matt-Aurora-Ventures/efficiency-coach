# This is /home/ubuntu/copri_app/src/main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from src.database import db  # Changed to absolute import

# Import integration modules (example for Trello)
from src.integrations.trello_integration import TrelloIntegration
# from src.services.coaching_service import CoachingService # Will be used later

app = Flask(__name__, template_folder='templates') # Ensure templates folder is specified, removed tabs

# --- Temp file for PAT --- 
PAT_FILE_PATH = "/tmp/github_pat.txt"

# Database Configuration - Using SQLite for prototype simplicity
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, "..", "instance")
if not os.path.exists(INSTANCE_FOLDER_PATH):
    os.makedirs(INSTANCE_FOLDER_PATH)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_FOLDER_PATH, 'copri_prototype.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "a_very_secret_key_for_prototype")

db.init_app(app) # Initialize db with the app

# Import models here to avoid circular imports, after db is initialized
from src.models.copri_models import User, PlatformConnection, TrelloCard, Email, CalendarEvent, Project, CoachingInteraction, FinancialNote, ApplicationTracking

# --- Temporary route for PAT submission ---
@app.route("/input-secure-token", methods=["GET", "POST"])
def input_secure_token():
    if request.method == "POST":
        pat = request.form.get("pat")
        if pat:
            try:
                with open(PAT_FILE_PATH, "w") as f:
                    f.write(pat)
                os.chmod(PAT_FILE_PATH, 0o600) # Restrict permissions
                print(f"PAT received and written to {PAT_FILE_PATH} (length: {len(pat)})")
                flash("Token submitted successfully! You can close this page.", "success")
                return render_template("submit_pat.html", message="Token submitted. You can close this page.", message_type="success")
            except Exception as e:
                print(f"Error writing PAT to file: {e}")
                flash(f"Error saving token: {e}", "error")
                return render_template("submit_pat.html", message=f"Error saving token: {e}", message_type="error")
        else:
            flash("No token provided.", "error")
            return render_template("submit_pat.html", message="Error: No token provided.", message_type="error")
    return render_template("submit_pat.html")

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

