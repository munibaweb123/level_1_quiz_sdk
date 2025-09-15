# pydantic 
import asyncio
import os
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, RunConfig, RunContextWrapper, handoff
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()
#tracing
openai_api_key = os.getenv('OPENAI_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

openai_model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.5-flash"
)

config = RunConfig(
    model=openai_model,
    tracing_disabled=False
)

class PydanticData(BaseModel):
    priority:str
    reason:str
    

async def on_handoff(ctx:RunContextWrapper[PydanticData],input:PydanticData):
    print(f"input data is:{input.priority} and {input.reason}")
    #return f"[handoff escalated with]: {ctx.context.priority} with reason {ctx.context.reason} "

escalation_agent = Agent(
    name="Escalation Agent",
    instructions="you deal with escalated queries",

)

handoff_obj = handoff(agent=escalation_agent,on_handoff=on_handoff,
                      tool_description_override="answer escalated query",input_type=PydanticData)

pydantic_agent = Agent(
    name= "Pydantic Agent",
    instructions="you handle pydantic queries if need to escalate then escalate with priority and reason",
    handoffs=[handoff_obj]
)

print(handoff_obj.tool_name)
async def main():
    res = await Runner.run(starting_agent=pydantic_agent,
                           input="tell me about pydantic validation in openai agents sdk with priority 1 and reason",
                           run_config=config)
    print(res.final_output)
    print(res.last_agent.name)

asyncio.run(main())
    