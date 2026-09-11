import asyncio

from forge.executor import execute_plan
from forge.state import clear_state, load_state


class FakeAgent:
    async def ainvoke(self, payload):
        raise RuntimeError("Simulated execution failure")


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

    # Verify structured failure result.
    assert len(results) == 1

    result = results[0]

    assert result["step"] == 1
    assert result["status"] == "failed"
    assert result["description"] == "Create project structure"
    assert result["error"] == "Step failed after 4 execution attempts."

    # Step 1 must NOT be marked as completed.
    state = load_state()

    assert state is not None
    assert state["status"] == "paused"
    assert state["completed_steps"] == []
    assert state["current_step"] == 1

    clear_state()

    print("\n✓ V2.8.2 failure detection test passed")


if __name__ == "__main__":
    asyncio.run(main())
