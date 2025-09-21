
from agents import Agent, function_tool, Runner
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
    model="gemini-2.5-flash"

)
config=RunConfig(
    tracing_disabled=False,
    model=llm_model,
    model_provider=external_client
)

@function_tool
def add(num1:int,num2:int):
    return num1+num2

math_agent = Agent(
    name="math agent",
    instructions="you are helpful assistant don't use tool",
    tools=[add],
    model_settings=ModelSettings(temperature=1.9, top_p=0.1, max_tokens=1500, tool_choice=None)
)

res = Runner.run_sync(math_agent,"what is agentic ai",run_config=config)
print(res.final_output)