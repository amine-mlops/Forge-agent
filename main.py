import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
 

from tools import (
    search,

    create_file,
    read_file,
    list_file,
    edit_file,

    browser_open,
    browser_read,
    browser_click,
    browser_type,
    browser_screenshot,
    browser_manager,

    terminal_run,
)


agent = create_agent(
    model="openrouter:openrouter/free",

    tools=[
        search,

        create_file,
        read_file,
        list_file,
        edit_file,

        browser_open,
        browser_read,
        browser_click,
        browser_type,
        browser_screenshot,

        terminal_run,
    ],

    system_prompt="""
You are Forge, an AI research and coding assistant.

You have access to tools that you can actually execute.

IMPORTANT:

- Use terminal_run for shell commands and code execution.
- Terminal commands execute inside the Forge sandbox.
- Use filesystem tools to create, read, list, and edit files.
- Use browser tools for browser interaction.
- Use web search for internet research.
- When solving coding tasks, inspect existing files before modifying them.
- After modifying code, execute it and inspect the result.
- If execution fails, diagnose the error, modify the code, and try again.
- Do not claim success unless the corresponding tool confirms it.

When a browser task requires multiple actions, keep using
the browser tools instead of switching to web search.

After using the tools, provide a short summary of what you did.
"""
)

import asyncio

async def main():

    try:

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": """
Create a Python program called prime_numbers.py that finds all prime numbers between 1 and 100. Run it, verify that the result is correct, and if there is any error, debug it automatically.
"""
                    }
                ]
            }
        )

        print("\n" + "=" * 60)
        print("FINAL ANSWER")
        print("=" * 60)

        print(
            result["messages"][-1].content
        )

    finally:

        await browser_manager.close()


if __name__ == "__main__":
    asyncio.run(main())