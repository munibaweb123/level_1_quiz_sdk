
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
def add(a: int, b: int) -> int:
    """Adds two integers together."""
    return a + b

math_agent = Agent(
    name="MathAgent",
    instructions="You are an expert at math. Use your tools to solve problems.",
    tools=[add],
    model='gpt-4o-mini'
)

router_agent = Agent(
    name="RouterAgent",
    instructions="You are a router. If the user asks a math question, you must handoffs to the MathAgent. Otherwise, say you cannot help.",
    tools = [],
    model='gpt-4o-mini'
)


res = Runner.run_sync(router_agent, "What is 5 plus 7?")
print(res.final_output)
print(res.last_agent)

# Given the code base, what is the most likely initial outcome of the following call? Runner.run_sync(router_agent, "What is 5 plus 7?")
# A. The RouterAgent will respond, "I cannot help,"
# B. The RouterAgent will generate a Handoff to the MathAgent based on its instructions. 
# C. The code will raise an error because RouterAgent tries to access the add tool, which it doesn't have. 
# D. The RouterAgent will answer "12" directly, ignoring its instructions to handoff.