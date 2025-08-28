import asyncio
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

import os
from dotenv import load_dotenv
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

gemini_api_key = os.getenv('GEMINI_API_KEY')

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

llm_model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.0-flash"
)

#set_tracing_disabled(True)

async def model_config():
    agent: Agent = Agent(
        name="Haiku Agent",
        instructions="you are a helpful assistant",
        model=llm_model

    )

    result = await Runner.run(agent, "write a story about AI")
    print(result.final_output)

asyncio.run(model_config())