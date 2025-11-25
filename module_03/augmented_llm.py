from dotenv import load_dotenv
from rich import print as rprint
from langchain.agents import create_agent

assert load_dotenv(), ".env file empty or missing"

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


agent = create_agent(
    model="ollama:qwen3:0.6b",
   # tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

# Run the agent
res = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

rprint(res)
