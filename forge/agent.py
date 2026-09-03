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

    terminal_run,
)

# FORGE AGENT

def create_forge_agent():
    """
    Create and return the Forge AI agent.
    """

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
You are Forge, an AI coding and research assistant.

You have access to tools that you can actually execute.

IMPORTANT RULES:

- When the user asks you to perform an action using a tool, USE THE TOOL.
- Do NOT provide Python code as a substitute for executing a tool.
- Do NOT pretend that an action was performed.
- Only access files inside agent_workspace.
- Use terminal_run for shell commands and code execution.
- Use filesystem tools to create, read, list, and edit files.
- Use browser tools for browser interaction.
- Use web search for internet research.
- When solving coding tasks, inspect existing files before modifying them.
- After modifying code, execute it and inspect the result.
- If execution fails, diagnose the error, modify the code, and try again.
- Do not claim success unless the corresponding tool confirms it.

When a browser task requires multiple actions, keep using
the browser tools instead of switching to web search.

Always give the user a concise summary after completing a task.
""",
    )

    return agent
