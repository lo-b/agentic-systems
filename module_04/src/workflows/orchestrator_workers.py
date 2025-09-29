import operator

from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from typing_extensions import Annotated, TypedDict

# llm = ChatOllama(model="granite3-moe:3b")
llm = AzureAIChatCompletionsModel(model="Ministral-3B")


class Improvement(TypedDict):
    name: Annotated[str, "Name for this section of improvement."]
    description: Annotated[
        str,
        "Brief overview of the what should be improved.",
    ]


class Improvements(TypedDict):
    sections: Annotated[list[Improvement], "CV improvements."]


planner = llm.with_structured_output(Improvements)


class State(TypedDict):
    cv: str
    job_description: str
    sections: list[Improvement]  # List of report sections
    completed_sections: Annotated[
        list, operator.add
    ]  # All workers write to this key in parallel
    final_report: str  # Final report


class WorkerState(TypedDict):
    section: Improvement
    completed_sections: Annotated[list, operator.add]


def orchestrator(state: State):
    """Orchestrator that generates CV improvements, based on a job description/vacancy."""

    # Generate queries
    report_sections = planner.invoke(
        [
            SystemMessage(
                content="""You are an expert CV consultant and ATS optimization specialist. Analyze the provided CV 
                against the job description to identify specific, actionable improvements.

                Your task is to generate a comprehensive list of targeted improvements that will:
                1. Better align the CV with the job requirements
                2. Optimize for ATS (Applicant Tracking System) compatibility
                3. Highlight relevant skills and experiences
                4. Improve keyword matching and relevance
                5. Enhance overall presentation and impact

                Focus on these improvement categories:
                - **Skills Alignment**: Missing technical/soft skills mentioned in the job description
                - **Experience Relevance**: How to better showcase relevant experience and achievements
                - **Keyword Optimization**: Important keywords and phrases that should be incorporated
                - **Formatting & Structure**: ATS-friendly formatting and logical flow improvements
                - **Quantifiable Achievements**: Areas where metrics and results should be added
                - **Industry Language**: Professional terminology and language that matches the role
                - **Section Enhancement**: Improvements to specific CV sections (summary, experience, education, etc.)

                For each improvement, provide:
                - A clear, descriptive name that indicates the specific area of focus
                - A detailed description that explains what needs to be changed and why it matters for this specific role

                Prioritize improvements that will have the highest impact on job application success."""
            ),
            HumanMessage(content=f"**CV to Analyze:**\n{state['cv']}"),
            HumanMessage(
                content=f"**Target Job Description:**\n{state['job_description']}\n\nPlease analyze the CV against this job description and generate specific improvement recommendations."
            ),
        ]
    )

    return {"sections": report_sections["sections"]}


def llm_call(state: WorkerState):
    """Worker writes an improvement to tailor CV to the job description."""

    # Get the full state context (you'll need to modify the workflow to pass this)
    # For now, we'll work with the section information provided

    # Generate section
    section = llm.invoke(
        [
            SystemMessage(
                content="""You are a professional CV writing expert. Your task is to provide specific, actionable 
                improvement advice for tailoring a CV to a target job.

                For the given improvement area, provide:

                **Structure your response as follows:**
                ## {Improvement Name}

                ### Why This Matters
                Briefly explain why this improvement is important for job application success and ATS optimization.

                ### Current Gap Analysis
                Identify what's currently missing or could be enhanced.

                ### Specific Recommendations
                Provide concrete, actionable steps including:
                - Exact text suggestions where applicable
                - Keyword recommendations
                - Formatting improvements
                - Positioning advice

                ### Implementation Examples
                Where relevant, provide before/after examples or sample text that demonstrates the improvement.
                ### Impact Assessment
                Explain how this change will improve the CV's effectiveness for the target role.

                **Guidelines:**
                - Be specific and actionable rather than generic
                - Focus on ATS optimization and keyword relevance
                - Provide concrete examples and suggested text when possible
                - Consider both human recruiters and automated systems
                - Ensure recommendations are realistic and achievable
                - Use professional, clear language
                - Format using markdown for readability"""
            ),
            HumanMessage(
                content=f"""Please provide detailed improvement advice for:
                **Improvement Focus:** {state["section"]["name"]}

                **Improvement Description:** {state["section"]["description"]}

                Provide comprehensive, actionable guidance following the structure outlined in the system message."""
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
