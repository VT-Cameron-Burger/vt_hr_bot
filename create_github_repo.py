import requests
import json
import sys
import os

def create_github_repository(token, repo_name="vt_hr_bot", description="A Python script that downloads PDF files from a specified website"):
    """Create a new GitHub repository using the GitHub API."""
    
    # GitHub API endpoint for creating a repository
    url = "https://api.github.com/user/repos"
    
    # Headers for authentication
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Repository data
    data = {
        "name": repo_name,
        "description": description,
        "private": False,  # Makes the repository public
        "auto_init": False  # Don't initialize with README since we have our own
    }
    
    # Make the API request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        
        # Get the repository details from the response
        repo_data = response.json()
        clone_url = repo_data["clone_url"]
        
        print(f"Successfully created repository: {repo_name}")
        print(f"Clone URL: {clone_url}")
        
        return clone_url
        
    except requests.exceptions.HTTPError as e:
        response = e.response
        print(f"Error creating repository: {str(e)}")
        if response.status_code == 401:
            print("Authentication failed. Please check your GitHub token.")
        elif response.status_code == 422:
            print("Repository already exists or name is invalid.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error creating repository: {str(e)}")
        sys.exit(1)

def setup_remote_and_push(clone_url):
    """Set up the remote repository and push the code."""
    try:
        # Add the remote origin
        os.system(f'git remote add origin {clone_url}')
        
        # Rename the default branch to main
        os.system('git branch -M main')
        
        # Push the code
        os.system('git push -u origin main')
        
        print("Successfully pushed code to GitHub!")
        
    except Exception as e:
        print(f"Error pushing to remote repository: {str(e)}")
        sys.exit(1)

def main():
    # Get GitHub token from environment variable
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("Please set your GitHub token as an environment variable:")
        print("export GITHUB_TOKEN='your_token_here'")
        print("\nTo create a token:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Click 'Generate new token'")
        print("3. Select 'repo' scope")
        print("4. Copy the token and set it as an environment variable")
        sys.exit(1)
    
    # Create the repository
    clone_url = create_github_repository(token)
    
    # Set up remote and push code
    if clone_url:
        setup_remote_and_push(clone_url)

if __name__ == "__main__":
    main()