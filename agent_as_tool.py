from agents import Agent, ModelSettings, AsyncOpenAI, RunContextWrapper, Runner, function_tool,OpenAIChatCompletionsModel, RunConfig
import os
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
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

class LanguageContext(BaseModel):
    language_preference: str = "french_spanish"

def french_enabled(ctx: RunContextWrapper[LanguageContext], agent) -> bool:
    """Enable French for French+Spanish preference."""
    return ctx.context.language_preference == "french_spanish"

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
            is_enabled=True,
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
            is_enabled=french_enabled
        ),
    ],
)

async def main():
    context = RunContextWrapper(LanguageContext(language_preference="french_spanish"))
    result = await Runner.run(orchestrator_agent, input="Say 'best of luck for quiz level 1' in Spanish and French.",run_config=config,
                              max_turns=5, context=context.context)
    print(result.final_output)

asyncio.run(main())