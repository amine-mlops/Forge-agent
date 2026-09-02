import asyncio
from pathlib import Path

from langchain.tools import tool


# WORKSPACE

WORKSPACE = Path("agent_workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

# TERMINAL CONFIGURATION


TIMEOUT = 30
MAX_OUTPUT = 12000
BWRAP = "/usr/bin/bwrap"

# TERMINAL TOOL


@tool
async def terminal_run(command: str) -> str:
    """
    Execute a shell command inside the Forge sandbox.

    The command can read/write only the Forge workspace.
    The host filesystem is not mounted inside the sandbox.
    """

    try:
        
        # Basic validation
    
        if not command.strip():
            return "Terminal error: empty command."

        # Bubblewrap sandbox

        sandbox_command = [
            BWRAP,

            # Process lifetime
            
            "--die-with-parent",
            "--new-session",

            # Create isolated namespaces
        
            "--unshare-all",

            # We currently allow network access because
            # coding workflows may need pip, git, APIs, etc.
            "--share-net",

            # Read-only system environment
    
            "--ro-bind",
            "/usr",
            "/usr",

            "--ro-bind",
            "/bin",
            "/bin",

            "--ro-bind",
            "/lib",
            "/lib",

            "--ro-bind",
            "/lib64",
            "/lib64",

            # Basic system configuration needed by programs

            "--ro-bind-try",
            "/etc/resolv.conf",
            "/etc/resolv.conf",

            "--ro-bind-try",
            "/etc/hosts",
            "/etc/hosts",

            "--ro-bind-try",
            "/etc/nsswitch.conf",
            "/etc/nsswitch.conf",

            "--ro-bind-try",
            "/etc/ssl/certs",
            "/etc/ssl/certs",

            # Isolated /dev

            "--dev",
            "/dev",

            # Isolated /proc
  
            "--proc",
            "/proc",

            # Temporary filesystem

            "--tmpfs",
            "/tmp",

            # Forge workspace

            "--bind",
            str(WORKSPACE),
            "/workspace",

            "--chdir",
            "/workspace",

            # Environment

            "--clearenv",

            "--setenv",
            "HOME",
            "/workspace",

            "--setenv",
            "PATH",
            "/usr/local/bin:/usr/bin:/bin",

            "--setenv",
            "PYTHONUNBUFFERED",
            "1",

            # Shell

            "/bin/sh",
            "-c",
            command,
        ]

        # Execute asynchronously

        process = await asyncio.create_subprocess_exec(
            *sandbox_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=TIMEOUT,
            )

        except asyncio.TimeoutError:

            process.kill()
            await process.wait()

            return (
                f"Terminal timeout: command exceeded "
                f"{TIMEOUT} seconds."
            )

        # Decode output

        stdout_text = stdout.decode(
            "utf-8",
            errors="replace",
        )

        stderr_text = stderr.decode(
            "utf-8",
            errors="replace",
        )

        # Limit output size

        if len(stdout_text) > MAX_OUTPUT:
            stdout_text = (
                stdout_text[:MAX_OUTPUT]
                + "\n...[stdout truncated]"
            )

        if len(stderr_text) > MAX_OUTPUT:
            stderr_text = (
                stderr_text[:MAX_OUTPUT]
                + "\n...[stderr truncated]"
            )

        # Return result

        result = f"Exit code: {process.returncode}\n"

        if stdout_text:
            result += f"\nSTDOUT:\n{stdout_text}"

        if stderr_text:
            result += f"\nSTDERR:\n{stderr_text}"

        return result

    except Exception as e:
        return f"Terminal error: {e}"


