import re
from dataclasses import asdict, dataclass

from forge.state import save_state


@dataclass
class StepResult:
    step: int
    description: str
    status: str
    output: str = ""
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def parse_plan(plan: str) -> list[str]:
    if not isinstance(plan, str):
        return []

    steps = []

    for line in plan.splitlines():
        line = line.strip()

        match = re.match(r"^\d+\.\s+(.*)", line)

        if match:
            steps.append(match.group(1).strip())

    return steps


async def execute_plan(
    agent,
    plan: str,
    original_request: str,
    completed_steps: list[int] | None = None,
):
    steps = parse_plan(plan)

    if not steps:
        save_state(
            original_request=original_request,
            plan=plan,
            completed_steps=[],
            current_step=None,
            status="failed",
        )

        return [
            StepResult(
                step=0,
                description="Plan parsing",
                status="failed",
                error="The planner did not return a valid numbered execution plan.",
            ).to_dict()
        ]

    if completed_steps is None:
        completed_steps = []

    results = []

    for index, step in enumerate(steps, start=1):

        # Skip steps that were already completed.
        if index in completed_steps:
            print(f"✓ Step {index} already completed, skipping")
            continue

        print(f"┌─ Step {index}/{len(steps)} ─────────────────────────")
        print(f"│ {step}")
        print("└────────────────────────────────────────────")
        print()

        # Save state before starting the step.
        save_state(
            original_request=original_request,
            plan=plan,
            completed_steps=completed_steps,
            current_step=index,
            status="running",
        )

        execution_prompt = f"""
You are executing Step {index} of a larger Forge task.

Original user request:

{original_request}

Current plan step:

{step}

Instructions:

- Focus primarily on this step.
- Use available tools when necessary.
- Actually perform the required work.
- Inspect existing files before modifying them when appropriate.
- Do not pretend work was completed.
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

            step_result = StepResult(
                step=index,
                description=step,
                status="success",
                output=response,
            )

            results.append(step_result.to_dict())

            completed_steps.append(index)

            # Save progress after successful completion.
            save_state(
                original_request=original_request,
                plan=plan,
                completed_steps=completed_steps,
                current_step=index,
                status="running",
            )

            print(f"✓ Step {index} completed\n")

        except Exception as e:

            # Save the exact point where execution stopped.
            save_state(
                original_request=original_request,
                plan=plan,
                completed_steps=completed_steps,
                current_step=index,
                status="paused",
            )

            step_result = StepResult(
                step=index,
                description=step,
                status="failed",
                error=str(e),
            )

            results.append(step_result.to_dict())

            print(f"✗ Step {index} failed")
            print(f"  Error: {e}\n")

            break

    # If every step completed, mark the task as completed.
    if len(completed_steps) == len(steps):
        save_state(
            original_request=original_request,
            plan=plan,
            completed_steps=completed_steps,
            current_step=None,
            status="completed",
        )

    return results
