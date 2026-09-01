import os 
from pathlib import Path
from langchain.tools import tool
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_tavily import TavilySearch

# 1. Load environment variables

load_dotenv()

if not os.getenv("OPENROUTER_API_KEY"):
    raise ValueError("OPENROUTER_API_KEY")

if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY is not set in .env")

# 2. Agent workspace

WORKSPACE = Path("agent_workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

# 3. Helper function to protect the workspace

def safe_path(filename: str) -> Path:
    """
    convert a user-provided filename into a safe path
    inside agent_workspace
    """

    file_path = (WORKSPACE / filename).resolve()

    if WORKSPACE not in file_path.parents:
        raise ValueError(
            "Access denied: the agent can only access "
            "files inside agent_workspace."
        )

    return file_path

# 4. CREATE FILE TOOL

@tool
def create_file(filename:str, content: str) -> str:
    """
    Create a new text file inside agent_workspace.

    Args:
        filename: Name/path of the file to create.
        content: Text content that should be written to the file.
    """
    try:
        file_path = safe_path(filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            content,
            encoding="utf-8"
        )
        return f"File created successfully: {file_path.relative_to(WORKSPACE)}"
    except Exception as e:
        return f"Error creating file: {e}"

# 5. READ FILE TOOL
@tool
def read_file(filename: str) -> str:
    """
    Read a text file from agent_workspace.

    Args:
        filename: Name/path of the file to read.
    """

    try:
        file_path = safe_path(filename)
        if not file_path.exists():
            return f"File not found:{filename}"
        if not file_path.is_file():
            return f"{filename} is not a file."

        return file_path.read_text(encoding="utf-8")

    except Exception as e:
        return f"Error reading file: {e}"

# 6. LIST FILES TOOL

@tool
def list_file() -> str:
    """
    List all files and directories inside agent_workspace.
    """

    try:
        items = []

        for path in WORKSPACE.rglob("*"):

            relative_path = path.relative_to(WORKSPACE)

            if path.is_file():
                items.append(f"FILE : {relative_path}")
            elif path.is_dir():
                items.append(f"DIR: {relative_path}")

        if not items : 
            return "The agent workspace is empty."

        return "\n".join(items)

    except Exception as e:
        return f"Error listing files: {e}"

# 7. WEB SEARCH TOOL

search = TavilySearch(
    max_result=5
)
# 8. CREATE THE AGENT

agent = create_agent(
    model="openrouter:openrouter/free",
    tools=[
        search,
        create_file,
        read_file,
        list_file,
    ],
    system_prompt= """
You are a helpful AI research and coding assistant.

You have access to the following tools:

1. Web search
   - Use it when the user asks for current or external information.

2. File creation
   - You can create files inside agent_workspace.

3. File reading
   - You can read files inside agent_workspace.

4. File listing
   - You can list files inside agent_workspace.

IMPORTANT RULES:

- Always use the appropriate tool when the user asks you
  to perform an action that requires it.
- Only access files inside agent_workspace.
- Never try to access files outside agent_workspace.
- Never invent the result of a tool.
- After using a tool, use its result to formulate your answer.
- Be clear and concise.

"""
)

# 9. TEST THE AGENT

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
Search the web for the latest LangChain agent documentation.

Then create a file called:

langchain_notes.md

inside the agent workspace.

The file should contain a short summary of:
- What an agent is
- What tools are
- How create_agent works
- How tool calling works
"""
            }
        ]
    }
)

# 10. DISPLAY THE AGENT'S MESSAGES

print("\n" + "=" * 60)
print("AGENT EXECUTION")
print("=" * 60)

for message in result["messages"]:
    print("\nTYPE:", message.type)

    if hasattr(message, "content"):
        print("CONTENT:", message.content)
    if hasattr(message, "tool_calls") and message.tool_calls:
        print("TOOL CALLS:", message.tool_calls)

    print("-" * 60)

# 11. FINAL ANSWER

print("\n" + "=" * 60)
print("FINAL ANSWER")
print("=" * 60)

print(result["messages"][-1].content)





