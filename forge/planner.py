
import os

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent


PLANNER_PROMPT = """
You are Forge's planning component.

Your job is to analyze the user's request and determine whether
the task is simple or complex.

For simple tasks:
- Return exactly: SIMPLE

For complex tasks:
- Return a numbered execution plan.
- Keep the plan concise.
- Include only meaningful implementation steps.
- Do not execute tools.
- Do not write code.
- Do not claim that anything has been created or modified.

A task is complex if it:
- requires multiple files,
- requires several implementation steps,
- requires debugging,
- requires tests,
- requires architectural changes,
- or requires multiple tools.

For complex tasks, use this format:

PLAN
1. ...
2. ...
3. ...
4. ...

Do not include anything before PLAN or SIMPLE.

NUMBERING RULES:

- Number every step sequentially.
- Start at 1.
- Never skip a number.
- Never duplicate a number.
- The final plan must have consecutive numbering: 1, 2, 3, ... N.

- Before returning the plan, verify that the numbering is sequential.
"""


def create_planner():
    """
    Create the Forge planning agent.
    """

    return create_agent(
        model="openrouter:openrouter/free",
        tools=[],
        system_prompt=PLANNER_PROMPT,
    )


async def generate_plan(planner, user_input):
    """
    Analyze a user request and return either SIMPLE
    or a numbered execution plan.
    """

    result = await planner.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        }
    )

    return result["messages"][-1].content.strip()
