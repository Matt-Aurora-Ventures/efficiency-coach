# This is /home/ubuntu/copri_app/src/models/copri_models.py
from src.database import db # Changed to absolute import
from sqlalchemy.dialects.mysql import JSON # Using mysql dialect for JSON, works with SQLite too
import datetime

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False) # e.g., email
    hashed_password = db.Column(db.String(255), nullable=False)
    preferences = db.Column(JSON) # For dashboard/interaction preferences
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    connections = db.relationship("PlatformConnection", backref="user", lazy=True, cascade="all, delete-orphan")
    projects = db.relationship("Project", backref="user", lazy=True, cascade="all, delete-orphan")
    coaching_interactions = db.relationship("CoachingInteraction", backref="user", lazy=True, cascade="all, delete-orphan")
    financial_notes = db.relationship("FinancialNote", backref="user", lazy=True, cascade="all, delete-orphan")
    applications = db.relationship("ApplicationTracking", backref="user", lazy=True, cascade="all, delete-orphan")

class PlatformConnection(db.Model):
    __tablename__ = "platform_connections"
    connection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    platform_name = db.Column(db.String(50), nullable=False) # Enum: Trello, LinkedIn, Gmail, GoogleCalendar, X, GitHub
    platform_user_id = db.Column(db.String(255), nullable=True)
    access_token = db.Column(db.Text, nullable=False) # Encrypted
    refresh_token = db.Column(db.Text, nullable=True) # Encrypted
    token_expires_at = db.Column(db.TIMESTAMP, nullable=True)
    scopes = db.Column(db.Text, nullable=True)
    last_sync_time = db.Column(db.TIMESTAMP, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships to data tables linked via this connection
    trello_cards = db.relationship("TrelloCard", backref="platform_connection", lazy=True, cascade="all, delete-orphan")
    emails = db.relationship("Email", backref="platform_connection", lazy=True, cascade="all, delete-orphan")
    calendar_events = db.relationship("CalendarEvent", backref="platform_connection", lazy=True, cascade="all, delete-orphan")
    # github_issues = db.relationship("GitHubIssue", backref="platform_connection", lazy=True, cascade="all, delete-orphan")

class TrelloCard(db.Model):
    __tablename__ = "trello_cards"
    card_id_pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trello_card_id = db.Column(db.String(255), unique=True, nullable=False)
    connection_id = db.Column(db.Integer, db.ForeignKey("platform_connections.connection_id"), nullable=False)
    trello_board_id = db.Column(db.String(255), nullable=False)
    trello_list_id = db.Column(db.String(255), nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.TIMESTAMP, nullable=True)
    url = db.Column(db.String(2048), nullable=True)
    labels = db.Column(JSON, nullable=True)
    members_trello_ids = db.Column(JSON, nullable=True)
    last_activity_date = db.Column(db.TIMESTAMP, nullable=True)
    created_at_trello = db.Column(db.TIMESTAMP, nullable=True)
    imported_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at_copri = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Email(db.Model):
    __tablename__ = "emails"
    email_id_pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gmail_message_id = db.Column(db.String(255), unique=True, nullable=False)
    gmail_thread_id = db.Column(db.String(255), nullable=False)
    connection_id = db.Column(db.Integer, db.ForeignKey("platform_connections.connection_id"), nullable=False)
    sender = db.Column(db.String(255), nullable=True)
    recipients_to = db.Column(db.Text, nullable=True)
    recipients_cc = db.Column(db.Text, nullable=True)
    subject = db.Column(db.Text, nullable=True)
    snippet = db.Column(db.Text, nullable=True)
    received_date = db.Column(db.TIMESTAMP, nullable=True)
    labels_gmail = db.Column(JSON, nullable=True)
    is_read = db.Column(db.Boolean, nullable=True)
    is_important = db.Column(db.Boolean, nullable=True)
    follow_up_status = db.Column(db.String(50), nullable=True)
    extracted_tasks = db.Column(JSON, nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    imported_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at_copri = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"
    event_id_pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gcal_event_id = db.Column(db.String(255), unique=True, nullable=False)
    gcal_calendar_id = db.Column(db.String(255), nullable=False)
    connection_id = db.Column(db.Integer, db.ForeignKey("platform_connections.connection_id"), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.TIMESTAMP, nullable=True)
    end_time = db.Column(db.TIMESTAMP, nullable=True)
    is_all_day = db.Column(db.Boolean, nullable=True)
    location = db.Column(db.Text, nullable=True)
    attendees = db.Column(JSON, nullable=True)
    creator_email = db.Column(db.String(255), nullable=True)
    status_gcal = db.Column(db.String(50), nullable=True)
    imported_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at_copri = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Project(db.Model):
    __tablename__ = "projects"
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    priority_copri = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # project_item_links = db.relationship("ProjectItemLink", backref="project", lazy=True, cascade="all, delete-orphan")

# class ProjectItemLink(db.Model):
#     __tablename__ = "project_item_links"
#     link_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id"), nullable=False)
#     item_id_pk = db.Column(db.Integer, nullable=False) # Refers to PK in respective data table
#     item_type = db.Column(db.String(50), nullable=False) # Enum: TrelloCard, Email, etc.

class CoachingInteraction(db.Model):
    __tablename__ = "coaching_interactions"
    interaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    interaction_type = db.Column(db.String(100), nullable=True)
    question_asked = db.Column(db.Text, nullable=True)
    user_response = db.Column(db.Text, nullable=True)
    generated_insight_or_suggestion = db.Column(db.Text, nullable=True)
    related_item_id_pk = db.Column(db.Integer, nullable=True)
    related_item_type = db.Column(db.String(50), nullable=True)

class FinancialNote(db.Model):
    __tablename__ = "financial_notes"
    note_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id"), nullable=True)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=True)
    currency = db.Column(db.String(3), default="USD")
    type = db.Column(db.String(50), nullable=True) # Enum: Income, Expense, Investment, Projection
    transaction_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class ApplicationTracking(db.Model):
    __tablename__ = "application_tracking"
    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    name_of_program = db.Column(db.String(255), nullable=False)
    type_of_program = db.Column(db.String(100), nullable=True)
    application_status = db.Column(db.String(50), nullable=True)
    submission_deadline = db.Column(db.Date, nullable=True)
    submitted_date = db.Column(db.Date, nullable=True)
    decision_date = db.Column(db.Date, nullable=True)
    url_program = db.Column(db.String(2048), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

# Placeholder for GitHub and other platform-specific data models if needed later
# class GitHubIssue(db.Model): ...
# class LinkedInData(db.Model): ...
# class XData(db.Model): ...

