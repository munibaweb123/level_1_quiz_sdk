import os
import asyncio
import requests
from dotenv import load_dotenv, find_dotenv
# Load environment variables
_: bool = load_dotenv(find_dotenv())
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, RunContextWrapper



# ONLY FOR TRACING
os.getenv('OPENAI_AGENTS_DISABLE_TRACING')
print("Tracing disabled:", os.getenv("OPENAI_AGENTS_DISABLE_TRACING"))
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

# filepath: [adv_tool4.py](http://_vscodecontentref_/0)
# ...existing code...
def error(ctx: RunContextWrapper, error: Exception):
    print("[failure_error_function] called with:", repr(error))
    return f"this is the {error}"

# -------- Weather Tool --------
def get_weather_alternative(city: str) -> str:
    """Fallback weather service (dummy or backup API)."""
    return f"Alternative weather service: Weather in {city} is sunny (fallback)."



@function_tool(description_override="Fetch weather for a given city",failure_error_function=error)
def get_weather(city: str) -> str:
    """Primary weather service using wttr.in (or any free API)."""
    try:
        url = "weatherapi.com"
        #url = f"https://wttr.in/{city}?format=3"  # simple free API
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise ValueError("Primary weather service failed.")
    except (ValueError, TimeoutError):
        # Call alternative service
        return get_weather_alternative(city)
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

# -------- Base Agent --------
base_agent: Agent = Agent(
    name="WeatherAgent",
    instructions="Use the weather tool to fetch the current weather.",
    model=llm_model,
    tools=[get_weather],
)

base_agent

# -------- Runner --------
async def main():
    res = await Runner.run(base_agent, "What is weather in Islamabad?")
    print("Agent Response:", res.final_output)

if __name__ == "__main__":
    asyncio.run(main())
