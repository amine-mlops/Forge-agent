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
)


agent = create_agent(
    model="openrouter:nvidia/nemotron-3.5-lightning:free",

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

After using the tools, provide a short summary of what you did.
"""
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
Open YouTube in the browser and search for "neural networks".

Then perform all of the following tasks:

1. Read the YouTube search results.
2. Identify the first 5 videos you can see.
3. Give me the title and URL of each of the 5 videos.
4. Take a screenshot of the YouTube search-results page after
   searching for "neural networks".
5. Save the screenshot inside agent_workspace as:
   youtube_neural_networks.png
6. Create a Markdown file inside agent_workspace called:
   youtube_neural_networks.md
7. Put the following information in the Markdown file:
   - Search query
   - YouTube search URL
   - The first 5 video titles
   - The URLs of the 5 videos

IMPORTANT:
- Use the browser tools to actually open YouTube and perform the search.
- Use the browser_read tool to inspect the results.
- Use the browser_screenshot tool to create the screenshot.
- Use the create_file tool to create the Markdown file.
- Do not give me Python code instead of performing the actions.
- Do not pretend that an action was performed if it wasn't.
- Complete the actions using the available tools.
"""
            }
        ]
    }
)
print("\n" + "=" * 60)
print("FORGE EXECUTION")
print("=" * 60)

for message in result["messages"]:

    print("\nMESSAGE TYPE:")
    print(message.type)

    print("\nCONTENT:")
    print(message.content)

    if hasattr(message, "tool_calls") and message.tool_calls:

        print("\nTOOL CALLS:")
        print(message.tool_calls)

    print("-" * 60)


print("\nFINAL ANSWER:")
print(result["messages"][-1].content)
