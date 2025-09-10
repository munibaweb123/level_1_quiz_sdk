from agents import Agent,Runner,OpenAIChatCompletionsModel,function_tool,set_default_openai_key,set_default_openai_client
import os
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from dotenv import load_dotenv
import asyncio

# for debugging purpose


load_dotenv()

# for tracing purpose
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

@function_tool
def weather (city:str)->str:
    return f"The weather in {city} is sunny"


# only required if you want to use gemini and to set the api key globally
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=gemini_client
)

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    tools=[weather],
    model=model
    
)

# asynchronously
async def stream_agent():
    # run streamed is an async function
    result = Runner.run_streamed(agent,"What is the weather in karachi?")

    async for event in result.stream_events():

        # to see each event in the stream
        # print(f"\n[EVENT] : {event}\n")
        print(f"\n[EVENT TYPE] : {event.type}\n")

        # to see only the data events in the stream
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(f"\n[DATA] : {event.data}\n")
    print(result.final_output)

asyncio.run(stream_agent())
# for event in result.events:
#     print(event)