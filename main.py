import os
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
 

from tools.filesystem import(
    create_file,
    read_file,
    list_file,
    edit_file,
)

from tools.web import search

from tools.browser import(
    browser_open,
    browser_read,
    browser_click,
    browser_type,
    browser_screenshot,
    browser_manager,
)

from tools.terminal import terminal_run


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

- When the user asks you to perform an action using a tool,
  USE THE TOOL.
- Do NOT provide Python code as a substitute for executing a tool.
- Do NOT pretend that an action was performed.
- Only access files inside agent_workspace.
- Use browser tools for browser tasks.
- Use filesystem tools for file tasks.
- Use web search when internet research is required.
- Use terminal_run for shell commands and code execution.
- Terminal execution is sandboxed inside agent_workspace.
- Never claim a command was executed unless the terminal tool returned a result.

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
Create a Python file called fibonacci.py inside the workspace.

The program should calculate the first 20 Fibonacci numbers and print them.

Then execute the Python program using the terminal tool.

Read the output and tell me the result.

You MUST use the filesystem and terminal tools to actually create and execute the file.
Do not just give me the Python code.
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