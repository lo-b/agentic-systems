from typing import Annotated

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


# INFO: has a 'messages' containing a list of 'BaseMessags'; enables 'chat' mode.
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


graph_builder = StateGraph(State)

llm = ChatOllama(model="qwen3:0.6b", reasoning=True)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# Add the chatbot node
graph_builder.add_node("chatbot", chatbot)

# Connect START to chatbot
graph_builder.add_edge(START, "chatbot")

# Compile normally - no interrupt needed for basic chat
basic_chatbot = graph_builder.compile()
