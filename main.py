from agents import Agent, ModelSettings, AsyncOpenAI, Runner, function_tool,OpenAIChatCompletionsModel, RunConfig
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not gemini_api_key and openai_api_key:
    raise ValueError('your api keys are not set')

external_client=AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

llm_model:OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.5-flash-lite"

)
config=RunConfig(
    tracing_disabled=False,
    model=llm_model,
    model_provider=external_client
)

@function_tool
def weather(city:str)->str:
    return f"weather for {city} is cloudy"

weather_model=ModelSettings(
    tool_choice='none',
    temperature=0.9,
    max_tokens=200
    )

agent:Agent = Agent(
    name="Haiku Agent",
    instructions="you are a helpful assistant",
    tools=[weather],
    model_settings=weather_model,
    model="gpt-4o-mini"
)

math_tutor = Agent(
    name="Math Tutor",
    instructions="You are a precise math tutor. Always show your work step by step.",
    model_settings=ModelSettings(
        temperature=0.1,  # Very focused
        max_tokens=500    # Enough for detailed steps
    )
)

creative_writer = Agent(
    name="Creative Writer",
    instructions="You are a creative storyteller. Write engaging, imaginative stories.",
    model_settings=ModelSettings(
        temperature=0.8,  # Very creative
        max_tokens=300    # Short but creative
    ),
    model="gpt-4o-mini"
)

@function_tool
def calculate_area(length: float, width: float) -> str:
    """Calculate the area of a rectangle."""
    area = length * width
    return f"Area = {length} × {width} = {area} square units"

# Agent that MUST use tools
tool_user = Agent(
    name="Tool User",
    instructions="You are a helpful assistant. Always use tools when available.",
    tools=[calculate_area],
    model_settings=ModelSettings(tool_choice="auto"),
    
)
agent_none = Agent(
        name="None",
        tools=[calculate_area],
        model_settings=ModelSettings(tool_choice="none"),
        
    )
agent_brief = Agent(
    name="Brief Assistant",
    model_settings=ModelSettings(max_tokens=400)
)

agent_detailed = Agent(
    name="Detailed Assistant", 
    instructions="You are a detailed and thorough assistant. Provide comprehensive and well-explained answers. if tokens are exceeded give brief relp and use less tokens",
    model_settings=ModelSettings(max_tokens=1000)
)

async def new():
    result = await Runner.run(agent_detailed,"What is economic condition of Pakistan in 2025", run_config=config)
    print(result.final_output)

asyncio.run(new())
