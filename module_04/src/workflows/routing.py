from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from typing_extensions import Annotated, Literal, TypedDict, cast

_llm = ChatOllama(model="qwen3:0.6b", reasoning=True)


# Schema for structured output to use as routing logic
class Route(TypedDict):
    step: Annotated[
        Literal["poem", "story", "joke"], "The next step in the routing process"
    ]


# Augment the LLM with schema for structured output
_router = _llm.with_structured_output(Route)


class State(TypedDict):
    input: str
    decision: str
    output: str


# Nodes
def llm_call_1(state: State):
    """Write a story"""

    result = _llm.invoke(state["input"])
    return {"output": result.content}


def llm_call_2(state: State):
    """Write a joke"""

    result = _llm.invoke(state["input"])
    return {"output": result.content}


def llm_call_3(state: State):
    """Write a poem"""

    result = _llm.invoke(state["input"])
    return {"output": result.content}


def llm_call_router(state: State):
    """Route the input to the appropriate node"""

    # Run the augmented LLM with structured output to serve as routing logic
    decision = _router.invoke(
        [
            SystemMessage(
                content="Route the input to story, joke, or poem based on the user's request."
            ),
            HumanMessage(content=state["input"]),
        ]
    )

    decision = cast(Route, decision)

    return {"decision": decision["step"]}


# Conditional edge function to route to the appropriate node
def route_decision(state: State):
    # Return the node name you want to visit next
    if state["decision"] == "story":
        return "llm_call_1"
    elif state["decision"] == "joke":
        return "llm_call_2"
    elif state["decision"] == "poem":
        return "llm_call_3"


# Build workflow
router_workflow = (
    StateGraph(State)
    .add_node("llm_call_1", llm_call_1)
    .add_node("llm_call_2", llm_call_2)
    .add_node("llm_call_3", llm_call_3)
    .add_node("llm_call_router", llm_call_router)
    .add_edge(START, "llm_call_router")
    .add_conditional_edges(
        "llm_call_router",
        route_decision,
        {  # Name returned by route_decision : Name of next node to visit
            "llm_call_1": "llm_call_1",
            "llm_call_2": "llm_call_2",
            "llm_call_3": "llm_call_3",
        },
    )
    .add_edge("llm_call_1", END)
    .add_edge("llm_call_2", END)
    .add_edge("llm_call_3", END)
    .compile()
)
