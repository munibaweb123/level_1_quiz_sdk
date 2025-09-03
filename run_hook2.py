import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunHooks


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



# Create a system-wide monitoring class
class SystemMonitor(RunHooks):
    def __init__(self):
        self.active_agents = []
        self.tool_usage = {}
        self.handoffs = 0
    
    async def on_agent_start(self, context, agent):
        self.active_agents.append(agent.name)
        print(f"🌅 SYSTEM: {agent.name} is now working")
        print(f"   Active agents so far: {self.active_agents}")
    
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        print(f"📞 SYSTEM: {agent.name} is thinking...")
    
    async def on_llm_end(self, context, agent, response):
        print(f"🧠✨ SYSTEM: {agent.name} finished thinking")
    
    async def on_tool_start(self, context, agent, tool):
        tool_name = tool.name
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        print(f"🔨 SYSTEM: {tool_name} used {self.tool_usage[tool_name]} times")
    
    async def on_tool_end(self, context, agent, tool, result):
        print(f"✅🔨 SYSTEM: {agent.name} finished using {tool.name}")
    
    async def on_handoff(self, context, from_agent, to_agent):
        self.handoffs += 1
        print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF #{self.handoffs}: {from_agent.name} → {to_agent.name}")
    
    async def on_agent_end(self, context, agent, output):
        print(f"✅ SYSTEM: {agent.name} completed their work")
        print(f"📊 STATS: {len(self.active_agents)} agents used, {self.handoffs} handoffs")

# Create your agents
customer_service = Agent(name="CustomerService")
tech_support = Agent(name="TechnicalSupport")
billing_manager = Agent(name="BillingManager")

# Create the system monitor
system_monitor = SystemMonitor()

# Run with system-wide monitoring
async def main():
    result = await Runner.run(
        starting_agent=customer_service,
        input="I need help with my account",
        hooks=system_monitor,  # This monitors EVERYTHING
    )
    print(f"Final output: {result.final_output}")

asyncio.run(main())