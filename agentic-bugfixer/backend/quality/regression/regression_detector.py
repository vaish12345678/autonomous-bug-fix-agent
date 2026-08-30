import subprocess
from dataclasses import dataclass


# ============================================================
# REGRESSION RESULT
# ============================================================

@dataclass
class RegressionResult:
    passed: bool
    total_tests: int
    failed_tests: int
    output: str
    message: str


# ============================================================
# REGRESSION DETECTOR
# ============================================================

def detect_regression(
    repository_path: str,
    baseline_output: str | None = None
) -> RegressionResult:
    """
    Run the complete test suite after a patch.

    A regression is detected when the repository test suite
    fails after the patch has been applied.
    """

    try:

        result = subprocess.run(
            [
                "pytest",
                "-q"
            ],
            cwd=repository_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        passed = result.returncode == 0

        total_tests = 0
        failed_tests = 0

        # ----------------------------------------------------
        # Extract pytest summary
        # ----------------------------------------------------

        for line in output.splitlines():

            line = line.strip()

            if "passed" in line:

                parts = line.split()

                for index, part in enumerate(parts):

                    if part == "passed":

                        try:
                            total_tests += int(
                                parts[index - 1]
                            )
                        except (ValueError, IndexError):
                            pass

                    if part == "failed":

                        try:
                            failed_tests += int(
                                parts[index - 1]
                            )
                        except (ValueError, IndexError):
                            pass

        # ----------------------------------------------------
        # Determine result
        # ----------------------------------------------------

        if passed:

            message = (
                "No regression detected. "
                "All tests passed after the patch."
            )

        else:

            message = (
                "Potential regression detected. "
                "The test suite failed after the patch."
            )

        return RegressionResult(
            passed=passed,
            total_tests=total_tests,
            failed_tests=failed_tests,
            output=output,
            message=message
        )

    except subprocess.TimeoutExpired:

        return RegressionResult(
            passed=False,
            total_tests=0,
            failed_tests=0,
            output="Tests timed out.",
            message=(
                "Regression status could not be verified "
                "because the test suite timed out."
            )
        )

    except Exception as error:

        return RegressionResult(
            passed=False,
            total_tests=0,
            failed_tests=0,
            output=str(error),
            message=(
                "Regression detection failed."
            )
        )


# ============================================================
# DISPLAY RESULT
# ============================================================

def print_regression_result(
    result: RegressionResult
):

    print()
    print("=" * 55)
    print("       🔍 REGRESSION DETECTION")
    print("=" * 55)

    print()

    if result.passed:

        print(
            "✅ REGRESSION CHECK PASSED"
        )

    else:

        print(
            "❌ REGRESSION DETECTED"
        )

    print()

    print(
        f"Total Tests : {result.total_tests}"
    )

    print(
        f"Failed Tests: {result.failed_tests}"
    )

    print()

    print(
        f"Result      : {result.message}"
    )

    print()

    print("=" * 55)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python -m "
            "backend.quality.regression.regression_detector "
            "<repository_path>"
        )

        raise SystemExit(1)

    repository = sys.argv[1]

    result = detect_regression(
        repository
    )

    print_regression_result(
        result
    )