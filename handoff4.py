import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, handoff, HandoffInputData

_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

def summarized_news_transfer(data: HandoffInputData) -> HandoffInputData:
    print("\n\n[HANDOFF] Summarizing news transfer...\n\n")
    summarized_conversation = "Get latest tech news."
    
    print("\n\n[ITEM 1]", data.input_history)
    print("\n\n[ITEM 2]", data.pre_handoff_items)
    print("\n\n[ITEM 1]", data.new_items)
    
    return HandoffInputData(
        input_history=summarized_conversation,
        pre_handoff_items=(),
        new_items=(),
    )

@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions="You get latest news about tech community and share it with me.",
    model=llm_model,
    tools=[get_weather],
)

weather_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are weather expert - share weather updates as I travel a lot. For all Tech and News let the NewsAgent handle that part by delegation.",
    model=llm_model,
    tools=[get_weather],
    handoffs=[handoff(agent=news_agent, input_filter=summarized_news_transfer)]
)

res = Runner.run_sync(weather_agent, "Check if there's any news about OpenAI after GPT-5 launch?")
print("\nAGENT NAME", res.last_agent.name)
print("\n[RESPONSE:]", res.final_output)

# Now check the trace in 