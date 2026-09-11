from forge.ui import (
    show_banner,
    show_system_info,
    show_step_header,
    show_attempt,
    show_step_success,
    show_step_failure,
    show_recovery_start,
    show_recovery_success,
    show_recovery_failure,
    show_task_success,
    show_task_paused,
)


def main():
    show_banner()
    show_system_info()

    show_step_header(
        step_number=1,
        total_steps=4,
        description="Create project structure",
    )

    show_attempt(
        attempt=1,
        max_attempts=4,
    )

    show_step_success(1)

    show_step_header(
        step_number=2,
        total_steps=4,
        description="Implement core functionality",
    )

    show_attempt(
        attempt=1,
        max_attempts=4,
    )

    show_recovery_start()

    show_recovery_success()

    show_attempt(
        attempt=2,
        max_attempts=4,
    )

    show_step_success(2)

    show_step_header(
        step_number=3,
        total_steps=4,
        description="Verify implementation",
    )

    show_attempt(
        attempt=1,
        max_attempts=4,
    )

    show_step_failure(
        step_number=3,
        error="Tests failed: 2 assertions did not pass.",
    )

    show_recovery_start()

    show_recovery_failure(
        error="Unable to repair the failing tests.",
    )

    show_task_paused()

    show_task_success()


if __name__ == "__main__":
    main()
