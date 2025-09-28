import operator

from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from typing_extensions import Annotated, TypedDict

# llm = ChatOllama(model="granite3-moe:3b")
llm = AzureAIChatCompletionsModel(model="Ministral-3B")


class Section(TypedDict):
    name: Annotated[str, "Name for this section of the report."]
    description: Annotated[
        str,
        "Brief overview of the main topics and concepts to be covered in this section.",
    ]


class Sections(TypedDict):
    sections: Annotated[list[Section], "Sections of the report."]


planner = llm.with_structured_output(Sections)


class State(TypedDict):
    topic: str  # Report topic
    sections: list[Section]  # List of report sections
    completed_sections: Annotated[
        list, operator.add
    ]  # All workers write to this key in parallel
    final_report: str  # Final report


class WorkerState(TypedDict):
    section: Section
    completed_sections: Annotated[list, operator.add]


def orchestrator(state: State):
    """Orchestrator that generates a plan for the report"""

    # Generate queries
    report_sections = planner.invoke(
        [
            SystemMessage(content="Generate a plan for the report."),
            HumanMessage(content=f"Here is the report topic: {state['topic']}"),
        ]
    )

    return {"sections": report_sections["sections"]}


def llm_call(state: WorkerState):
    """Worker writes a section of the report"""

    # Generate section
    section = llm.invoke(
        [
            SystemMessage(
                content="Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."
            ),
            HumanMessage(
                content=f"Here is the section name: {state['section']['name']} and description: {state['section']['description']}"
            ),
        ]
    )

    # Write the updated section to completed sections
    return {"completed_sections": [section.content]}


def synthesizer(state: State):
    """Synthesize full report from sections"""

    completed_sections = state["completed_sections"]

    completed_report_sections = "\n\n---\n\n".join(completed_sections)

    return {"final_report": completed_report_sections}


# Conditional edge function to create llm_call workers that each write a section of the report
def assign_workers(state: State):
    """Assign a worker to each section in the plan"""

    # Kick off section writing in parallel via Send() API
    return [Send("llm_call", {"section": s}) for s in state["sections"]]


orchestrator_worker_builder = (
    StateGraph(State)
    .add_node("orchestrator", orchestrator)
    .add_node("llm_call", llm_call)
    .add_node("synthesizer", synthesizer)
    .add_edge(START, "orchestrator")
    .add_conditional_edges("orchestrator", assign_workers, ["llm_call"])
    .add_edge("llm_call", "synthesizer")
    .add_edge("synthesizer", END)
)

orchestrator_workers = orchestrator_worker_builder.compile()
