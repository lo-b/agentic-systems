from langchain import __version__  as langchain_version
from langchain.messages import HumanMessage
from langgraph.version import __version__ as langgraph_version
from langgraph.graph import END, START, MessagesState, StateGraph
from rich import print as rprint

from dotenv import load_dotenv

assert load_dotenv(), ".env file empty or not present"

rprint("///////////////////////////// healthcheck /////////////////////////////")
rprint("===== Package Versions =====")
rprint("LangChain\t\t:", langchain_version)
rprint("LangGraph\t\t:", langgraph_version)

rprint("===== LangChain/LangGraph testrun =====")
def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "pong"}]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile(name="Getting Started Testrun")
rprint("graph ascii visualization")
rprint(graph.get_graph().draw_ascii())
rprint("run with 'ping' input:")
res = graph.invoke({"messages": [HumanMessage("ping")]})
rprint(res)
rprint("===== View LangSmith tracing ======")
rprint("go to: https://smith.langchain.com/",)