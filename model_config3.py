from agents import Agent, Runner, set_tracing_disabled, set_default_openai_api, OpenAIChatCompletionsModel, set_default_openai_client
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
load_dotenv()

set_tracing_disabled(True)
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

set_default_openai_api('chat_completions')
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

set_default_openai_client(external_client)

agent:Agent = Agent(
    name="Haiku Agent",
    instructions="you are a helpful assistant, you always respond haikus",
    model="gemini-1.5-flash"
)

result = Runner.run_sync(agent,"what is openai agents sdk?" )
print(result.final_output)