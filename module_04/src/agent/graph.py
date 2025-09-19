"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, TypedDict

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langsmith import Client


class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str


@dataclass
class State:
    """Input state for the agent.

    Defines the initial structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    """

    vacancy: str
    summary: str = ""
    draft: str = ""


async def summarize(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    client = Client()
    prompt = await asyncio.to_thread(client.pull_prompt, "summarize-vacancy-prompt")

    model = ChatAnthropic(model_name="claude-3-5-sonnet-latest")
    chain = prompt | model

    try:
        summary = await chain.ainvoke({"vacancy_description": state.vacancy})
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary = "Failed to generate summary"

    return {"summary": summary}


graph = (
    StateGraph(State, context_schema=Context)
    .add_node(summarize)
    .add_edge("__start__", "summarize")
    .compile(name="New Graph")
)
