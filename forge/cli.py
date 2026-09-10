
import asyncio

from forge.agent import create_forge_agent
from forge.planner import create_planner, generate_plan
from forge.executor import execute_plan
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
  /clear      Clear the terminal
  /exit       Exit Forge

Anything else is sent to the Forge agent.
""")


def print_status():
    print("""
Forge V2 Status
────────────────────────────
Model:      OpenRouter / Free
Workspace:  agent_workspace
Browser:    Playwright + Brave
Terminal:   Bubblewrap sandbox
Web:        Tavily
Planner:    Enabled
Executor:   Enabled
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

