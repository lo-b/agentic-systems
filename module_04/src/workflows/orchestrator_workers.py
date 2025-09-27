from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph

_llm = ChatOllama(model="deepseek-r1:7b")
analysis_prompt = """Role: Expert IT recruitment analyst

Task: Extract key requirements from this IT consultancy job vacancy.

Output Format:
CRITICAL REQUIREMENTS: [must-haves]
PREFERRED: [nice-to-haves] 
TECHNOLOGIES: [specific tools/platforms]
EXPERIENCE: [years + domains]
CONSULTING SKILLS: [client-facing competencies]

Job Vacancy: {job_vacancy}
"""


class State(MessagesState):
    vacancy: str
    result: str


def analysis(state: State):
    pt = ChatPromptTemplate.from_messages([("system", analysis_prompt)])
    p = pt.invoke({"job_vacancy": state["vacancy"]})
    return {"messages": _llm.invoke(p)}


graph_builder = (
    StateGraph(State)
    .add_node(analysis)
    .add_edge(START, "analysis")
    .add_edge("analysis", END)
)

orchestrator_workers = graph_builder.compile(name="Orchestrator-workers workflow")
