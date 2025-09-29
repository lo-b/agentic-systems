# import os

# from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langsmith.client import Client
from typing_extensions import Annotated, Literal, TypedDict, cast

_langsmith_client = Client()

_llm = ChatOllama(model="qwen3:0.6b", reasoning=True)
# _llm = AzureAIChatCompletionsModel(
#     model="Ministral-3B",
#     endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
#     credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
# )


class Route(TypedDict):
    step: Annotated[
        Literal["low_code", "data_engineering", "integration_development"],
        "The next step in the routing process",
    ]


_router = _llm.with_structured_output(Route)


class State(TypedDict):
    input: str
    decision: str
    output: str


def low_code(state: State):
    prompt = _langsmith_client.pull_prompt("low_code_cv_outline")
    chain = prompt | _llm
    result = chain.invoke({"job_description": state["input"]})
    return {"output": result.content}


def data_engineering(state: State):
    prompt = _langsmith_client.pull_prompt("data_engineering_cv_outline")
    chain = prompt | _llm
    result = chain.invoke({"job_description": state["input"]})
    return {"output": result.content}


def integration_development(state: State):
    prompt = _langsmith_client.pull_prompt("integration_developer_cv_outline")
    chain = prompt | _llm
    result = chain.invoke({"job_description": state["input"]})
    return {"output": result.content}


def router(state: State):
    """Route the input to the appropriate node"""

    decision = _router.invoke(
        [
            SystemMessage(
                content=(
                    "Route the input to 'low_code', 'data_engineering'"
                    " or 'integration_development' based on the user's request."
                )
            ),
            HumanMessage(content=state["input"]),
        ]
    )

    decision = cast(Route, decision)

    return {"decision": decision["step"]}


def route_decision(state: State):
    """Routes to the decision its corresponding node."""
    if state["decision"] == "low_code":
        return "low_code"
    elif state["decision"] == "data_engineering":
        return "data_engineering"
    elif state["decision"] == "integration_development":
        return "integration_development"


simple_routing = (
    StateGraph(State)
    .add_node("low_code", low_code)
    .add_node("data_engineering", data_engineering)
    .add_node("integration_development", integration_development)
    .add_node("router", router)
    .add_edge(START, "router")
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
    .compile()
)
