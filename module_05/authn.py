import os
import time

import jwt
from config import GitHubAppConfig, GitHubConfig
from requests import post


def create_gh_app_token(
    config: GitHubAppConfig, expire_after: int, drift: int = 0
) -> str:
    """Create a JWT for the GitHub Application

    Args:
        config (GitHubAppConfig): Config to use when creating the JWT.
        drift (int): Number of seconds to subtract from the current time when setting the token's 'created at' time stamp.
        expire_after (int): Amount of seconds when the token will expire after.


    """
    assert expire_after <= 600, "JWT 'exp' cannot be longer than 10 minutes"

    with open(config.pem_path, "rb") as pem_file:
        signing_key = pem_file.read()

    payload = {
        # WARN: might need time drift adjustment; i.e. issue token in the past by subtracting e.g. 60s
        "iat": int(time.time()) - drift,
        "exp": int(time.time()) + expire_after,
        "iss": config.app_id,
    }

    return jwt.encode(payload, signing_key, algorithm="RS256")


def create_gh_app_access_token(config: GitHubConfig, token: str) -> str:
    """Exchange an app JWT for a short-lived installation access token.

    Returns the installation access token string. Raises for non-2xx responses.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    res = post(
        f"{config.url}/app/installations/{os.getenv('GITHUB_APP_INSTALL_ID', '')}/access_tokens",  # FIX: use install id from webhookreq
        headers=headers,
    )
    # Raise an HTTPError if the request was unsuccessful
    res.raise_for_status()
    data = res.json()
    return data["token"]
