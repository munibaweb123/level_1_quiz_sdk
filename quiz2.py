import asyncio
from agents import Agent, AsyncOpenAI, Runner, function_tool,OpenAIChatCompletionsModel, RunConfig ,enable_verbose_stdout_logging
import os
from dotenv import load_dotenv
load_dotenv()
enable_verbose_stdout_logging()
gemini_api_key = os.getenv('GEMINI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not gemini_api_key and openai_api_key:
    raise ValueError('your api keys are not set')

external_client=AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

llm_model:OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.5-flash-lite"

)
config=RunConfig(
    tracing_disabled=False,
    model=llm_model,
    model_provider=external_client
)

@function_tool
async def get_weather(city:str):
    "args: city, tell the weather to user for the given city"
    return f"the weather for {city} is sunny"

agent:Agent=Agent(
    name="assistant",
    instructions="you are a helpful agent, use tool to fetch weather",
    tools=[get_weather]
)
async def main():
    res =await Runner.run(agent,"what is the weather of Lahore",max_turns=2,run_config=config)
    print(res.final_output)

asyncio.run(main())