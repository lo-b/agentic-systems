from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ModelRequest,
    dynamic_prompt,
)
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field

from module_05.prompts import DEFAULT, SUMMARIZE_PR, WALKTHROUGH

assert load_dotenv(), "no .env file found"


class Context(BaseModel):
    model: str = Field(
        title="Model identifier",
        default="ollama:qwen3:0.6b",
        description="provider and model name",
        examples=["azure_ai:Ministral-3B"],
    )
    pr_id: int = Field(title="Pull Request (PR) ID", gt=0)
    repo_name: str = Field(
        title="GitHub repository name",
        default="simple-faas",
    )
    pr_action: str = Field(
        title="PR action to take", examples=["summary", "walkthrough"]
    )


@dynamic_prompt
def pr_action_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on pr_aciton role."""
    context = Context.model_validate(request.runtime.context)
    prompt = DEFAULT

    if context.pr_action == "summary":
        prompt = SUMMARIZE_PR
    elif context.pr_action == "walkthrough":
        prompt = WALKTHROUGH

    return PromptTemplate.from_template(prompt).format(
        pr_id=context.pr_id, repo_name=context.repo_name
    )


async def make_graph(graphConfig: RunnableConfig):
    config = graphConfig.get("configurable", {})
    client = MultiServerMCPClient(
        {
            "custom-github": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()

    agent = create_agent(
        model=config.get("model", "ollama:qwen3:0.6b"),
        tools=tools,
        middleware=[
            pr_action_prompt,
            ModelCallLimitMiddleware(  # type: ignore[reportArgumentType]
                thread_limit=10,  # Max 10 calls per thread (across runs)
                run_limit=5,  # Max 5 calls per run (single invocation)
                exit_behavior="end",  # Or "error" to raise exception
            ),
        ],
        context_schema=Context,
    )

    return agent
