from pathlib import Path
from langchain.tools import tool

WORKSPACE = Path("agent_workspace").resolve()

def safe_path(filename: str) -> Path:
    """Return a path guaranteed to stay inside the workspace."""

    file_path = (WORKSPACE / filename).resolve()

    if WORKSPACE not in file_path.parents:
        raise ValueError(
            "Access denied: path is outside agent_workspace."
        )
    return file_path
@tool
def create_file(filename: str, content: str) -> str:
    """Create a text file inside agent_workspace."""

    try:
        file_path = safe_path(filename)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return f"Created: {file_path.relative_to(WORKSPACE)}"

    except Exception as e:
        return f"Error: {e}"


@tool
def read_file(filename: str) -> str:
    """Read a text file from agent_workspace."""

    try:
        file_path = safe_path(filename)

        if not file_path.exists():
            return f"File not found: {filename}"

        if not file_path.is_file():
            return f"{filename} is not a file."

        return file_path.read_text(
            encoding="utf-8"
        )

    except Exception as e:
        return f"Error: {e}"


@tool
def list_file() -> str:
    """List files and directories inside agent_workspace."""

    try:
        items = []

        for path in WORKSPACE.rglob("*"):

            relative = path.relative_to(WORKSPACE)

            if path.is_file():
                items.append(f"FILE: {relative}")

            elif path.is_dir():
                items.append(f"DIR: {relative}")

        if not items:
            return "Workspace is empty."

        return "\n".join(items)

    except Exception as e:
        return f"Error: {e}"

@tool
def edit_file(filename: str, content: str) -> str:
    """Replace the contents of an existing text file."""

    try:
        file_path = safe_path(filename)

        if not file_path.exists():
            return f"File not found: {filename}"

        if not file_path.is_file():
            return f"{filename} is not a file."

        file_path.write_text(
            content,
            encoding="utf-8"
        )
        return f"Update: {file_path.relative_to(WORKSPACE)}"

    except Exception as e:
        return f"Error: {e}"
    

