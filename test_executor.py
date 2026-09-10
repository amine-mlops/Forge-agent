from forge.executor import parse_plan


plan = """
PLAN
1. Create the project structure.
2. Implement the Todo application.
3. Write the tests.
4. Create the README.
5. Run the tests.
"""

steps = parse_plan(plan)

print("Parsed steps:")
print()

for i, step in enumerate(steps, start=1):
    print(f"{i}. {step}")
