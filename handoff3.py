import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, handoff, RunContextWrapper
from pydantic_bm import BaseModel
_: bool = load_dotenv(find_dotenv())
#from agents import enable_verbose_stdout_logging
#enable_verbose_stdout_logging()

# ONLY FOR TRACING
#os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

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

class Weather(BaseModel):
    city:str
    reason:str

@function_tool
def get_weather(city: str) -> str:
    """A simple function to get the weather for a user."""
    return f"The weather for {city} is sunny."


# define on_handoff callback
async def on_handoff_callback(ctx: RunContextWrapper[Weather],input_data:Weather):
    print(f"\n[HANDOFF] delegating with input: {input_data} ")
    #print(f"city: {ctx.context.city}")
    #print(f"reason: {ctx.context.reason}")
    return input_data

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions="You get latest news about tech community and share it with me.",
    model=llm_model,
    tools=[get_weather],
)


news_tool=   handoff(
            
            agent=news_agent,
            on_handoff=on_handoff_callback,
            input_type=Weather,  # optional: agar structured input chahiye
            tool_name_override="latest_news",
            tool_description_override="latest tech news"
        )
    

weather_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are weather expert - share weather updates as I travel a lot. For all Tech and News let the NewsAgent handle that part by delegation.",
    model=llm_model,
    tools=[get_weather],
    handoffs=[news_tool]
)



res = Runner.run_sync(weather_agent, "Check if there's any news about openai release and weather of karachi?")
print("\nAGENT NAME", res.last_agent.name)
print("\n[RESPONSE:]", res.final_output)
print("tool name is: ",news_tool.tool_name)


# Now check the trace in 