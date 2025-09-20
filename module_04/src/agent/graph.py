"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

# import os
import asyncio
from typing import Any, Dict, TypedDict

# from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langsmith import Client

# WARN: Unsure if this is problematic w.r.t. pregel/LangGraph's async requirement/preference.
_client = Client()


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


class OverallState(TypedDict):
    vacancy: str
    summary: str
    response: str


async def summarize(state: InputState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    prompt = await asyncio.to_thread(_client.pull_prompt, "summarize-vacancy-prompt")

    # INFO: SaaS LLMs using Azure AI Foundry
    # model = AzureAIChatCompletionsModel(
    #     model="Ministral-3B",
    #     endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    #     credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
    # )
    model = ChatOllama(model="qwen3:0.6b", reasoning=True)
    chain = prompt | model

    try:
        summary = await chain.ainvoke({"vacancy_description": state["vacancy"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary = "Failed to generate summary"

    return {"vacancy": state["vacancy"], "summary": summary}


async def create_draft(state: OverallState) -> Dict[str, Any]:
    prompt = await asyncio.to_thread(_client.pull_prompt, "create-cv-draft")
    model = ChatOllama(model="qwen3:0.6b", reasoning=True)
    chain = prompt | model

    try:
        draft = await chain.ainvoke({"job_summary": state["summary"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        draft = "Failed to generate summary"

    return {"response": draft}


graph = (
    StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState,
        context_schema=Context,
    )
    .add_node(summarize)
    .add_node(create_draft)
    .add_edge("__start__", "summarize")
    .add_edge("summarize", "create_draft")
    .compile(name="New Graph")
)
