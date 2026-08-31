from dataclasses import dataclass


# ============================================================
# COMPARISON RESULT
# ============================================================

@dataclass
class ComparisonResult:
    baseline_passed: int
    baseline_failed: int
    current_passed: int
    current_failed: int
    improvement: int
    regression: int
    status: str


# ============================================================
# PARSE PYTEST RESULT
# ============================================================

def parse_test_result(output: str) -> tuple[int, int]:
    """
    Extract passed and failed test counts from pytest output.
    """

    passed = 0
    failed = 0

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        parts = line.replace(",", "").split()

        for index, part in enumerate(parts):

            if part == "passed":

                try:
                    passed = int(parts[index - 1])
                except (ValueError, IndexError):
                    pass

            if part == "failed":

                try:
                    failed = int(parts[index - 1])
                except (ValueError, IndexError):
                    pass

    return passed, failed


# ============================================================
# COMPARE RESULTS
# ============================================================

def compare_results(
    baseline_output: str,
    current_output: str
) -> ComparisonResult:

    baseline_passed, baseline_failed = (
        parse_test_result(
            baseline_output
        )
    )

    current_passed, current_failed = (
        parse_test_result(
            current_output
        )
    )

    improvement = max(
        0,
        current_passed - baseline_passed
    )

    regression = max(
        0,
        current_failed - baseline_failed
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if regression > 0:

        status = "REGRESSION"

    elif improvement > 0:

        status = "IMPROVED"

    elif (
        current_passed == baseline_passed
        and current_failed == baseline_failed
    ):

        status = "UNCHANGED"

    else:

        status = "CHANGED"

    return ComparisonResult(
        baseline_passed=baseline_passed,
        baseline_failed=baseline_failed,
        current_passed=current_passed,
        current_failed=current_failed,
        improvement=improvement,
        regression=regression,
        status=status
    )


# ============================================================
# DISPLAY
# ============================================================

def print_comparison(
    result: ComparisonResult
):

    print()
    print("=" * 60)
    print("       📊 BASELINE VS PATCH COMPARISON")
    print("=" * 60)

    print()

    print(
        f"Baseline Passed : {result.baseline_passed}"
    )

    print(
        f"Baseline Failed : {result.baseline_failed}"
    )

    print()

    print(
        f"Current Passed  : {result.current_passed}"
    )

    print(
        f"Current Failed  : {result.current_failed}"
    )

    print()

    print(
        f"Tests Improved  : {result.improvement}"
    )

    print(
        f"Tests Regressed : {result.regression}"
    )

    print()

    if result.status == "REGRESSION":

        print(
            "❌ REGRESSION DETECTED"
        )

    elif result.status == "IMPROVED":

        print(
            "🎉 TEST RESULTS IMPROVED"
        )

    elif result.status == "UNCHANGED":

        print(
            "✅ TEST RESULTS UNCHANGED"
        )

    else:

        print(
            "ℹ TEST RESULTS CHANGED"
        )

    print()

    print(
        f"Status : {result.status}"
    )

    print()

    print("=" * 60)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    baseline = """
    1 failed, 1 passed in 0.20s
    """

    current = """
    2 passed in 0.15s
    """

    result = compare_results(
        baseline,
        current
    )

    print_comparison(
        result
    )