import asyncio
import os
from openai import AsyncOpenAI
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OpenAIChatCompletionsModel,
    RunConfig,
    RunContextWrapper,
    TResponseInputItem,
    Runner,
    input_guardrail
)
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

class MathHomeworkOutput(BaseModel):
    is_math_homework:bool
    reasoning: str

guardrail_agent = Agent(
    name="guardrail check",
    instructions="check if the user is ask you to do his math homework",
    output_type=MathHomeworkOutput
)

@input_guardrail
async def math_guardrail(
    ctx:RunContextWrapper[None], agent: Agent, input:str|list[TResponseInputItem]
)->GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_math_homework

    )

agent = Agent(
    name="Customer Support Agent",
    instructions="you are a customer support agent you help customers with their customer support questions",
    input_guardrails=[math_guardrail]
)

async def main():
    try:
        res = await Runner.run(agent, "what is the square root of 9",run_config=config)
        print(res.final_output)
        print("Guardrail didn't trip this is unexpected")
    except InputGuardrailTripwireTriggered:
        print("math homework guardrail tripped because query is not related to math")

asyncio.run(main())