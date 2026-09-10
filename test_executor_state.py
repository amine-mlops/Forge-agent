import asyncio

from forge.executor import execute_plan
from forge.state import load_state, clear_state


class FakeAgent:
    def __init__(self):
        self.calls = 0

    async def ainvoke(self, payload):
        self.calls += 1

        # Simulate two successful steps, then a failure.
        if self.calls == 3:
            raise RuntimeError("Simulated failure for resume test")

        return {
            "messages": [
                type(
                    "Message",
                    (),
                    {"content": "Step completed successfully"},
                )()
            ]
        }


async def main():
    clear_state()

    plan = """PLAN
1. Create project structure
2. Implement main functionality
3. Write tests
4. Create README
"""

    agent = FakeAgent()

    print("Starting simulated execution...\n")

    results = await execute_plan(
        agent=agent,
        plan=plan,
        original_request="Create a test project",
    )

    print("\nExecution results:")
    for result in results:
        print(result)

    print("\nSaved state:")
    state = load_state()
    print(state)

    print("\nChecking paused state...")

    assert state is not None
    assert state["completed_steps"] == [1, 2]
    assert state["current_step"] == 3
    assert state["status"] == "paused"

    print("✓ Completed steps are correct")
    print("✓ Current step is correct")
    print("✓ Status is paused")

    print("\n✓ Test state cleaned up")
    print("\nAll executor state tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
