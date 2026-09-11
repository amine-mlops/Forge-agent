import asyncio
from pathlib import Path

from forge.agent import create_forge_agent


WORKSPACE = Path("agent_workspace/recovery_test")


async def main():
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    buggy_file = WORKSPACE / "buggy.py"

    buggy_file.write_text(
        """def divide(a, b):
    return a / b


if __name__ == "__main__":
    print(divide(10, 0))
""",
        encoding="utf-8",
    )

    print("Created intentionally broken file:")
    print(buggy_file)
    print()

    agent = create_forge_agent()

    prompt = f"""
A Forge execution step failed.

Original task:
Create and verify a simple division program.

Failed step:
Run the division program and verify that it works correctly.

Error:
ZeroDivisionError: division by zero

The relevant file is:
{buggy_file}

Your job is to diagnose and repair the failure.

Instructions:
- Inspect the file before modifying it.
- Identify the actual cause of the failure.
- Fix the implementation.
- Run the program after the fix.
- Verify that it no longer crashes.
- Actually modify the file; do not only explain the solution.
- Do not modify files outside agent_workspace/recovery_test.
- Report what you changed and how you verified it.
"""

    print("Forge is diagnosing and repairing the failure...\n")

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }
    )

    response = result["messages"][-1].content

    print("Forge response:")
    print("────────────────────────────")
    print(response)
    print()

    print("Repaired file:")
    print("────────────────────────────")
    print(buggy_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
