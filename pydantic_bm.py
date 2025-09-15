import os
import asyncio
from pydantic import BaseModel
from agents import Agent, RunConfig, Runner, OpenAIChatCompletionsModel,RunContextWrapper, handoff
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

if not openai_api_key and gemini_api_key:
    raise ValueError('api key is not set')

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
    model_provider=external_client,
    tracing_disabled=False
)

class EscalationData(BaseModel):
    reason:str
    priority: int

escalation_agent = Agent(name="Escalation Agent")

async def on_handoff(ctx:RunContextWrapper[None], input_data:EscalationData):
    print(f"[Escalation] Reason: {input_data.reason}, Priority:{input_data.priority}")

handoff_obj = handoff(
    agent=escalation_agent,
    on_handoff=on_handoff,
    input_type=EscalationData
)
pydantic_agent = Agent(
    name="pydantic Agent",
    instructions= "Answer Pydantic queries. If you cannot resolve the issue, CALL the tool named "
+        "`escalate` and pass a JSON object matching {reason: str, priority: int}. "
+        "Example tool call: escalate {\"reason\":\"complex validation\", \"priority\":2}",
    handoffs=[handoff_obj]
)

async def main():
    res = await Runner.run(pydantic_agent,"I am facing a critical bug with Pydantic in production and need urgent escalation with priority:1.",run_config=config)
    print(res.final_output)

asyncio.run(main())
