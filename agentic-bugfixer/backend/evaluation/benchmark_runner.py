import json
import time
import subprocess
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

BENCHMARKS_DIR = (
    BASE_DIR / "benchmarks"
)

REPORT_DIR = (
    BASE_DIR
    / "evaluation"
    / "reports"
)

REPORT_FILE = (
    REPORT_DIR
    / "benchmark_results.json"
)


# ============================================================
# DISCOVER BENCHMARKS
# ============================================================

def get_benchmarks():
    """
    Discover all valid benchmark directories.
    """

    if not BENCHMARKS_DIR.exists():

        raise FileNotFoundError(
            f"Benchmarks directory not found: "
            f"{BENCHMARKS_DIR}"
        )

    benchmarks = []

    for directory in BENCHMARKS_DIR.iterdir():

        if not directory.is_dir():
            continue

        if not directory.name.startswith("bug_"):
            continue

        issue_file = (
            directory / "issue.txt"
        )

        repo_directory = (
            directory / "repo"
        )

        if (
            issue_file.is_file()
            and repo_directory.is_dir()
        ):

            benchmarks.append(
                directory
            )

    benchmarks.sort(
        key=lambda path: path.name
    )

    return benchmarks


# ============================================================
# RUN BENCHMARK TESTS
# ============================================================

def run_benchmark(benchmark):
    """
    Run the tests belonging to one benchmark.
    """

    repo_path = (
        benchmark / "repo"
    )

    start_time = time.perf_counter()

    try:

        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "-q"
            ],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        runtime = (
            time.perf_counter()
            - start_time
        )

        output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        return {

            "benchmark":
                benchmark.name,

            "passed":
                result.returncode == 0,

            "runtime_seconds":
                round(runtime, 2),

            "output":
                output.strip()
        }

    except subprocess.TimeoutExpired:

        runtime = (
            time.perf_counter()
            - start_time
        )

        return {

            "benchmark":
                benchmark.name,

            "passed":
                False,

            "runtime_seconds":
                round(runtime, 2),

            "output":
                "Benchmark timed out."
        }

    except Exception as error:

        runtime = (
            time.perf_counter()
            - start_time
        )

        return {

            "benchmark":
                benchmark.name,

            "passed":
                False,

            "runtime_seconds":
                round(runtime, 2),

            "output":
                str(error)
        }


# ============================================================
# RUN ALL BENCHMARKS
# ============================================================

def run_all_benchmarks():

    benchmarks = get_benchmarks()

    if not benchmarks:

        raise RuntimeError(
            "No benchmarks found."
        )

    results = []

    print()
    print("=" * 70)
    print(
        "       🤖 AUTONOMOUS BUG FIX BENCHMARK RUNNER"
    )
    print("=" * 70)

    print()
    print(
        f"Discovered benchmarks: "
        f"{len(benchmarks)}"
    )

    print()

    for benchmark in benchmarks:

        print(
            f"▶ Running {benchmark.name}..."
        )

        result = run_benchmark(
            benchmark
        )

        results.append(result)

        if result["passed"]:

            print(
                f"  ✓ PASS "
                f"({result['runtime_seconds']:.2f}s)"
            )

        else:

            print(
                f"  ✗ FAIL "
                f"({result['runtime_seconds']:.2f}s)"
            )

    return results


# ============================================================
# BUILD SUMMARY
# ============================================================

def build_summary(results):

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = (
        total - passed
    )

    success_rate = (
        (passed / total) * 100
        if total
        else 0
    )

    average_runtime = (
        sum(
            result["runtime_seconds"]
            for result in results
        ) / total
        if total
        else 0
    )

    return {

        "total_benchmarks":
            total,

        "passed":
            passed,

        "failed":
            failed,

        "success_rate":
            round(
                success_rate,
                2
            ),

        "average_runtime_seconds":
            round(
                average_runtime,
                2
            )
    }


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    results,
    summary
):

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report = {

        "summary":
            summary,

        "benchmarks":
            results
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=4
        ),
        encoding="utf-8"
    )

    return REPORT_FILE


# ============================================================
# DISPLAY FINAL REPORT
# ============================================================

def display_report(
    results,
    summary
):

    print()

    print("=" * 70)
    print(
        "                    FINAL RESULTS"
    )
    print("=" * 70)

    print()

    print(
        f"Total Benchmarks : "
        f"{summary['total_benchmarks']}"
    )

    print(
        f"Passed           : "
        f"{summary['passed']}"
    )

    print(
        f"Failed           : "
        f"{summary['failed']}"
    )

    print(
        f"Success Rate     : "
        f"{summary['success_rate']:.2f}%"
    )

    print(
        f"Average Runtime  : "
        f"{summary['average_runtime_seconds']:.2f}s"
    )

    print()

    print(
        "Benchmark Results:"
    )

    print()

    for result in results:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"  {result['benchmark']:<15}"
            f"{status:<8}"
            f"{result['runtime_seconds']:.2f}s"
        )

    print()

    if summary["success_rate"] == 100:

        print(
            "🏆 SYSTEM STATUS: EXCELLENT"
        )

    elif summary["success_rate"] >= 80:

        print(
            "✅ SYSTEM STATUS: GOOD"
        )

    elif summary["success_rate"] >= 50:

        print(
            "⚠ SYSTEM STATUS: NEEDS IMPROVEMENT"
        )

    else:

        print(
            "❌ SYSTEM STATUS: CRITICAL"
        )

    print()

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    results = run_all_benchmarks()

    summary = build_summary(
        results
    )

    report_file = save_report(
        results,
        summary
    )

    display_report(
        results,
        summary
    )

    print()

    print(
        "✓ Evaluation report saved to:"
    )

    print(
        report_file
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()