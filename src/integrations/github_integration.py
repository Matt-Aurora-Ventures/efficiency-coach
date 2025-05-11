# This is /home/ubuntu/copri_app/src/integrations/github_integration.py
import requests
import json
import base64 # For encoding file content for GitHub API

GITHUB_API_BASE_URL = "https://api.github.com"

class GitHubIntegration:
    def __init__(self, token=None):
        """Initializes the GitHub client.
        token: Personal Access Token for authentication.
        """
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28" # Recommended by GitHub
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}" # Changed from token to Bearer for PAT

    def get_authenticated_user_info(self):
        """Fetches information about the authenticated user to verify token and permissions."""
        if not self.token:
            print("[GitHubIntegration] Token not provided. Cannot fetch authenticated user info.")
            return None
        url = f"{GITHUB_API_BASE_URL}/user"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print("[GitHubIntegration] Successfully fetched authenticated user info.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching authenticated GitHub user info: {e}")
            if response is not None:
                print(f"Response status: {response.status_code}, Response content: {response.text}")
            return None

    def create_repository(self, repo_name, description="", private=False):
        """Creates a new repository for the authenticated user."""
        if not self.token:
            print("[GitHubIntegration] Token not provided. Cannot create repository.")
            return None
        
        url = f"{GITHUB_API_BASE_URL}/user/repos"
        payload = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True # Creates with a README, first commit, and main branch
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"[GitHubIntegration] Successfully created repository: {response.json().get('html_url')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating GitHub repository 	{repo_name}": {e}")
            if response is not None:
                print(f"Response status: {response.status_code}, Response content: {response.text}")
            return None

    def get_file_sha(self, owner, repo, file_path, branch="main"):
        """Gets the SHA of a file if it exists. Returns None if not found."""
        if not self.token:
            print("[GitHubIntegration] Token not provided. Cannot get file SHA.")
            return None
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                return None # File not found
            response.raise_for_status()
            return response.json().get("sha")
        except requests.exceptions.RequestException as e:
            print(f"Error getting SHA for file {file_path} in {owner}/{repo}: {e}")
            return None

    def upload_or_update_file(self, owner, repo, file_path, file_content_str, commit_message, branch="main"):
        """Uploads a new file or updates an existing file in a repository."""
        if not self.token:
            print("[GitHubIntegration] Token not provided. Cannot upload/update file.")
            return None

        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
        
        # Content must be Base64 encoded
        encoded_content = base64.b64encode(file_content_str.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch
        }
        
        # Check if file exists to get its SHA for update
        sha = self.get_file_sha(owner, repo, file_path, branch)
        if sha:
            payload["sha"] = sha
            print(f"[GitHubIntegration] Updating existing file: {file_path} in {owner}/{repo}")
        else:
            print(f"[GitHubIntegration] Creating new file: {file_path} in {owner}/{repo}")

        try:
            response = requests.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"[GitHubIntegration] Successfully uploaded/updated file: {file_path}. Commit: {response.json()['commit']['sha']}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error uploading/updating file {file_path} to {owner}/{repo}: {e}")
            if response is not None:
                print(f"Response status: {response.status_code}, Response content: {response.text}")
            return None

    def get_user_repos(self, username=None):
        """Fetches repositories for the authenticated user or a specified user."""
        if username:
            url = f"{GITHUB_API_BASE_URL}/users/{username}/repos"
        else:
            if not self.token: # Authenticated user needs a token
                print("[GitHubIntegration] Token required to fetch authenticated user's repos.")
                return []
            url = f"{GITHUB_API_BASE_URL}/user/repos"
        
        params = {"type": "owner", "sort": "updated", "per_page": 10}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            print(f"[GitHubIntegration] Fetched repositories for {	'authenticated user' if not username else username}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GitHub repositories: {e}")
            return []

    def get_repo_issues(self, owner, repo, state="open"):
        """Fetches issues for a specific repository."""
        url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": 10}
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            print(f"[GitHubIntegration] Fetched issues for {owner}/{repo}.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues for {owner}/{repo}: {e}")
            return []

# Example usage (for testing - DO NOT COMMIT/PUSH ACTUAL TOKENS)
# if __name__ == "__main__":
#     # For authenticated requests, generate a Personal Access Token (PAT)
#     # from GitHub Developer Settings with 'repo' scope.
#     # Store it securely, e.g., in an environment variable, do not hardcode.
#     import os
#     TEST_GITHUB_TOKEN = os.getenv("MY_APP_GITHUB_PAT") 

#     if not TEST_GITHUB_TOKEN:
#         print("GitHub token not set (MY_APP_GITHUB_PAT env var). Cannot run authenticated tests.")
#         gh_client = GitHubIntegration()
#         # Example: Fetch repos for a public user
#         public_repos = gh_client.get_user_repos(username="octocat")
#         if public_repos:
#             print(f"Octocat repos: {json.dumps(public_repos[:2], indent=2)}")
#     else:
#         gh_client = GitHubIntegration(token=TEST_GITHUB_TOKEN)
#         user_info = gh_client.get_authenticated_user_info()
#         if user_info:
#             print(f"Authenticated as: {user_info.get('login')}")
            
#             # Test create repository
#             repo_name = "copri-test-repo-delete-me"
#             # created_repo = gh_client.create_repository(repo_name, description="Test repo for CoPri app", private=True)
#             # if created_repo:
#             #     print(f"Created repo: {created_repo.get('html_url')}")
                
#                 # Test upload file
#                 # readme_content = "# Test README\nThis is a test file created by CoPri."
#                 # upload_status = gh_client.upload_or_update_file(user_info.get('login'), repo_name, "README.md", readme_content, "Initial commit")
#                 # if upload_status:
#                 #     print("README.md uploaded/updated successfully.")

#                 # Test update file
#                 # readme_content_updated = "# Test README (Updated)\nThis is an updated test file created by CoPri."
#                 # upload_status_updated = gh_client.upload_or_update_file(user_info.get('login'), repo_name, "README.md", readme_content_updated, "Update README.md")
#                 # if upload_status_updated:
#                 #     print("README.md updated successfully.")

#         my_repos = gh_client.get_user_repos()
#         if my_repos:
#             print(f"My repos: {json.dumps(my_repos[:2], indent=2)}")
#             if my_repos:
#                 first_repo_full_name = my_repos[0]["full_name"]
#                 owner, repo = first_repo_full_name.split('/')
#                 issues = gh_client.get_repo_issues(owner, repo)
#                 if issues:
#                     print(f"Issues for {first_repo_full_name}: {json.dumps(issues[:1], indent=2)}")

