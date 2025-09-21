import asyncio

# import os
# from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langsmith.client import Client
from typing_extensions import Annotated, Any, Literal, TypedDict, cast

_langsmith_client = Client()

_llm = ChatOllama(model="qwen3:0.6b", reasoning=True)
# _llm = AzureAIChatCompletionsModel(
#     model="Ministral-3B",
#     endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
#     credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
# )


class Route(TypedDict):
    step: Annotated[
        Literal[
            "low_code",
            "data_engineering",
            "integration_development",
        ],
        "The next step in the routing process",
    ]


_router = _llm.with_structured_output(Route)


class InputState(TypedDict):
    vacancy: str


class OutputState(TypedDict):
    response: str


class OverallState(TypedDict):
    vacancy: str
    summary: str
    draft: str
    response: str
    decision: str


async def summarize(state: InputState) -> dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    prompt = await asyncio.to_thread(
        _langsmith_client.pull_prompt, "summarize-vacancy-prompt"
    )
    chain = prompt | _llm

    try:
        summary = await chain.ainvoke({"vacancy_description": state["vacancy"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        summary = "Failed to generate summary"

    return {"vacancy": state["vacancy"], "summary": summary.content}


async def create_draft(state: OverallState) -> dict[str, Any]:
    prompt = await asyncio.to_thread(_langsmith_client.pull_prompt, "create-cv-draft")
    chain = prompt | _llm

    try:
        draft = await chain.ainvoke({"job_summary": state["summary"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        draft = "Failed to generate summary"

    return {"draft": draft.content}


async def create_outline(state: OverallState) -> dict[str, Any]:
    prompt = await asyncio.to_thread(_langsmith_client.pull_prompt, "create-cv-outline")
    chain = prompt | _llm

    try:
        cv_outline = await chain.ainvoke({"cv_draft": state["draft"]})
    except Exception as e:
        print(f"Error during summarization: {e}")
        cv_outline = "Failed to generate summary"

    return {"response": cv_outline.content}


def low_code(state: OverallState):
    prompt = _langsmith_client.pull_prompt("low_code_cv_outline")
    chain = prompt | _llm
    result = chain.invoke({"job_description": state["draft"]})
    return {"response": result.content}


def data_engineering(state: OverallState):
    prompt = _langsmith_client.pull_prompt("data_engineering_cv_outline")
    chain = prompt | _llm
    result = chain.invoke({"job_description": state["draft"]})
    return {"response": result.content}


def integration_development(state: OverallState):
    prompt = _langsmith_client.pull_prompt("integration_developer_cv_outline")
    chain = prompt | _llm
    result = chain.invoke({"job_description": state["draft"]})
    return {"response": result.content}


def router(state: OverallState):
    """Route the input to the appropriate node"""

    decision = _router.invoke(
        [
            SystemMessage(
                content=(
                    "Route the input to 'low_code', 'data_engineering'"
                    " or 'integration_development' based on the user's request."
                )
            ),
            HumanMessage(content=state["draft"]),
        ]
    )

    decision = cast(Route, decision)

    return {"decision": decision["step"]}


def route_decision(state: OverallState):
    """Routes to the decision its corresponding node."""
    if state["decision"] == "low_code":
        return "low_code"
    elif state["decision"] == "data_engineering":
        return "data_engineering"
    elif state["decision"] == "integration_development":
        return "integration_development"


chained_routing = (
    StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState,
    )
    .add_node(summarize)
    .add_node(create_draft)
    .add_node(router)
    .add_node(low_code)
    .add_node(data_engineering)
    .add_node(integration_development)
    .add_edge(START, "summarize")
    .add_edge("summarize", "create_draft")
    .add_edge("create_draft", "router")
    .add_conditional_edges(
        "router",
        route_decision,
        {
            "low_code": "low_code",
            "data_engineering": "data_engineering",
            "integration_development": "integration_development",
        },
    )
    .add_edge("low_code", END)
    .add_edge("data_engineering", END)
    .add_edge("integration_development", END)
    .compile(name="Chained routing")
)
