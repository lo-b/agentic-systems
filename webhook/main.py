import logging
import os
from typing import Annotated, Any

import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, Response
from langchain_core.runnables import RunnableConfig
from langgraph_sdk import get_client
from pydantic import BaseModel, Field
from utils import verify_signature

assert load_dotenv(), ".env file missing or empty"

WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", 8000))
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
VALIDATE_SIG: bool = os.getenv("VALIDATE_SIG", "true").lower() == "true"

_SUMMON = "@mergemuppet"

logger = logging.getLogger("uvicorn.error")
# logger = logging.getLogger("GitHubWebHook")
# logger.setLevel(logging.INFO)

app = FastAPI(title="GitHub App webhook")


class RepositoryResponse(BaseModel):
    name: str = Field(description="Repository name")


class IssueResponse(BaseModel):
    number: int = Field(description="Issue or PR ID")


class IssueCommentResponse(BaseModel):
    body: str = Field(
        description="Contents of the issue comment",
    )


class SenderResponse(BaseModel):
    login: str = Field(
        description="Sender name; e.g. GitHub user or app name",
        examples=[
            "user-name",
            "my-app[bot]",
        ],
    )
    type: str = Field(examples=["User", "Bot"])


class PullRequestResponse(BaseModel):
    title: str = Field(description="The title of the pull request.")
    body: str | None = Field(description="Pull request description")


class IssueCommentEventPayload(BaseModel):
    action: str = Field(
        default="created",
        description="action type",
        examples=["created", "deleted", "edited"],
    )
    comment: IssueCommentResponse
    issue: IssueResponse
    repository: RepositoryResponse
    sender: SenderResponse


class PullRequestEventPayload(BaseModel):
    action: str = Field(
        description="action type",
        examples=["opened", "edited"],
    )
    number: int = Field(description="The pull request number.")
    pull_request: PullRequestResponse
    repository: RepositoryResponse
    sender: SenderResponse


class PingEventPayload(BaseModel):
    zen: str


@app.post("/postreceive")
async def github_webhook(
    event_payload: Request,
    x_hub_signature_256: Annotated[str, Header()],
    x_github_event: Annotated[
        str,
        Header(example="ping"),
    ],
    background_tasks: BackgroundTasks,
):
    """
    Handle GitHub webhook events.

    This endpoint receives GitHub webhook events and processes PR comments.
    """
    body = await event_payload.body()

    if VALIDATE_SIG and not verify_signature(
        body, GITHUB_WEBHOOK_SECRET, x_hub_signature_256
    ):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")

    logger.info("received event=%s" % x_github_event)
    data: dict[str, Any] = await event_payload.json()
    assert data is not dict, logger.error("received data is not a dict (json)")

    action: str = data.get("action", "UNKNOWN")
    logger.info("event action=%s" % action)

    match x_github_event:
        case "ping":
            req = PingEventPayload.model_validate(data)
            return Response(status_code=200, content=req.zen)
        case "pull_request":
            event = PullRequestEventPayload.model_validate(data)
            match event.action:
                case "opened":
                    if event.sender.type != "Bot":
                        background_tasks.add_task(
                            http_graph_invoke,
                            "Update the description with a summary of the PR changes.",
                            event.number,
                            event.repository.name,
                            "summary",
                        )
                        background_tasks.add_task(
                            http_graph_invoke,
                            "Create a new PR comment with a walkthrough of the changes.",
                            event.number,
                            event.repository.name,
                            "walkthrough",
                        )
                case _:
                    logger.warning(
                        "skip processing of event=%s, action=%s"
                        % (x_github_event, action)
                    )
                    return Response(status_code=422, content="event not allowed")
        case "issue_comment":
            req = IssueCommentEventPayload.model_validate(data)
            match req.action:
                case "created":
                    if _SUMMON in req.comment.body and req.sender.type != "Bot":
                        background_tasks.add_task(
                            http_graph_invoke,
                            req.comment.body,
                            req.issue.number,
                            req.repository.name,
                            "N/A",
                        )
                    else:
                        logger.warning(
                            "skip processing of event=%s, action=%s"
                            % (x_github_event, action)
                        )
                        return Response(status_code=422, content="event not allowed")

                case _:
                    logger.warning(
                        "skip processing of event=%s, action=%s"
                        % (x_github_event, action)
                    )
                    return Response(status_code=422, content="event not allowed")
        case _:
            logger.warning(
                "skip processing of event=%s, action=%s" % (x_github_event, action)
            )
            return Response(status_code=422, content="event not allowed")

    return Response(status_code=202, content="accepted")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "GitHub Webhook Handler is running"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


async def http_graph_invoke(comment: str, pr_id: int, repo_name: str, pr_action: str):
    client = get_client(url="http://localhost:2024")
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    config = RunnableConfig(recursion_limit=15)
    run = await client.runs.wait(
        thread_id,
        "simple_agent",
        input={
            "messages": [
                {
                    "role": "human",
                    "content": comment,
                }
            ],
        },
        config=config,
        context={
            "model": "xai:grok-4-fast-reasoning",
            "pr_id": pr_id,
            "repo_name": repo_name,
            "pr_action": pr_action,
        },
    )
    last_msg = run.get("messages")[-1]
    usage_metadata = last_msg["usage_metadata"]
    logger.info(
        f"token (total) in/reasoning/out: ({usage_metadata['total_tokens']}) {usage_metadata['input_tokens']}/{usage_metadata['output_token_details']['reasoning']}/{usage_metadata['output_tokens']}"
    )


if __name__ == "__main__":
    # Run the server
    # In production, use a proper ASGI server like gunicorn with uvicorn workers
    uvicorn.run(app, host="0.0.0.0", port=WEBHOOK_PORT)
