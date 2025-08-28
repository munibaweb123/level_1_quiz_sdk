from agents import Agent, ModelSettings, AsyncOpenAI, Runner, function_tool,OpenAIChatCompletionsModel, RunConfig
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

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
    model="gemini-2.0-flash"

)
config=RunConfig(
    tracing_disabled=False,
    model_provider=external_client
)

@function_tool
def weather(city:str)->str:
    return f"weather for {city} is cloudy"

weather_model=ModelSettings(
    tool_choice='none',
    temperature=0.9,
    max_tokens=200
    )

agent:Agent = Agent(
    name="Haiku Agent",
    instructions="you are a helpful assistant",
    tools=[weather],
    model_settings=weather_model,
    model="gpt-4o-mini"
)

async def new():
    result = await Runner.run(agent,"write the story about panda and a wolf")
    print(result.final_output)

asyncio.run(new())
