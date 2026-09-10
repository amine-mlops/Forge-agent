import re

from dotenv import load_dotenv
from langchain.agents import create_agent

load_dotenv()


PLANNER_PROMPT = """
You are Forge's planning component.

Your ONLY responsibility is to analyze the user's request and create
a concise execution plan.

You are NOT the executor.

You MUST NEVER:
- execute tools
- call tools
- write files
- modify files
- run commands
- browse the web
- generate source code
- generate file contents
- simulate tool calls
- output tool-call syntax
- output XML
- output JSON
- say that you are starting implementation

You only produce a plan.

============================================================
SIMPLE TASKS
============================================================

If the task is simple and can be completed directly with one action,
return EXACTLY:

SIMPLE

Nothing else.

============================================================
COMPLEX TASKS
============================================================

For complex tasks, return ONLY a numbered plan.

The output MUST have exactly this structure:

PLAN
1. ...
2. ...
3. ...

Rules:

- Start with exactly: PLAN
- Every step must be numbered.
- Number sequentially: 1, 2, 3, 4, ... N
- Never skip a number.
- Never duplicate a number.
- Never include text before PLAN.
- Never include text after the final step.
- Keep each step concise.
- Describe WHAT should be done, not HOW to write the code.
- Do not include source code.
- Do not include file contents.
- Do not include tool calls.
- Do not include phrases such as "Let me start implementing".
- Do not actually perform any of the steps.

Before returning the answer, verify:

1. The output starts with PLAN.
2. The steps are sequentially numbered.
3. There is no tool-call syntax.
4. There is no source code.
5. There is no implementation after the plan.

The final response MUST contain ONLY the plan.
"""


def create_planner():
    return create_agent(
        model="openrouter:openrouter/free",
        tools=[],
        system_prompt=PLANNER_PROMPT,
    )


def clean_plan(plan: str) -> str:
    """
    Clean accidental model output that appears after the plan.

    The planner should never generate tool calls or implementation
    content. This function provides a safety layer before the output
    reaches the executor.
    """

    if not isinstance(plan, str):
        return "SIMPLE"

    plan = plan.strip()


    # SIMPLE

    if plan.startswith("SIMPLE"):
        return "SIMPLE"

    # Find PLAN

    plan_match = re.search(r"\bPLAN\b", plan)

    if not plan_match:
        return "SIMPLE"

    plan = plan[plan_match.start():]

    # Remove accidental implementation/tool output

    stop_patterns = [
        r"<\|tool_call_start\|>",
        r"<\|tool_call_end\|>",
        r"Let me start implementing",
        r"Let me implement",
        r"I will now implement",
        r"Implementation:",
    ]

    stop_position = len(plan)

    for pattern in stop_patterns:

        match = re.search(
            pattern,
            plan,
            flags=re.IGNORECASE,
        )

        if match:
            stop_position = min(
                stop_position,
                match.start(),
            )

    plan = plan[:stop_position].strip()

    # Keep only numbered steps
  
    lines = plan.splitlines()

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if line == "PLAN":
            cleaned_lines.append(line)
            continue

        if re.match(r"^\d+\.\s+", line):
            cleaned_lines.append(line)

    if len(cleaned_lines) <= 1:
        return "SIMPLE"

    return "\n".join(cleaned_lines)


async def generate_plan(planner, user_input):
    """
    Generate and sanitize a plan for the user's request.
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

    raw_plan = result["messages"][-1].content

    return clean_plan(raw_plan)


