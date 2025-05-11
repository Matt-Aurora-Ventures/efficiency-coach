# This is /home/ubuntu/copri_app/src/services/coaching_service.py
from src.main import db # Assuming db is initialized in src/main.py
from src.models.copri_models import User, CoachingInteraction #, Project, TrelloCard, Email, etc.
import datetime

class CoachingService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.query.get(self.user_id)
        if not self.user:
            raise ValueError(f"User with id {self.user_id} not found.")

    def ask_about_accomplishments(self):
        """Asks the user about their accomplishments."""
        question = "What have you accomplished recently that you are proud of?"
        # In a real scenario, this would be presented to the user via the chosen interface (dashboard/chat)
        # For now, we can log this interaction or store it.
        interaction = CoachingInteraction(
            user_id=self.user_id,
            interaction_type="ask_accomplishments",
            question_asked=question,
            timestamp=datetime.datetime.utcnow()
        )
        # db.session.add(interaction)
        # db.session.commit() # This would be handled by the route/controller normally
        print(f"[CoachingService] Asking user {self.user_id}: {question}")
        return question # Or an object representing the interaction to be displayed

    def ask_highest_priority(self):
        """Asks the user about their highest priority."""
        question = "What is your single highest priority task or goal right now?"
        interaction = CoachingInteraction(
            user_id=self.user_id,
            interaction_type="ask_priority",
            question_asked=question,
            timestamp=datetime.datetime.utcnow()
        )
        # db.session.add(interaction)
        # db.session.commit()
        print(f"[CoachingService] Asking user {self.user_id}: {question}")
        return question

    def ask_about_finances_for_scaling(self, project_name=None):
        """Asks about finances related to scaling a business/project."""
        if project_name:
            question = f"Regarding your project 	{project_name}", what are your current financial considerations for scaling it up?"
        else:
            question = "What are your current financial considerations for scaling your businesses or projects?"
        
        interaction = CoachingInteraction(
            user_id=self.user_id,
            interaction_type="ask_finances_scaling",
            question_asked=question,
            timestamp=datetime.datetime.utcnow()
        )
        # db.session.add(interaction)
        # db.session.commit()
        print(f"[CoachingService] Asking user {self.user_id}: {question}")
        return question

    def record_user_response(self, interaction_id, response_text):
        """Records the user_s response to a coaching question."""
        interaction = CoachingInteraction.query.get(interaction_id)
        if interaction and interaction.user_id == self.user_id:
            interaction.user_response = response_text
            interaction.updated_at = datetime.datetime.utcnow()
            # db.session.commit()
            print(f"[CoachingService] Recorded response for interaction {interaction_id}")
            return True
        print(f"[CoachingService] Failed to record response for interaction {interaction_id}")
        return False

    def suggest_next_moves(self):
        """Analyzes available data and suggests next moves. Placeholder for complex logic."""
        # This would involve: 
        # 1. Fetching data from Trello, Gmail, Calendar, FinancialNotes, Applications etc.
        # 2. Applying prioritization heuristics (due dates, user-set priorities, keywords, financial goals)
        # 3. Considering ethical monetization and future prospects.
        suggestion = "Based on current data, consider focusing on [Placeholder Task/Project] because [Placeholder Reason]."
        
        interaction = CoachingInteraction(
            user_id=self.user_id,
            interaction_type="suggest_next_moves",
            generated_insight_or_suggestion=suggestion,
            timestamp=datetime.datetime.utcnow()
        )
        # db.session.add(interaction)
        # db.session.commit()
        print(f"[CoachingService] Suggesting next moves for user {self.user_id}: {suggestion}")
        return suggestion

# Example usage (for testing, would be called from a service or route)
# if __name__ == "__main__":
#     # This requires a Flask app context and a user in the database
#     # from src.main import app, db
#     # with app.app_context():
#     #     # Ensure a user exists, e.g., user_id = 1
#     #     test_user_id = 1 
#     #     if User.query.get(test_user_id):
#     #         coach = CoachingService(user_id=test_user_id)
#     #         coach.ask_about_accomplishments()
#     #         coach.ask_highest_priority()
#     #         coach.suggest_next_moves()
#     #     else:
#     #         print(f"User {test_user_id} not found. Please create a user to test CoachingService.")

