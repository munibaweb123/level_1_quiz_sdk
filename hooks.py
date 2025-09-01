from agents import Agent, AgentHooks, RunContextWrapper, Runner, OpenAIChatCompletionsModel, RunConfig, function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
openai_key = os.getenv('OPENAI_API_KEY')
gemini_api = os.getenv('GEMINI_API_KEY')
if not openai_key or not gemini_api:
    raise ValueError('API keys not set properly')

external_client = AsyncOpenAI(
    api_key=gemini_api,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.0-flash"
)
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=False
)

class customizeHook(AgentHooks):
    def __init__(self, display_name: str):
        self.display_name = display_name
        self.count = 0
    async def on_start(self,context: RunContextWrapper[None], agent: Agent)->None:
        self.count += 1
        print(f"{self.display_name} {self.count} {agent.name} has been started")


greet = Agent(
    name="Greeting Agent",
    instructions="You are a helpful assistant that greets user in islamic way",
    handoff_description="Islamic greeting Agent"
)
manager_agent = Agent(
    name="Manager Agent",
    instructions="only use greet to greet user cannot answer by yourself",
    handoffs=[greet],
    hooks=customizeHook("Manager Agent"),
    handoff_description="Manager Agent"
)

async def main():
    result = await Runner.run(
        starting_agent=manager_agent,
        input="Hello",
        run_config=config,
    )
    print(result.final_output)

asyncio.run(main())
