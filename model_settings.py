from agents import Agent, ModelSettings, OpenAIChatCompletionsModel, RunConfig, RunContextWrapper, Runner, function_tool
import os
from agents.agent import StopAtTools
from dotenv import load_dotenv
from openai import AsyncOpenAI
load_dotenv()

openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    raise ValueError('openai api key not set')

gemini_api = os.getenv('GEMINI_API_KEY')
if not gemini_api:
    raise ValueError("api key not set")

external_client = AsyncOpenAI(
    api_key=gemini_api,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model= OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.0-flash"
)

config=RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=False
)
openai_client=AsyncOpenAI(api_key=openai_key)


# 1. Temperature => The Creativity Knob
focus_model_setting = ModelSettings(
    temperature=0.1
)

focused_agent = Agent(
    name="Focused Math Tutor",
    # instructions="you are a focus agent, you give answers to query in focused and consistent way",
    #model="gpt-4o-mini",
    model="gpt-4o-mini",
    model_settings=ModelSettings(
        top_p=0.3,              # Use only top 30% of vocabulary
        frequency_penalty=0.5,   # Avoid repeating words
        presence_penalty=0.3,     # Encourage new topics
        temperature=1.9          # High creativity
    )
    # model_settings=focus_model_setting
)
creative_model_settings = ModelSettings(
    temperature= 0.9
)
top_p_model_settings=ModelSettings(
    top_p=0.9,
    frequency_penalty=0.9,
    presence_penalty=0.9
)
agent_creative = Agent(
    name="Creative Story Writer",
    instructions="You are creative storyteller",
    model_settings= top_p_model_settings,
    model="gpt-4o-mini"
)

# 2. Tool Choice - The "can I use tools" switch
@function_tool
def calculator(a:int,b:int,op:str)-> int|str|float:
    if op=='add' or op == 'plus' or op == 'sum' or op == '+':
        return a+b
    elif op == 'subtract' or op == 'minus' or op == 'difference' or op == '-':
        return a-b
    elif op == 'multiply' or op == 'times' or op == 'product' or op == '*':
        return a*b
    elif op == 'divide' or op == 'division' or op == 'quotient' or op == '/':
        try:
            return a/b
        except ZeroDivisionError as e:
            return 'can not divide with zero',e
    else:
        return {"error": f"Unsupported operation: {op}"}

@function_tool
def weather(city:str):
    return f'weather of {city} is cloudy'


@function_tool
async def translator(
    ctx: RunContextWrapper,
    from_language: str,
    to_language: str,
    text: str
) -> dict:
    """
    Translate text from one language to another using OpenAI.
    """
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are a translator. Translate from {from_language} to {to_language}."},
            {"role": "user", "content": text}
        ]
    )
    
    translation = response.choices[0].message.content
    return {"translation": translation}




agent_auto = Agent(
    name="Smart assistant",
    tools=[calculator, weather],
    model_settings=ModelSettings(tool_choice='auto'),
    #model="gpt-4o-mini"
    model=model
)

agent_required = Agent(
    name="Tool user",
    tools=[calculator, weather],
    model_settings=ModelSettings(tool_choice='required'),
    #tool_use_behavior="stop_on_first_tool",
    #tool_use_behavior=StopAtTools(stop_at_tool_names=["weather"]),
    tool_use_behavior="run_llm_again", # by default set for tool use behavior
    #model='gpt-4o-mini'
    model=model
)

agent_no_tools = Agent(
    name="chat only",
    tools=[calculator, weather],
    model_settings=ModelSettings(tool_choice='none', max_tokens=100),
    #model='gpt-4o-mini'
    model=model
)

# 3. Max Tokens - The Response Length Limit
agent_brief = Agent(
    name="brief assistant",
    model_settings=ModelSettings(max_tokens=100),
    model=model
)
agent_detailed = Agent(
    name="Detailed assistant",
    model_settings=ModelSettings(max_tokens=500),
    model=model
)

# Advance settings => parallel tool call
parallel_agent = Agent(
    name="Multi-Tasker",
    tools=[weather, calculator, translator],
    model_settings=ModelSettings(
        tool_choice="auto",
        parallel_tool_calls=False  # Use multiple tools simultaneously
    ),
    model="gpt-4o-mini"
)

# Agent uses tool one at a time
sequential_agent = Agent(
    name="One at a time",
    tools=[weather, calculator, translator],
    model_settings=ModelSettings(
        tool_choice='required',
        parallel_tool_calls=False
    ),
    model=model
)

# result=Runner.run_sync(focused_agent,"what is openai agents sdk?")
result = Runner.run_sync(agent_required, "what today weather in new york ")
print(result.final_output)

