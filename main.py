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
Open YouTube in the browser.

Search for "Agentic AI".

Read the search results.

Take a full-page screenshot of the search results
and save it as:

youtube_Agentic_AI.png

Then tell me the titles of the first 5 videos you can see.

Use the browser tools to perform the task.
Do not use Tavily instead of the browser.
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