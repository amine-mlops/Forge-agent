import asyncio

from forge.agent import create_forge_agent
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
║       ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝          ║
║                                                          ║
║             AI Coding & Research Agent                   ║
║                         Forge V2                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


def print_banner():
    print(BANNER)
    print("  Model: OpenRouter / Free")
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


async def run_agent(agent, user_input):
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
    agent = create_forge_agent()

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

            # Commands
            
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

            # Agent

            print("\nForge is working...\n")

            response = await run_agent(agent, user_input)

            print(response)
            print()

    finally:
        await browser_manager.close()


if __name__ == "__main__":
    asyncio.run(cli())
