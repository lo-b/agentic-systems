import operator

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage
from langchain.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated

assert load_dotenv(), ".env file empty or missing"

model = init_chat_model(
    # "ollama:qwen3:0.6b",  # your local model
    "azure_ai:Ministral-3B",  # model hosted in the cloud
    temperature=0
)


class MessagesState(TypedDict):
    # required to make the model a 'chat' model
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
    ingredients: str


def determine_ingredients(state: dict):
    ai_response = model.invoke(
        [
            SystemMessage(
                content="You are a helpful assistant tasked with "
                        "determining ingredients used in a dish. "
                        "Output the ingredients as a numbered list."
            )
        ]
        + state["messages"]
    )

    return {
        "messages": [ai_response],
        "llm_calls": state.get('llm_calls', 0) + 1,
        "ingredients": ai_response.content
    }


def make_recipe(state: dict):
    """Create a recipe based on the ingredients"""

    ai_response = model.invoke(
        [
            SystemMessage(
                content="You are a helpful assistant that creates simple recipes."
            ),
            HumanMessage(
                content=f"Given these ingredients, create a simple recipe:\n\n{state['ingredients']}"
            )
        ]
    )

    return {
        "messages": [ai_response],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("determine_ingredients", determine_ingredients)
agent_builder.add_node("make_recipe", make_recipe)

# Add edges to connect nodes
agent_builder.add_edge(START, "determine_ingredients")
agent_builder.add_edge("determine_ingredients", "make_recipe")
agent_builder.add_edge("make_recipe", END)

# Compile the agent
agent = agent_builder.compile()

# Show the agent
print(agent.get_graph().draw_ascii())

# Invoke
messages = [HumanMessage(content="Cheesecake")]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()
