from forge.state import save_state, load_state, clear_state


print("Saving state...")

save_state(
    original_request="Create an expense tracker",
    plan="""PLAN
1. Create expense module
2. Create CLI
3. Create tests
4. Create README
5. Run tests
""",
    completed_steps=[1, 2],
    current_step=3,
    status="paused",
)

print("Loading state...")

state = load_state()

print(state)

print("\nChecking values...")

assert state["original_request"] == "Create an expense tracker"
assert state["completed_steps"] == [1, 2]
assert state["current_step"] == 3
assert state["status"] == "paused"

print("✓ State data is correct")

print("\nClearing state...")

clear_state()

assert load_state() is None

print("✓ State cleared")

print("\nAll state tests passed!")
