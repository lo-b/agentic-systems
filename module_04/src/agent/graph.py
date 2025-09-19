"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

import asyncio
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


# INFO: define separate input, output and overall states; nicer UX.
class InputState(TypedDict):
    vacancy: str


class OutputState(TypedDict):
    response: str


class OverallState(InputState, OutputState):
    pass


async def summarize(state: InputState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    client = Client()
    prompt = await asyncio.to_thread(client.pull_prompt, "summarize-vacancy-prompt")

    model = ChatAnthropic(model_name="claude-3-5-sonnet-latest")
    chain = prompt | model

    try:
        summary = await chain.ainvoke({"vacancy_description": state["vacancy"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary = "Failed to generate summary"

    return {"vacancy": state["vacancy"], "response": summary}


graph = (
    StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState,
        context_schema=Context,
    )
    .add_node(summarize)
    .add_edge("__start__", "summarize")
    .compile(name="New Graph")
)
