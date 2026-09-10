import re

def parse_plan(plan: str) -> list[str]:
    """
    Extract numbered steps from the planner output.

    Example:

        PLAN
        1. Create the project structure.
        2. Implement the application.
        3. Write tests.

    Returns:

        [
            "Create the project structure.",
            "Implement the application.",
            "Write tests."
        ]
    """

    if not isinstance(plan, str):
        return []

    steps = []

    for line in plan.splitlines():

        line = line.strip()

        match = re.match(r"^\d+\.\s+(.*)", line)

        if match:
            steps.append(match.group(1).strip())

    return steps


async def execute_plan(agent, plan: str, original_request: str):
    """
    Execute a Forge plan step by step.
    """

    steps = parse_plan(plan)

    # Protect against invalid planner output
    
    if not steps:
        return [
            {
                "step": 0,
                "description": "Plan parsing",
                "result": (
                    "FAILED: The planner did not return a valid "
                    "numbered execution plan."
                ),
            }
        ]

    results = []

    # Execute each step
    
    for index, step in enumerate(steps, start=1):

        print(f"\n{'=' * 60}")
        print(f"Executing step {index}/{len(steps)}")
        print(f"{'=' * 60}")
        print(step)
        print()

        execution_prompt = f"""
You are executing Step {index} of a larger Forge task.

Original user request:
{original_request}

Current plan step:
{step}

Instructions:

- Focus primarily on this step.
- Use the available tools when necessary.
- Actually perform the required work.
- Inspect existing files before modifying them when appropriate.
- Do not pretend that work was completed.
- Verify your work when possible.
- If this step depends on previous work, inspect the current workspace.
- If you encounter an error, diagnose and fix it before finishing.

When you finish this step, briefly report what you actually completed
and what you verified.
"""

        try:

            result = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": execution_prompt,
                        }
                    ]
                }
            )

            response = result["messages"][-1].content

            results.append(
                {
                    "step": index,
                    "description": step,
                    "result": response,
                }
            )

            print(f"\n✓ Step {index} completed\n")

        except Exception as e:

            print(f"\n✗ Step {index} failed")
            print(f"Error: {e}\n")

            results.append(
                {
                    "step": index,
                    "description": step,
                    "result": f"FAILED: {e}",
                }
            )

            # Stop execution for now.
            # Recovery/retry will be added later.
            break

    return results


