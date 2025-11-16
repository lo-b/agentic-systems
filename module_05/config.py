import os
from dataclasses import dataclass

from dotenv import load_dotenv

assert load_dotenv(), ".env file missing or empty"


@dataclass
class GitHubConfig:
    """Configuration object for the GitHub REST API."""

    url: str = os.getenv("GITHUB_SERVICE_URL", "")
    owner: str = os.getenv("GITHUB_OWNER", "")
    secret_token: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    api_version: str = os.getenv("GITHUB_API_VERSION", "")


@dataclass
class GitHubAppConfig:
    """Configuration object for GitHub App Authentication (AuthN)."""

    app_id: str = os.getenv("GITHUB_APP_CLIENT_ID", "")
    pem_path: str = os.getenv("GITHUB_APP_PEM_PATH", "")
