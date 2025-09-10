import asyncio
import os

from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import Agent, HandoffInputData, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled, handoff
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

_: bool = load_dotenv(find_dotenv())

gemini_api_key: str = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(disabled=False)

llm_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

def summarized_news_transfer(data: HandoffInputData)-> HandoffInputData:
    print("\n[Handoff] Summarizing new transfer..\n")
    summarized_conversation = "Get latest tech news"
    print("\n\n[ITEM 1]", data.input_history)
    print("\n\n[ITEM 2]",data.pre_handoff_items)
    print("\n\n[ITEM 3]",data.new_items)

    return HandoffInputData(
        input_history=summarized_conversation,
        pre_handoff_items=(),
        new_items=(),
    )

@function_tool
def get_weather(city:str)->str:
    return f"The weather in {city} is sunny with a high of 75°F."

news_agent: Agent = Agent(
    name="NewsAgent",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX} You get latest news about tech community and share it with me.",
    model=llm_model,
    tools=[get_weather],
)

weather_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="You are weather expert - share weather updates as I travel a lot. For all Tech and News let the NewsAgent handle that part by delegation.",
    model=llm_model,
    tools=[get_weather],
    handoffs=[handoff(agent=news_agent,input_filter=summarized_news_transfer)]
    #handoffs=[handoff(agent=news_agent,input_filter=handoff_filters.remove_all_tools)]
)

async def main():
    result = await Runner.run(
        starting_agent=weather_agent,
        input="What's the latest news in tech and what's the weather like in New York?",
    )
    print(f"Final Result: {result.final_output}")
    print(f"last agent: {result.last_agent.name}")

asyncio.run(main())