import asyncio

from forge.executor import execute_plan
from forge.state import clear_state, load_state


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeAgent:
    async def ainvoke(self, payload):
        return {
            "messages": [
                FakeMessage("Step completed successfully.")
            ]
        }


async def main():
    clear_state()

    agent = FakeAgent()

    plan = """PLAN
1. Create project structure
2. Implement main functionality
"""

    results = await execute_plan(
        agent=agent,
        plan=plan,
        original_request="Create a test project",
    )

    print("\nResults:")
    print(results)

    assert len(results) == 2

    assert results[0]["step"] == 1
    assert results[0]["status"] == "success"
    assert results[0]["output"] == "Step completed successfully."
    assert results[0]["error"] is None

    assert results[1]["step"] == 2
    assert results[1]["status"] == "success"

    state = load_state()

    assert state is not None
    assert state["status"] == "completed"
    assert state["completed_steps"] == [1, 2]

    clear_state()

    print("\n✓ V2.8.1 structured execution result test passed")


if __name__ == "__main__":
    asyncio.run(main())
