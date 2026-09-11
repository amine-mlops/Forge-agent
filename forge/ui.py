from rich.spinner import Spinner
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme


# ============================================================
# Forge Terminal Theme
# ============================================================

FORGE_THEME = Theme(
    {
        "forge": "bold cyan",
        "title": "bold white",
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "muted": "dim",
        "command": "bold cyan",
        "step": "bold white",
    }
)

console = Console(theme=FORGE_THEME)


# ============================================================
# Forge Logo
# ============================================================

FORGE_LOGO = r"""
███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
"""


# ============================================================
# Basic Messages
# ============================================================

def print_info(message: str):
    console.print(f"[info]→[/info] {message}")


def print_success(message: str):
    console.print(f"[success]✓[/success] {message}")


def print_warning(message: str):
    console.print(f"[warning]⚠[/warning] {message}")


def print_error(message: str):
    console.print(f"[error]✗[/error] {message}")


# ============================================================
# Banner
# ============================================================

def show_banner(version: str = "v2.8.4"):
    logo = Text(FORGE_LOGO, style="forge")

    subtitle = Text(
        "\nAI RESEARCH & CODING ASSISTANT",
        style="title",
    )

    version_text = Text(
        f"\nForge {version}",
        style="muted",
    )

    content = Text.assemble(
        logo,
        subtitle,
        version_text,
    )

    panel = Panel(
        Align.center(content),
        border_style="cyan",
        padding=(1, 4),
    )

    console.print()
    console.print(panel)
    console.print()


# ============================================================
# System Information
# ============================================================

def show_system_info(
    workspace: str = "agent_workspace",
    model: str = "GLM 5.3 Flash",
):
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
    )

    table.add_column(style="muted")
    table.add_column(style="info")

    table.add_row("Workspace", workspace)
    table.add_row("Model", model)
    table.add_row(
        "Status",
        "[success]Ready[/success]",
    )

    console.print(table)
    console.print()
# ============================================================
# Execution UI
# ============================================================

def show_step_header(
    step_number: int,
    total_steps: int,
    description: str,
):
    """Display a Forge execution step."""

    content = Text()

    content.append(
        f"Step {step_number} / {total_steps}\n\n",
        style="bold white",
    )

    content.append(
        description,
        style="info",
    )

    panel = Panel(
        content,
        title="Forge Execution",
        title_align="left",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)


def show_attempt(
    attempt: int,
    max_attempts: int,
):
    """Display the current execution attempt."""

    console.print(
        f"  [info]●[/info] "
        f"Attempt [bold]{attempt}/{max_attempts}[/bold]"
    )


def show_step_success(step_number: int):
    """Display a successful step."""

    console.print(
        f"  [success]✓[/success] "
        f"Step {step_number} completed"
    )

    console.print()


def show_step_failure(
    step_number: int,
    error: str | None = None,
):
    """Display a failed step."""

    console.print(
        f"  [error]✗[/error] "
        f"Step {step_number} failed"
    )

    if error:
        console.print(
            Panel(
                error,
                title="Error",
                border_style="red",
                padding=(1, 2),
            )
        )

    console.print()


def show_recovery_start():
    """Display recovery start."""

    console.print(
        "  [warning]⚠[/warning] "
        "[bold yellow]Diagnosing failure...[/bold yellow]"
    )


def show_recovery_success():
    """Display successful repair."""

    console.print(
        "  [success]✓[/success] "
        "Repair completed"
    )

    console.print(
        "  [info]→[/info] Retrying step..."
    )


def show_recovery_failure(error: str | None = None):
    """Display failed repair."""

    console.print(
        "  [error]✗[/error] "
        "Repair failed"
    )

    if error:
        console.print(
            f"    [error]{error}[/error]"
        )


def show_task_success():
    """Display successful task completion."""

    console.print(
        Panel(
            Text(
                "✓  Task completed successfully",
                style="bold green",
            ),
            border_style="green",
            padding=(1, 2),
        )
    )


def show_task_paused():
    """Display paused task state."""

    console.print(
        Panel(
            Text(
                "⚠  Task paused\n\n"
                "Saved state is available for /resume.",
                style="bold yellow",
            ),
            border_style="yellow",
            padding=(1, 2),
        )
    )
