import asyncio
from pathlib import Path

from forge.agent import create_forge_agent
from forge.executor import diagnose_and_repair


WORKSPACE = Path("agent_workspace/recovery_test")


async def main():
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    buggy_file = WORKSPACE / "buggy.py"

    buggy_file.write_text(
        """def calculate_average(total, count):
    return total / count


if __name__ == "__main__":
    print(calculate_average(100, 0))
""",
        encoding="utf-8",
    )

    print("Created broken program:")
    print(buggy_file)
    print()

    agent = create_forge_agent()

    result = await diagnose_and_repair(
        agent=agent,
        original_request=(
            "Create a Python program that calculates an average "
            "and handles invalid input safely."
        ),
        step="Implement and verify the average calculation.",
        error="ZeroDivisionError: division by zero",
    )

    print("Recovery result:")
    print("────────────────────────────")
    print(result)
    print()

    assert result["status"] == "success"
    assert result["error"] is None
    assert result["output"]

    print("Repaired file:")
    print("────────────────────────────")
    print(buggy_file.read_text(encoding="utf-8"))

    print("\n✓ diagnose_and_repair() test passed")


if __name__ == "__main__":
    asyncio.run(main())
