import os
from dataclasses import dataclass
from http import HTTPStatus
from typing import TypedDict

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from requests import get, patch, post

assert load_dotenv(), "empty or no .env file found"

mcp = FastMCP("CustomGitHub")


@dataclass
class GitHubConfig:
    """Configuration object for the GitHub REST API."""

    url: str = os.getenv("GITHUB_SERVICE_URL", "")
    owner: str = os.getenv("GITHUB_OWNER", "")
    secret_token: str = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
    api_version: str = os.getenv("GITHUB_API_VERSION", "")


config = GitHubConfig()

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {config.secret_token}",
    "X-GitHub-Api-Version": "2022-11-28",
}


class RepoResponse(TypedDict):
    """Simplified GitHub /repos GET reponse"""

    description: str


class PRResponse(TypedDict):
    """GitHub PR Patch reponse"""

    http_code: HTTPStatus


class DiffEntry(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    changes: int
    patch: str | None = Field(
        None,
        description="Unified diff: headers (@@ -old +new @@) + changes (- removed, + added, unchanged context)",
    )


class PrChanges(BaseModel):
    changes: list[DiffEntry]


class CommentResponse(TypedDict):
    comment_id: int


@mcp.tool()
async def get_repo(repo_name: str) -> RepoResponse:
    """Get GitHub repositories by repository name for (already set) github user."""

    res = get(
        f"{config.url}/repos/{config.owner}/{repo_name}",
        headers=headers,
    )

    return {"description": res.json()["description"]}


@mcp.tool()
async def update_pr_description(
        repo_name: str, description: str, pr_id: int
) -> PRResponse:
    """Update GitHub Pull Request body (description).

    Args:
        repo_name: Name of the repository
        description: New description (body) text for the pull request
        pr_id: ID of the pull request to update

    Returns:
        PRResponse: Dictionary containing the HTTP status code of the operation
    """
    req = {"body": description}

    res = patch(
        f"{config.url}/repos/{config.owner}/{repo_name}/pulls/{pr_id}",
        json=req,
        headers=headers,
    )

    return {"http_code": HTTPStatus(res.status_code)}


@mcp.tool()
async def pull_request_get_files(repo_name: str, pr_id: int) -> PrChanges:
    """Retieve changed files in a pull request.

    Args:
        repo_name: Name of the repository
        pr_id: ID of the pull request to update

    """
    res = get(
        f"{config.url}/repos/{config.owner}/{repo_name}/pulls/{pr_id}/files",
        headers=headers,
    )

    return PrChanges(changes=res.json())


@mcp.tool()
async def create_pr_comment(repo_name: str, pr_id: int, comment: str) -> CommentResponse:
    """Create a GitHub Pull Request (PR) comment.

    Args:
        repo_name: Name of the repository
        pr_id: ID of the pull request to update
        comment: Comment text for the pull request

    Returns:
        CommentResponse: Dictionary containing the ID of the created comment

    """

    req = {"body": comment}
    res = post(
        f"{config.url}/repos/{config.owner}/{repo_name}/issues/{pr_id}/comments",
        json=req,
        headers=headers,
    )

    return {"comment_id": res.json()["id"]}


@mcp.tool()
async def update_pr_comment(repo_name: str, comment_id: int, comment: str) -> CommentResponse:
    """Update GitHub Pull Request (PR) comment.

    Args:
        repo_name: Name of the repository
        comment_id: ID of the comment to update
        comment: New comment text for the pull request

    """

    req = {"body": comment}
    # GitHub API for updating an issue comment requires PATCH and the issues/comments path
    res = patch(
        f"{config.url}/repos/{config.owner}/{repo_name}/issues/comments/{comment_id}",
        json=req,
        headers=headers,
    )

    return {"comment_id": res.json()["id"]}


# INFO: `__main__` is the name of the environment where top-level code is run.
# 'Top-level code' is the first user-specified Python module that starts running.
# I.e. the MCP server runs when this file is run directly (and name gets set to main).
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
