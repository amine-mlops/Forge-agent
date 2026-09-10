import json
from pathlib import Path


STATE_FILE = Path("forge/.forge_state.json")


def save_state(
    original_request: str,
    plan: str,
    completed_steps: list[int],
    current_step: int | None,
    status: str,
):
    state = {
        "original_request": original_request,
        "plan": plan,
        "completed_steps": completed_steps,
        "current_step": current_step,
        "status": status,
    }

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)


def load_state() -> dict | None:
    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def clear_state():
    if STATE_FILE.exists():
        STATE_FILE.unlink()
