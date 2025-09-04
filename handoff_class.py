import asyncio
import os

from dotenv import load_dotenv, find_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import Agent, OpenAIChatCompletionsModel, RunConfig, Runner, set_tracing_disabled, handoff

_: bool = load_dotenv(find_dotenv())

gemini_api_key: str = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_tracing_disabled(disabled=False)

llm_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

config = RunConfig(
    model=llm_model,
    model_provider=client,
    tracing_disabled=False
)

billing_agent = Agent(name="Billing Agent")
refund_agent = Agent(name="Refund Agent")

triage_agent = Agent(name="Triage Agent", handoffs=[billing_agent, handoff(refund_agent)])

async def handoff():
    result = await Runner.run(triage_agent,"i want to refund money from bank",run_config=config)
    print(result.final_output)

asyncio.run(handoff())

