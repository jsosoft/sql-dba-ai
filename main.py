import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

async def main():
    # 1. Setup the Gemini Client
    model_client = OpenAIChatCompletionClient(
        model="gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
        # Base URL for Google AI Studio's OpenAI-compatible endpoint
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/" 
    )

    # 2. Define the DBA Agent
    dba_agent = AssistantAgent(
        name="SQL_DBA",
        model_client=model_client,
        system_message="You are a SQL Server expert. Help the user optimize their local instance.",
    )

    # 3. Run a test conversation
    await Console(dba_agent.run_stream(task="Check my SQL Server connection health."))

if __name__ == "__main__":
    asyncio.run(main())