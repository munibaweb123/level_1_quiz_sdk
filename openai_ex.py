import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise ValueError("Your API key is not set")

# Create a single OpenAI async client
openai_client = AsyncOpenAI(api_key=openai_api_key)

# Wrap models properly
spanish_model = OpenAIChatCompletionsModel(
    openai_client=openai_client, model="gpt-5-mini"
)
english_model = OpenAIChatCompletionsModel(
    openai_client=openai_client, model="gpt-5-nano"
)
triage_model = OpenAIChatCompletionsModel(
    openai_client=openai_client, model="gpt-5"
)

# Define agents
spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    model=spanish_model,
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English.",
    model=english_model,
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    model=triage_model,
)

# Run
async def main():
    #result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    result = await Runner.run(triage_agent, "what day is today?")
    print(result.final_output)

asyncio.run(main())
