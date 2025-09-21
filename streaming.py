import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, OpenAIChatCompletionsModel, RunConfig, Runner, function_tool

load_dotenv(find_dotenv())
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

config = RunConfig(
    model=llm_model,
    tracing_disabled=False,
    model_provider=external_client
)

@function_tool
def get_weather(city: str):
    "fetch weather for provided city"
    return f"weather for {city} is cloudy"

async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant use tool to fetch weather and tell jokes.",
        tools=[get_weather],
        tool_use_behavior="stop_on_first_tool",
    )

    
    result = Runner.run_streamed(
        agent,
        input="Tell me a short joke and also the weather in Karachi.",
        run_config=config,
        max_turns=3
    )

    # ✅ Stream events before final_output
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)

    # ✅ Final output is available after streaming
    print("\n\nFinal Output:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
