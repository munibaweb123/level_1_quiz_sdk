import asyncio
import os

from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from pydantic_bm import BaseModel
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled, handoff

_: bool = load_dotenv(find_dotenv())

gemini_api_key: str = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(disabled=False)

llm_model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=client
)

class UserContext(BaseModel):
    user_id: str
    subscription_tier: str = "free"
    has_permission: bool

handoff_agent = Agent(
    name="Assistant",
    instructions="You only respond for the user's request and delegate to the expert agent if needed.",
    model=llm_model,
    
)

expert_agent = Agent(
    name="Expert",
    instructions="you are an expert in the field of recursion in programming.",
    model=llm_model,
    

)
# lambda function => argument: expression 
handoff_agent.handoffs=[handoff(expert_agent, is_enabled=lambda ctx,agent: ctx.context.has_permission, tool_name_override="Expert_Assistant", 
                        tool_description_override="you are expert in recursion")]

async def main():
    context = UserContext(
        user_id="1233",
        subscription_tier="free",
        has_permission=False
    )
    context2 = UserContext(
        user_id= "420",
        subscription_tier="premium",
        has_permission=True
    )
    result = await Runner.run(
        starting_agent=handoff_agent,
        input="call the expert agent to explain recursion in programming",
        #context=context
        context=context2
    )
    print(f"Final Result: {result.final_output}")

asyncio.run(main())