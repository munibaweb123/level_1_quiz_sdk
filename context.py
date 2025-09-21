from dataclasses import dataclass
from agents import Agent, RunContextWrapper, Runner, OpenAIChatCompletionsModel, RunConfig, function_tool
from openai import AsyncOpenAI, BaseModel
from dotenv import load_dotenv
load_dotenv()

import os
import asyncio

openai_key = os.getenv('OPENAI_API_KEY')
gemini_api = os.getenv('GEMINI_API_KEY')
if not openai_key or not gemini_api:
    raise ValueError('API keys not set properly')

external_client = AsyncOpenAI(
    api_key=gemini_api,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(
    openai_client=external_client,
    model="gemini-2.0-flash"
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=False
)

class UserContext(BaseModel):
    user_id:int
    user_name: str
    user_role: str
    user_experience: str

@function_tool
async def greet_user(ctx:RunContextWrapper[UserContext], greeting:str)->str:
    return f"{greeting}, user {ctx.context.user_name} with role {ctx.context.user_role} and experience {ctx.context.user_experience}"



@function_tool
async def get_user_age(ctx:RunContextWrapper)->str:
    print(f"The user {ctx.context['age']} years old")


async def dynamic_instructions(ctx:RunContextWrapper, agent)->str:
    return f"You are a helpful assistant that greets user based on context. The user name is {ctx.context['name']} with {ctx.context['age']} years old"    


context_agent = Agent(
    name="Context Agent",
    instructions=dynamic_instructions,
    # tools=[greet_user],
    tools=[get_user_age],
    
)



async def main():
    user_context = UserContext(
        user_id="one-two-three", # throw type error by pydantic, input should be a valid integer
        user_name="Nitoo",
        user_role="Agentic ai developer",
        user_experience="2 years"
    )
    result = await Runner.run(
        starting_agent=context_agent,
        input="Hi there!",
        #context={"age": 25, "name": "Nitoo"},
        context=user_context,
        run_config=config
    )
    print(f"Output is {result.final_output}")

asyncio.run(main())