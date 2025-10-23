# GitHub Repository Automation

A Python script to automate the creation of GitHub repositories and initial code pushing.

## Features

- Creates new GitHub repositories via GitHub API
- Sets up remote repository connection
- Pushes initial code to the repository
- Handles error cases and provides clear feedback

## Requirements

- Python 3.x
- requests

## Installation

1. Clone the repository:
```bash
git clone https://github.com/VT-Cameron-Burger/github_automation.git
cd github_automation
```

2. Install dependencies:
```bash
pip install requests
```

3. Set up GitHub token:
- Go to https://github.com/settings/tokens
- Click "Generate new token (classic)"
- Select the `repo` scope
- Copy the generated token
- Set it as an environment variable:
```bash
export GITHUB_TOKEN='your_token_here'
```

## Usage

```bash
python create_github_repo.py
```

The script will:
1. Create a new GitHub repository using your token
2. Set up the remote connection
3. Push your code to the repository

## Required Token Permissions

The GitHub Personal Access Token needs the following scope:
- `repo` - Full control of private repositories

This provides all necessary permissions to:
- Create new repositories
- Push code to repositories
- Manage repository settings
- Set up remote connections

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.