import os

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from forge.prompts import FORGE_SYSTEM_PROMPT

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

system_prompt=FORGE_SYSTEM_PROMPT,
    )

    return agent
