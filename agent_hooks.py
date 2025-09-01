from dataclasses import dataclass
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

@dataclass
class AgentHooksContext:
    agent_start:str
    llm_start:str

class customizeHook(AgentHooks):
    def __init__(self, display_name: str):
        self.display_name = display_name
        self.count = 0
    async def on_start(self,context: RunContextWrapper[AgentHooksContext], agent: Agent)->None:
        self.count += 1
        print(f"{self.display_name} {self.count} {agent.name} has been started with context {context.context.agent_start}")
    async def on_llm_start(self, context:RunContextWrapper[AgentHooksContext], agent, system_prompt, input_items):
        self.count += 1
        print(f"📞 {agent.name} {self.count} is asking AI for help with context {context.context.llm_start}")
        print(f"System Prompt: {system_prompt}")
        print(f"Input Items: {input_items}")
    async def on_llm_end(self, context:RunContextWrapper[AgentHooksContext], agent, response):
        self.count += 1
        print(f"🧠✨ {agent.name} {self.count} got AI response")
        print(f"Response: {response} with context {context.context.llm_start}")
    async def on_tool_start(self, context, agent, tool):
        self.count += 1
        print(f"🔨 {agent.name} {self.count} is using {tool.name}")
    async def on_tool_end(self, context, agent, tool, result):
        self.count += 1
        print(f"✅ {agent.name} {self.count} finished using {tool.name}")
    
    async def on_handoff(self, context, agent, source):
        self.count += 1
        print(f"🏃‍♂️➡️🏃‍♀️ {agent.name} {self.count} received work from {source.name}")
        print(f"   Work is being transferred due to specialization")
    async def on_end(self, context, agent, output):
        self.count += 1
        print(f"🎉 {agent.name} {self.count} completed the task!")

@function_tool
async def get_weather(ctx:RunContextWrapper, location:str)->str:
    return f"The weather in {location} is sunny"


greet = Agent(
    name="Greeting Agent",
    instructions="You are a helpful assistant that greets user in islamic way",
    handoff_description="Islamic greeting Agent",
    hooks=customizeHook("Greeting Agent"),
)
manager_agent = Agent(
    name="Manager Agent",
    instructions="only use weather tool to fetch weather and greet tool to greet user cannot answer by yourself",
    handoffs=[greet],
    hooks=customizeHook("Manager Agent"),
    tools=[get_weather],
    handoff_description="Manager Agent"
)

async def main():
    #agent_context = AgentHooksContext(agent_start="Starting the agent")
    result = await Runner.run(
        starting_agent=manager_agent,
        input="Hello, tell me the weather in Paris and greet me",
        context=AgentHooksContext(agent_start="Starting the agent",llm_start="llm is about to start"),
        run_config=config,
    )
    print(result.final_output)

asyncio.run(main())
