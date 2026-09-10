import asyncio

from forge.agent import create_forge_agent
from forge.planner import create_planner, generate_plan
from forge.executor import execute_plan
from forge.state import load_state, clear_state
from tools.browser import browser_manager


# FORGE CLI

BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       ███████╗ ██████╗ ██████╗  ██████╗ ███████╗         ║
║       ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝         ║
║       █████╗  ██║   ██║██████╔╝██║  ███╗█████╗           ║
║       ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝           ║
║       ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗         ║
║       ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝          ║
║                                                          ║
║             AI Coding & Research Agent                   ║
║                         Forge V2                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


def print_banner():
    print(BANNER)
    print("  Model: GLM 5.3 Flash")
    print("  Workspace: agent_workspace")
    print("  Status: ● Ready")
    print()
    print("  Type /help for commands.")
    print("  Type /exit to quit.")
    print()


def print_help():
    print("""
Forge commands:

  /help       Show this help message
  /status     Show Forge status
  /tools      Show available tools
  /resume     Resume the last paused task
  /clear      Clear the terminal
  /exit       Exit Forge

Anything else is sent to the Forge agent.
""")


def print_status():
    print("""
Forge V2 Status
────────────────────────────
Model:      GLM 5.3 Flash
Workspace:  agent_workspace
Browser:    Playwright + Brave
Terminal:   Bubblewrap sandbox
Web:        Tavily
Planner:    Enabled
Executor:   Enabled
State:      Enabled
Resume:     Enabled
Status:     ● Ready
""")


def print_tools():
    print("""
Forge Tools
────────────────────────────
• create_file
• read_file
• list_file
• edit_file
• web search
• browser_open
• browser_read
• browser_click
• browser_type
• browser_screenshot
• terminal_run
""")


def print_plan(plan):
    """
    Display the planner output in the Forge CLI.
    """

    print("┌─ Forge Plan ────────────────────────────────┐")

    for line in plan.splitlines():

        if line.strip() == "PLAN":
            continue

        if line.strip():
            print(f"│ {line:<44} │")

    print("└──────────────────────────────────────────────┘")
    print()


async def run_agent(agent, user_input):
    """
    Send a request directly to the Forge execution agent.

    Used for simple tasks that don't require planning.
    """

    try:
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            }
        )

        return result["messages"][-1].content

    except Exception as e:
        return f"Forge error: {e}"


async def resume_task(agent):
    """
    Resume the most recently paused Forge task.
    """

    state = load_state()

    if state is None:
        print("\nNo saved Forge task found.\n")
        return

    status = state.get("status")

    if status != "paused":
        if status == "completed":
            print("\nThe saved task is already completed.\n")
        else:
            print(f"\nCannot resume task with status: {status}\n")
        return

    original_request = state.get("original_request")
    plan = state.get("plan")
    completed_steps = state.get("completed_steps", [])
    current_step = state.get("current_step")

    if not original_request or not plan:
        print("\nSaved Forge state is incomplete. Cannot resume.\n")
        return

    print("\nResuming paused Forge task...\n")

    print(f"Current step: {current_step}")
    print(f"Completed steps: {completed_steps}")
    print()

    print_plan(plan)

    print("Continuing execution...\n")

    results = await execute_plan(
        agent=agent,
        plan=plan,
        original_request=original_request,
        completed_steps=completed_steps,
    )

    print("\nForge resume summary")
    print("────────────────────────────")

    for result in results:

        print(
            f"\nStep {result['step']}: "
            f"{result['description']}"
        )

        print(result["result"])

    # Check final state after execution.
    final_state = load_state()

    if final_state and final_state.get("status") == "completed":
        print("\n✓ Task completed successfully.")
        clear_state()
        print("✓ Saved state cleared.")

    else:
        print("\n⚠ Task is still paused.")
        print("The saved state was preserved for another /resume.")

    print()


async def cli():

    # Create Forge components
    agent = create_forge_agent()
    planner = create_planner()

    print_banner()

    try:

        while True:

            try:
                user_input = input("forge ❯ ").strip()

            except (KeyboardInterrupt, EOFError):
                print("\n")
                break

            if not user_input:
                continue


            # CLI COMMANDS

            if user_input == "/exit":
                print("\nGoodbye 👋")
                break

            if user_input == "/help":
                print_help()
                continue

            if user_input == "/status":
                print_status()
                continue

            if user_input == "/tools":
                print_tools()
                continue

            if user_input == "/resume":
                try:
                    await resume_task(agent)
                except Exception as e:
                    print(f"\nForge resume error: {e}\n")
                continue

            if user_input == "/clear":
                print("\033[2J\033[H", end="")
                print_banner()
                continue


            # PLANNING + EXECUTION

            print("\nForge is working...\n")

            try:

                # Step 1: Generate plan

                plan = await generate_plan(
                    planner,
                    user_input,
                )


                # Simple task

                if plan == "SIMPLE":

                    print("Simple task detected.\n")

                    response = await run_agent(
                        agent,
                        user_input,
                    )

                    print(response)
                    print()


                # Complex task

                else:

                    # Display generated plan
                    print_plan(plan)

                    print("Executing plan...\n")

                    # Execute every plan step
                    results = await execute_plan(
                        agent,
                        plan,
                        user_input,
                    )

                    # Execution summary

                    print("\nForge execution summary")
                    print("────────────────────────────")

                    for result in results:

                        print(
                            f"\nStep {result['step']}: "
                            f"{result['description']}"
                        )

                        print(result["result"])

                    print()

            except Exception as e:

                print(f"Forge error: {e}")
                print()

    finally:

        # Always close the persistent browser
        await browser_manager.close()


if __name__ == "__main__":
    asyncio.run(cli())



