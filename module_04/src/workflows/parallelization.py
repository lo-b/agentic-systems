"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

import asyncio

# import os
from typing import Any, Dict, TypedDict

# from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph
from langsmith import Client

# INFO: SaaS LLMs using Azure AI Foundry
# _model = AzureAIChatCompletionsModel(
#     model="Ministral-3B",
#     endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
#     credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
# )
_model = ChatOllama(model="qwen3:0.6b", reasoning=True)
_client = Client()


# INFO: define separate input, output and overall states; nicer UX.
class InputState(TypedDict):
    vacancy: str
    cv: str


class OutputState(TypedDict):
    response: str


class OverallState(TypedDict):
    vacancy: str
    job_summary: str
    cv_summary: str
    response: str


async def process_vacancy(state: InputState) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    prompt = await asyncio.to_thread(_client.pull_prompt, "summarize-vacancy-prompt")
    chain = prompt | _model

    try:
        summary = await chain.ainvoke({"vacancy_description": state["vacancy"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary = "Failed to generate summary"

    return {"vacancy": state["vacancy"], "job_summary": summary}


async def process_cv(state: InputState) -> Dict[str, Any]:
    prompt = await asyncio.to_thread(_client.pull_prompt, "summarize-cv")
    chain = prompt | _model

    try:
        summary = await chain.ainvoke({"cv": state["cv"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary = "Failed to generate summary"

    return {"cv": state["cv"], "cv_summary": summary}


def aggregator(state: OverallState):
    """Combine the summaries into a single output"""

    combined = f"JOB SUMMARY:\n{state['job_summary']}\n\n"
    combined += f"CV SUMMARY:\n{state['cv_summary']}\n\n"

    prompt = _client.pull_prompt("cv-outline-from-aggregation")
    chain = prompt | _model
    return {
        "response": chain.invoke(
            {
                "job_summary": state["job_summary"],
                "cv_summary": state["cv_summary"],
            }
        )
    }


parallelization = (
    StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState,
    )
    .add_node(process_cv)
    .add_node(process_vacancy)
    .add_node(aggregator)
    .add_edge(START, "process_cv")
    .add_edge(START, "process_vacancy")
    .add_edge("process_cv", "aggregator")
    .add_edge("process_vacancy", "aggregator")
    .compile(name="Prompt chaining workflow")
)
