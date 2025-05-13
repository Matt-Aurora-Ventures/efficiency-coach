# This is /home/ubuntu/copri_app/src/main.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import subprocess
import datetime

from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from src.database import db

from src.integrations.trello_integration import TrelloIntegration

app = Flask(__name__, template_folder=	"templates")

PAT_FILE_PATH = "/tmp/github_pat.txt"
REPO_PATH = "/home/ubuntu/copri_app"
GITHUB_USER = "Matt-Aurora-Ventures"
REPO_NAME = "efficiency-coach"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, "..", "instance")
if not os.path.exists(INSTANCE_FOLDER_PATH):
    os.makedirs(INSTANCE_FOLDER_PATH)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_FOLDER_PATH, 'copri_prototype.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "a_very_secret_key_for_prototype")

db.init_app(app)

from src.models.copri_models import User, PlatformConnection, TrelloCard, Email, CalendarEvent, Project, CoachingInteraction, FinancialNote, ApplicationTracking

@app.route("/input-secure-token", methods=["GET", "POST"])
def input_secure_token():
    if request.method == "POST":
        pat = request.form.get("pat")
        if pat:
            try:
                with open(PAT_FILE_PATH, "w") as f:
                    f.write(pat)
                os.chmod(PAT_FILE_PATH, 0o600)
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

@app.route("/github/push", methods=["POST"])
def trigger_github_push():
    if not os.path.exists(PAT_FILE_PATH):
        return jsonify({"success": False, "message": "GitHub PAT not found. Please submit it via /input-secure-token first."}), 400
    
    with open(PAT_FILE_PATH, "r") as f:
        pat = f.read().strip()

    if not pat:
        return jsonify({"success": False, "message": "GitHub PAT is empty. Please submit it via /input-secure-token first."}), 400

    try:
        # Check for changes
        status_result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_PATH, capture_output=True, text=True, check=True)
        if not status_result.stdout.strip():
            return jsonify({"success": True, "message": "No changes to push."})

        # Configure remote URL with PAT
        remote_url = f"https://{GITHUB_USER}:{pat}@github.com/{GITHUB_USER}/{REPO_NAME}.git"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=REPO_PATH, check=True)

        # Add, commit, and push
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
        commit_message = f"CoPri: User-triggered update - {datetime.datetime.utcnow().isoformat()}Z"
        subprocess.run(["git", "commit", "-m", commit_message], cwd=REPO_PATH, check=True)
        push_result = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_PATH, capture_output=True, text=True, check=True)
        
        # Securely delete PAT file after successful push
        os.remove(PAT_FILE_PATH)
        
        return jsonify({"success": True, "message": "Updates pushed to GitHub successfully.", "details": push_result.stdout})

    except subprocess.CalledProcessError as e:
        error_message = f"Git command failed: {e.cmd}\nStderr: {e.stderr}\nStdout: {e.stdout}"
        print(error_message)
        return jsonify({"success": False, "message": "Failed to push updates to GitHub.", "error": error_message}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"success": False, "message": "An unexpected error occurred.", "error": str(e)}), 500

@app.route("/")
def hello_world():
    return "Hello from CoPri App Prototype!"

@app.route("/test-trello-boards")
def test_trello_boards():
    placeholder_api_key = "YOUR_TRELLO_API_KEY_PLACEHOLDER"
    placeholder_token = "YOUR_TRELLO_TOKEN_PLACEHOLDER"
    if placeholder_api_key == "YOUR_TRELLO_API_KEY_PLACEHOLDER" or placeholder_token == "YOUR_TRELLO_TOKEN_PLACEHOLDER":
        return jsonify({
            "message": "Trello API key and token are placeholders. Live API call will not work.",
            "note": "To test live, replace placeholders or implement OAuth flow and secure token storage.",
            "simulated_data_info": "The TrelloIntegration class currently returns simulated data or errors if keys are not live."
        }), 400
    trello_client = TrelloIntegration(api_key=placeholder_api_key, token=placeholder_token)
    member_info = trello_client.get_member_info()
    if not member_info:
        return jsonify({"error": "Failed to authenticate with Trello or fetch member info. Check TrelloIntegration logs."}), 500
    boards = trello_client.get_boards()
    if boards is None:
        return jsonify({"error": "Failed to fetch Trello boards. Check TrelloIntegration logs."}), 500
    return jsonify({"authenticated_user": member_info.get("fullName", "N/A"), "boards": boards})

def create_tables():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created (if they didn_t exist).")

if __name__ == "__main__":
    create_tables()
    app.run(debug=True, host="0.0.0.0", port=5000)

