import subprocess
import time
from pathlib import Path

from backend.execution.test_detector import (
    detect_test_command,
)


# ============================================================
# INTELLIGENT TEST EXECUTOR
# ============================================================

DEFAULT_TIMEOUT = 120


# ============================================================
# EXECUTE DETECTED TEST COMMAND
# ============================================================

def execute_tests(
    repo_path: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """
    Detect and execute the repository's test command.

    Returns a structured execution result.
    """

    repository = Path(
        repo_path
    ).resolve()

    if not repository.is_dir():
        raise FileNotFoundError(
            f"Repository not found: {repo_path}"
        )

    detection = detect_test_command(
        str(repository)
    )

    if not detection["detected"]:

        return {
            "success": False,
            "status": "NOT_DETECTED",
            "project_type": detection[
                "project_type"
            ],
            "framework": detection[
                "framework"
            ],
            "command": None,
            "exit_code": None,
            "runtime": 0.0,
            "output": detection[
                "reason"
            ],
        }

    command = detection["command"]

    print(
        "\n========== TEST EXECUTION ==========\n"
    )

    print(
        "Project Type : "
        + detection["project_type"]
    )

    print(
        "Framework    : "
        + str(detection["framework"])
    )

    print(
        "Command      : "
        + " ".join(command)
    )

    print(
        "\n▶ Running tests...\n"
    )

    start_time = time.perf_counter()

    try:

        result = subprocess.run(
            command,
            cwd=str(repository),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )

        runtime = (
            time.perf_counter()
            - start_time
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()

        passed = (
            result.returncode == 0
        )

        if passed:

            status = "PASSED"

            print(
                "\n✅ TESTS PASSED"
            )

        else:

            status = "FAILED"

            print(
                "\n❌ TESTS FAILED"
            )

        print(
            f"Exit Code    : "
            f"{result.returncode}"
        )

        print(
            f"Runtime      : "
            f"{runtime:.2f}s"
        )

        return {
            "success": passed,
            "status": status,
            "project_type": detection[
                "project_type"
            ],
            "framework": detection[
                "framework"
            ],
            "command": command,
            "exit_code": result.returncode,
            "runtime": round(
                runtime,
                3,
            ),
            "output": output,
        }

    except subprocess.TimeoutExpired as error:

        runtime = (
            time.perf_counter()
            - start_time
        )

        output = ""

        if error.stdout:
            output += str(
                error.stdout
            )

        if error.stderr:
            output += "\n" + str(
                error.stderr
            )

        print(
            "\n⏰ TEST EXECUTION TIMED OUT"
        )

        return {
            "success": False,
            "status": "TIMEOUT",
            "project_type": detection[
                "project_type"
            ],
            "framework": detection[
                "framework"
            ],
            "command": command,
            "exit_code": None,
            "runtime": round(
                runtime,
                3,
            ),
            "output": (
                output.strip()
                or "Tests timed out."
            ),
        }

    except FileNotFoundError as error:

        runtime = (
            time.perf_counter()
            - start_time
        )

        print(
            "\n❌ TEST COMMAND NOT AVAILABLE"
        )

        return {
            "success": False,
            "status": "COMMAND_NOT_FOUND",
            "project_type": detection[
                "project_type"
            ],
            "framework": detection[
                "framework"
            ],
            "command": command,
            "exit_code": None,
            "runtime": round(
                runtime,
                3,
            ),
            "output": str(error),
        }

    except Exception as error:

        runtime = (
            time.perf_counter()
            - start_time
        )

        print(
            "\n❌ TEST EXECUTION ERROR"
        )

        return {
            "success": False,
            "status": "ERROR",
            "project_type": detection[
                "project_type"
            ],
            "framework": detection[
                "framework"
            ],
            "command": command,
            "exit_code": None,
            "runtime": round(
                runtime,
                3,
            ),
            "output": str(error),
        }


# ============================================================
# STANDALONE DEMO
# ============================================================

def main():

    import sys

    if len(sys.argv) > 1:

        repository = sys.argv[1]

    else:

        repository = (
            Path(__file__).resolve()
            .parents[2]
            / "benchmarks"
            / "bug_01"
            / "repo"
        )

    print(
        "\n" + "=" * 60
    )

    print(
        "       ▶️ INTELLIGENT TEST EXECUTOR"
    )

    print(
        "=" * 60
    )

    print(
        f"\nRepository:\n{repository}"
    )

    result = execute_tests(
        str(repository)
    )

    print(
        "\n========== EXECUTION RESULT ==========\n"
    )

    print(
        f"Status      : "
        f"{result['status']}"
    )

    print(
        f"Exit Code   : "
        f"{result['exit_code']}"
    )

    print(
        f"Runtime     : "
        f"{result['runtime']}s"
    )

    print(
        "\n========== TEST OUTPUT ==========\n"
    )

    print(
        result["output"]
    )

    print(
        "\n" + "=" * 60
    )


if __name__ == "__main__":
    main()