from dotenv import load_dotenv
load_dotenv()
from openai.types.shared import Reasoning
from agents import Agent, AsyncOpenAI, ModelSettings, Runner,OpenAIChatCompletionsModel, RunConfig,trace #set_tracing_disabled

import os
import asyncio
#set_tracing_disabled(disabled=True)

os.getenv('OPENAI_AGENTS_DISABLE_TRACING')
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
    model="gemini-2.5-flash"

)
config=RunConfig(
    tracing_disabled=True,
    model=llm_model,
    model_provider=external_client
)



async def main():
    agent: Agent=Agent(
    name="joke assistant", #required
    instructions="you are a joker, tell funny jokes", # system prompt
    model_settings=ModelSettings(temperature=0.1, top_p=1)
    
    # model_settings=ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="low")
    

)
    
    # global/run-config level settings (lower precedence than runtime overrides)
    base_run_config = RunConfig(model=llm_model, model_settings=ModelSettings(temperature=0.3))

    # runtime override (highest precedence)
    runtime_override = ModelSettings(temperature=0.8, top_p=0.9)

    # resolve: order is from lowest -> highest precedence
   # resolve precedence step by step (agent < base_run_config < runtime_override)
    resolved = ModelSettings.resolve(agent.model_settings, base_run_config.model_settings)
    resolved = ModelSettings.resolve(resolved, runtime_override)

    print("Resolved model settings:", resolved)

    print("Resolved model settings:", resolved)

    # use resolved settings in a run-config passed to Runner
    effective_config = RunConfig(model=llm_model, model_settings=resolved)
    #agent.model='gpt-4o-mini'
    with trace("Latest Joke Workflow"):
        result = await Runner.run(agent,"tell me 1 funny joke",run_config=effective_config)
        second_result = await Runner.run(agent,f"rate this joke:{result.final_output}",run_config=config)
        print(f"joke: {result.final_output}")
        print(f"rating: {second_result.final_output}")

asyncio.run(main())