import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# local utilities for SQL Server interaction
from db_utils import get_sql_health

load_dotenv()

async def main():
    model_client = OpenAIChatCompletionClient(
        model=os.getenv("OPEN_AI_MODEL"),
        api_key=os.getenv("GEMINI_API_KEY"),
        # Base URL for Google AI Studio's OpenAI-compatible endpoint
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": "GEMINI",
            "structured_output": False,
        },
    )

    # 2. Define the DBA Agent
    dba_agent = AssistantAgent(
        name="SQL_DBA",
        model_client=model_client,
        # instruct the agent to restrict its thinking and suggestions to
        # *instance-level* configuration/tuning.  avoid any advice about
        # individual database designs, specific queries, or application code.
        system_message=(
            "You are a SQL Server expert. Your analysis should be strictly limited "
            "to instance-level configuration and optimization (memory settings, "
            "max degree of parallelism, etc.) based on the sys.configurations output."
            "Do not suggest any per-database or query-specific changes."
        ),
    )

    # quick health check before talking to the agent
    health = get_sql_health()
    # health is now a list of tuples; show a few rows or entire list
    if isinstance(health, list):
        print("SQL health rows:")
        for row in health[:10]:  # limit to first 10 for brevity
            print(row)
        if len(health) > 10:
            print(f"... ({len(health)} rows total)")
    else:
        print(f"SQL health: {health}")

    if os.getenv("DRY_RUN") == "true":
        print("DRY RUN mode enabled; skipping API call")
    else:
        # include the health check in the prompt so the agent is aware of it
        task_text = f"SQL health: {health}\n\nProvide instance-level optimization advice."

        # use `run` to get the final response message so we can inspect it
        result = await dba_agent.run(task=task_text)
        final_msg = result.messages[-1].content
        print("Agent response:\n", final_msg)

        # naive execution: if the response looks like SQL (starts with common
        # keywords), apply it. You can replace this heuristic with manual
        # confirmation or regex parsing as needed.
        sql_candidate = final_msg.strip()
        if sql_candidate.upper().startswith(("ALTER", "CREATE", "UPDATE", "SET", "EXEC")):
            print("Detected SQL-like response, executing on instance...")
            try:
                from db_utils import execute_sql
                execute_sql(sql_candidate)
                print("Execution complete")
            except Exception as e:
                print("Execution failed:", e)
        else:
            print("No executable SQL detected or response not in expected format.")

os.environ.setdefault("OPEN_AI_MODEL", "gemini-2.5-flash")
print(os.getenv("OPEN_AI_MODEL"))
os.environ.setdefault("DRY_RUN", "false")  # set to 'false' or remove to hit the API

if __name__ == "__main__":
    asyncio.run(main())
