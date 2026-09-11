import asyncio

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from forge.agent import create_forge_agent
from forge.planner import create_planner, generate_plan
from forge.executor import execute_plan
from forge.state import load_state, clear_state
from tools.browser import browser_manager

from forge.ui import (
    console,
    show_banner,
    show_system_info,
    print_info,
    print_success,
    print_warning,
    print_error,
)


# Forge CLI Helpers

def print_help():
    """Display available Forge commands."""

    table = Table(
        title="Forge Commands",
        title_style="forge",
        border_style="cyan",
        show_header=True,
        header_style="bold white",
    )

    table.add_column("Command", style="command", width=12)
    table.add_column("Description", style="info")

    table.add_row("/help", "Show available commands")
    table.add_row("/status", "Show Forge system status")
    table.add_row("/tools", "Show available Forge tools")
    table.add_row("/resume", "Resume the last paused task")
    table.add_row("/clear", "Clear the terminal")
    table.add_row("/exit", "Exit Forge")

    console.print()
    console.print(table)
    console.print()

    console.print(
        "[muted]Anything else is sent to the Forge agent.[/muted]"
    )
    console.print()


def print_status():
    """Display Forge system status."""

    table = Table(
        title="Forge Status",
        title_style="forge",
        border_style="cyan",
        show_header=False,
    )

    table.add_column("Component", style="muted")
    table.add_column("Status", style="info")

    table.add_row("Model", "GLM 5.3 Flash")
    table.add_row("Workspace", "agent_workspace")
    table.add_row("Browser", "Playwright + Brave")
    table.add_row("Terminal", "Bubblewrap sandbox")
    table.add_row("Web", "Tavily")
    table.add_row("Planner", "[success]Enabled[/success]")
    table.add_row("Executor", "[success]Enabled[/success]")
    table.add_row("State", "[success]Enabled[/success]")
    table.add_row("Resume", "[success]Enabled[/success]")
    table.add_row("Status", "[success]● Ready[/success]")

    console.print()
    console.print(table)
    console.print()


def print_tools():
    """Display available Forge tools."""

    tools = [
        ("create_file", "Create a file"),
        ("read_file", "Read a file"),
        ("list_file", "List workspace files"),
        ("edit_file", "Edit a file"),
        ("search", "Search the web with Tavily"),
        ("browser_open", "Open a webpage"),
        ("browser_read", "Read webpage content"),
        ("browser_click", "Click on a webpage element"),
        ("browser_type", "Type into a webpage"),
        ("browser_screenshot", "Take a browser screenshot"),
        ("terminal_run", "Run commands in the sandbox"),
    ]

    table = Table(
        title="Forge Tools",
        title_style="forge",
        border_style="cyan",
        show_header=True,
        header_style="bold white",
    )

    table.add_column("Tool", style="command")
    table.add_column("Purpose", style="info")

    for name, description in tools:
        table.add_row(name, description)

    console.print()
    console.print(table)
    console.print()


def print_plan(plan: str):
    """
    Display the planner output in the Forge CLI.
    """

    lines = []

    for line in plan.splitlines():

        if line.strip() == "PLAN":
            continue

        if line.strip():
            lines.append(
                Text(line, style="step")
            )

    if not lines:
        lines.append(
            Text("No execution steps returned.", style="warning")
        )

    content = Group(*lines)

    panel = Panel(
        content,
        title="Forge Plan",
        title_align="left",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
    console.print()


def print_execution_result(result: dict):
    """Display a single execution result."""

    step = result.get("step", "?")
    description = result.get("description", "Unknown step")
    status = result.get("status", "unknown")
    output = result.get("output", "")
    error = result.get("error")

    if status == "success":

        console.print(
            f"[success]✓[/success] "
            f"[bold]Step {step} completed[/bold]"
        )

        if output:
            console.print(
                Panel(
                    output,
                    title=f"Step {step} Output",
                    border_style="green",
                    padding=(1, 2),
                )
            )

    else:

        console.print(
            f"[error]✗[/error] "
            f"[bold]Step {step} failed[/bold]"
        )

        if error:
            console.print(
                Panel(
                    error,
                    title=f"Step {step} Error",
                    border_style="red",
                    padding=(1, 2),
                )
            )


def print_execution_summary(results: list[dict]):
    """Display the final execution summary."""

    if not results:
        print_warning("No execution results returned.")
        return

    table = Table(
        title="Forge Execution Summary",
        title_style="forge",
        border_style="cyan",
        show_header=True,
        header_style="bold white",
    )

    table.add_column("Step", justify="center", style="command")
    table.add_column("Description", style="info")
    table.add_column("Status", justify="center")

    for result in results:

        status = result.get("status")

        if status == "success":
            status_display = "[success]✓ Success[/success]"
        else:
            status_display = "[error]✗ Failed[/error]"

        table.add_row(
            str(result.get("step", "?")),
            result.get("description", "Unknown"),
            status_display,
        )

    console.print()
    console.print(table)
    console.print()


# Agent Execution


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


# Resume

async def resume_task(agent):
    """
    Resume the most recently paused Forge task.
    """

    state = load_state()

    if state is None:

        print_warning("No saved Forge task found.")
        return

    status = state.get("status")

    if status != "paused":

        if status == "completed":
            print_info("The saved task is already completed.")

        else:
            print_warning(
                f"Cannot resume task with status: {status}"
            )

        return

    original_request = state.get("original_request")
    plan = state.get("plan")
    completed_steps = state.get(
        "completed_steps",
        [],
    )
    current_step = state.get("current_step")

    if not original_request or not plan:

        print_error(
            "Saved Forge state is incomplete. Cannot resume."
        )

        return

    console.print()

    console.print(
        Panel(
            Text(
                "Resuming paused Forge task...",
                style="bold white",
            ),
            border_style="cyan",
        )
    )

    console.print()

    info_table = Table(
        show_header=False,
        box=None,
    )

    info_table.add_column(
        "Property",
        style="muted",
    )

    info_table.add_column(
        "Value",
        style="info",
    )

    info_table.add_row(
        "Current step",
        str(current_step),
    )

    info_table.add_row(
        "Completed steps",
        str(completed_steps),
    )

    console.print(info_table)
    console.print()

    print_plan(plan)

    print_info("Continuing execution...")
    console.print()

    results = await execute_plan(
        agent=agent,
        plan=plan,
        original_request=original_request,
        completed_steps=completed_steps,
    )

    print_execution_summary(results)

    # Check final state after execution.
    final_state = load_state()

    if final_state and final_state.get("status") == "completed":

        print_success("Task completed successfully.")

        clear_state()

        print_success("Saved state cleared.")

    else:

        print_warning(
            "Task is still paused."
        )

        print_info(
            "The saved state was preserved for another /resume."
        )

    console.print()


# Main CLI

async def cli():

    # Create Forge components.
    agent = create_forge_agent()
    planner = create_planner()

    # Initial Forge interface.
    show_banner()
    show_system_info()

    try:

        while True:

            try:

                user_input = console.input(
                    "[forge]forge[/forge] [muted]❯[/muted] "
                ).strip()

            except (KeyboardInterrupt, EOFError):

                console.print()
                print_info("Exiting Forge...")
                break

            if not user_input:
                continue

            
            # CLI COMMANDS
            
            if user_input == "/exit":

                console.print()
                print_success("Goodbye.")
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

                    print_error(
                        f"Forge resume error: {e}"
                    )

                continue

            if user_input == "/clear":

                console.clear()

                show_banner()
                show_system_info()

                continue

            
            # PLANNING + EXECUTION
            
            console.print()

            console.print(
                Panel(
                    Text(
                        "Forge is working...",
                        style="bold white",
                    ),
                    border_style="cyan",
                )
            )

            console.print()

            try:

                
                # Step 1: Generate plan
                
                plan = await generate_plan(
                    planner,
                    user_input,
                )

                
                # Simple task
                
                if plan == "SIMPLE":

                    print_info(
                        "Simple task detected."
                    )

                    console.print()

                    response = await run_agent(
                        agent,
                        user_input,
                    )

                    console.print(
                        Panel(
                            response,
                            title="Forge",
                            border_style="cyan",
                            padding=(1, 2),
                        )
                    )

                    console.print()

            
                # Complex task
                
                else:

                    # Display generated plan.
                    print_plan(plan)

                    print_info(
                        "Executing plan..."
                    )

                    console.print()

                    # Execute every plan step.
                    results = await execute_plan(
                        agent,
                        plan,
                        user_input,
                    )

                    # Execution summary.
                    print_execution_summary(results)

            except Exception as e:

                print_error(
                    f"Forge error: {e}"
                )

                console.print()

    finally:

        # Always close the persistent browser.
        await browser_manager.close()


# Entry Point

if __name__ == "__main__":
    asyncio.run(cli())


