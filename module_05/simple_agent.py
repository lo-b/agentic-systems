from dataclasses import dataclass, field

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.constants import START
from langgraph.graph.message import add_messages
from langgraph.graph.state import RunnableConfig, StateGraph
from langgraph.managed import IsLastStep
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, Sequence, cast

assert load_dotenv(), "no .env file found"

SYSTEM_PROMPT = """You are a helpful AI assistant."""

client = MultiServerMCPClient(
    {
        "custom-github": {
            # make sure you start your weather server on port 8000
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
        # "microsoft_learn": {
        #     "url": "https://learn.microsoft.com/api/mcp",
        #     "transport": "streamable_http",
        # },
        # "github": {
        #     "transport": "stdio",
        #     "command": "docker",
        #     "env": {
        #         "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ[
        #             "GITHUB_PERSONAL_ACCESS_TOKEN"
        #         ],
        #         "GITHUB_TOOLSETS": "context,repos",
        #     },
        #     "args": [
        #         "run",
        #         "-i",
        #         "--rm",
        #         "mcp/github",
        #     ],
        # },
    }
)


@dataclass
class InputState:
    """Defines the input state for the agent, representing a narrower interface to the outside world.

    This class is used to define the initial state and structure of incoming data.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )
    """
    Messages tracking the primary execution state of the agent.

    Typically accumulates a pattern of:
    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    4. AIMessage without .tool_calls - agent responding in unstructured format to the user
    5. HumanMessage - user responds with the next conversational turn

    Steps 2-5 may repeat as needed.

    The `add_messages` annotation ensures that new messages are merged with existing ones,
    updating by ID to maintain an "append-only" state unless a message with the same ID is provided.
    """


@dataclass
class State(InputState):
    """Represents the complete state of the agent, extending InputState with additional attributes.

    This class can be used to store any information needed throughout the agent's lifecycle.
    """

    is_last_step: IsLastStep = field(default=False)
    """
    Indicates whether the current step is the last one before the graph raises an error.

    This is a 'managed' variable, controlled by the state machine rather than user code.
    It is set to 'True' when the step count reaches recursion_limit - 1.
    """

    # Additional attributes can be added here as needed.
    # Common examples include:
    # retrieved_documents: List[Document] = field(default_factory=list)
    # extracted_entities: Dict[str, Any] = field(default_factory=dict)
    # api_connections: Dict[str, Any] = field(default_factory=dict)


class Context(BaseModel):
    model: str = Field(default="ollama/qwen3:0.6b", description="model to use")
    pr_id: int = Field(default=2, description="Pull Request (PR) ID")
    repo_name: str = Field(default="SimpleFaas", description="Name of the repository")


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)


async def make_graph(config: RunnableConfig):
    builder = StateGraph(State, input_schema=InputState, context_schema=Context)

    # Define the two nodes we will cycle between
    tools = await client.get_tools()
    builder.add_node(call_model)
    builder.add_node("tools", ToolNode(tools))

    # Set the entrypoint as `call_model`
    # This means that this node is the first one called
    builder.add_edge(START, "call_model")

    def route_model_output(state: State) -> Literal["__end__", "tools"]:
        """Determine the next node based on the model's output.

        This function checks if the model's last message contains tool calls.

        Args:
            state (State): The current state of the conversation.

        Returns:
            str: The name of the next node to call ("__end__" or "tools").
        """
        last_message = state.messages[-1]
        if not isinstance(last_message, AIMessage):
            raise ValueError(
                f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
            )
        # If there is no tool call, then we finish
        if not last_message.tool_calls:
            return "__end__"
        # Otherwise we execute the requested actions
        return "tools"

    # Add a conditional edge to determine the next step after `call_model`
    builder.add_conditional_edges(
        "call_model",
        # After call_model finishes running, the next node(s) are scheduled
        # based on the output from route_model_output
        route_model_output,
    )

    # Add a normal edge from `tools` to `call_model`
    # This creates a cycle: after using tools, we always return to the model
    builder.add_edge("tools", "call_model")

    # Compile the builder into an executable graph
    return builder.compile()


async def call_model(
    state: State, runtime: Runtime[Context]
) -> dict[str, list[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    # Initialize the model with tool binding. Change the model or add more tools here.
    tools = await client.get_tools()
    model = load_chat_model(runtime.context.model).bind_tools(tools)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = (
        "You are a helpful AI assistant.\n\n"
        f"Context:\n- pr_id: {runtime.context.pr_id}\n- repo_name: {runtime.context.repo_name}\n\n"
        "When calling tools, ALWAYS use the pr_id from Context for any parameter named 'pr_id'.\n"
        "Do not guess or default to other values (e.g., 1). If a tool requires pr_id and it's not in the user message, still include the Context pr_id.\n"
    )
    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}
