import asyncio

from forge.executor import execute_step_with_recovery


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeAgent:
    def __init__(self):
        self.execution_calls = 0

    async def ainvoke(self, payload):
        prompt = payload["messages"][0]["content"]

        if "failure recovery component" in prompt:
            return {
                "messages": [
                    FakeMessage(
                        "Repair completed successfully."
                    )
                ]
            }

        self.execution_calls += 1

        if self.execution_calls < 3:
            raise RuntimeError(
                f"Simulated failure {self.execution_calls}"
            )

        return {
            "messages": [
                FakeMessage(
                    "Step successfully completed."
                )
            ]
        }


async def main():

    agent = FakeAgent()

    result = await execute_step_with_recovery(
        agent=agent,
        original_request="Create a test project.",
        step_number=1,
        step="Implement the main functionality.",
    )

    print("\nFinal result:")
    print(result)

    assert result["step"] == 1
    assert result["status"] == "success"
    assert result["output"] == "Step successfully completed."

    assert agent.execution_calls == 3

    print("\n✓ Automatic retry test passed")


if __name__ == "__main__":
    asyncio.run(main())
