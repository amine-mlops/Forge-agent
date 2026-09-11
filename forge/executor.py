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


async def diagnose_and_repair(
    agent,
    original_request: str,
    step: str,
    error: str,
) -> dict:
    """
    Ask the Forge agent to diagnose and repair a failed execution step.
    """

    recovery_prompt = f"""
You are Forge's failure recovery component.

A previous execution step failed.

============================================================
ORIGINAL USER REQUEST
============================================================

{original_request}

============================================================
FAILED STEP
============================================================

{step}

============================================================
ERROR
============================================================

{error}

============================================================
RECOVERY OBJECTIVE
============================================================

Diagnose the actual cause of the failure and repair it.

You MUST:

1. Inspect the relevant files in agent_workspace.
2. Determine the actual root cause of the failure.
3. Modify the necessary files to fix the problem.
4. Verify the fix by running appropriate tests or commands.
5. Do not modify files outside agent_workspace.
6. Do not merely explain what should be changed.
7. Actually perform the repair.
8. Do not claim success unless you verified the fix.

If the failure is caused by an incorrect implementation, fix the
implementation rather than simply hiding or suppressing the error.

When finished, report:

- Root cause
- Files modified
- Changes made
- Verification performed
- Whether the repair succeeded
"""

    try:
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": recovery_prompt,
                    }
                ]
            }
        )

        response = result["messages"][-1].content

        return {
            "status": "success",
            "output": response,
            "error": None,
        }

    except Exception as e:

        return {
            "status": "failed",
            "output": "",
            "error": str(e),
        }


async def execute_step(
    agent,
    original_request: str,
    step_number: int,
    step: str,
) -> dict:
    """
    Execute a single Forge plan step once.
    """

    execution_prompt = f"""
You are executing Step {step_number} of a larger Forge task.

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
- If you encounter an error, do not hide it.
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

        return StepResult(
            step=step_number,
            description=step,
            status="success",
            output=response,
        ).to_dict()

    except Exception as e:

        return StepResult(
            step=step_number,
            description=step,
            status="failed",
            error=str(e),
        ).to_dict()


MAX_RETRIES = 3


async def execute_step_with_recovery(
    agent,
    original_request: str,
    step_number: int,
    step: str,
) -> dict:
    """
    Execute a step with automatic diagnosis, repair, and retry.

    The initial execution is followed by up to MAX_RETRIES
    recovery attempts.
    """

    for attempt in range(1, MAX_RETRIES + 2):

        print(
            f"  Attempt {attempt}/{MAX_RETRIES + 1}"
        )

        result = await execute_step(
            agent=agent,
            original_request=original_request,
            step_number=step_number,
            step=step,
        )

        if result["status"] == "success":

            print(
                f"  ✓ Attempt {attempt} succeeded"
            )

            return result

        error = result["error"]

        print(
            f"  ✗ Attempt {attempt} failed"
        )
        print(
            f"    Error: {error}"
        )

        # No recovery after the final attempt.
        if attempt > MAX_RETRIES:
            break

        print(
            "  → Diagnosing and repairing..."
        )

        recovery = await diagnose_and_repair(
            agent=agent,
            original_request=original_request,
            step=step,
            error=error,
        )

        if recovery["status"] == "success":

            print(
                "  ✓ Repair completed"
            )
            print(
                "  → Retrying step..."
            )

        else:

            print(
                "  ✗ Repair failed"
            )
            print(
                f"    Error: {recovery['error']}"
            )

    return StepResult(
        step=step_number,
        description=step,
        status="failed",
        error=(
            f"Step failed after "
            f"{MAX_RETRIES + 1} execution attempts."
        ),
    ).to_dict()


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

        # Execute the step with automatic recovery.
        step_result = await execute_step_with_recovery(
            agent=agent,
            original_request=original_request,
            step_number=index,
            step=step,
        )

        results.append(step_result)

        if step_result["status"] == "success":

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

        else:

            # Recovery failed after all retry attempts.
            save_state(
                original_request=original_request,
                plan=plan,
                completed_steps=completed_steps,
                current_step=index,
                status="paused",
            )

            print(f"✗ Step {index} failed after recovery attempts")
            print(f"  Error: {step_result['error']}\n")

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
