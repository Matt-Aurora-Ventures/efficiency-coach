#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.integrations.github_integration import GitHubIntegration

def verify_pat_and_get_user():
    pat = os.getenv("MY_APP_GITHUB_PAT")
    if not pat:
        print("GitHub PAT (MY_APP_GITHUB_PAT) not found in environment variables.")
        print("Please ensure the PAT was submitted correctly via the secure browser input.")
        return None

    print(f"Found PAT: {'*' * (len(pat) - 4) + pat[-4:] if len(pat) > 4 else '***'}") # Print masked PAT
    github_client = GitHubIntegration(token=pat)
    user_info = github_client.get_authenticated_user_info()

    if user_info:
        print(f"Successfully authenticated with GitHub as user: {user_info.get('login')}")
        print(f"User ID: {user_info.get('id')}")
        return user_info
    else:
        print("Failed to authenticate with GitHub or fetch user info using the provided PAT.")
        print("Please double-check the PAT and its permissions (must include 'repo' scope).")
        return None

if __name__ == "__main__":
    authenticated_user = verify_pat_and_get_user()
    if authenticated_user:
        # Further actions can be taken here if needed, like storing the username
        pass

