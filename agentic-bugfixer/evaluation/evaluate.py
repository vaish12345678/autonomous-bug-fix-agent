import json
import subprocess
import sys
import time
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = ROOT / "benchmarks"

RESULTS_DIR = ROOT / "evaluation" / "results"
RESULTS_FILE = RESULTS_DIR / "evaluation_results.json"


# ============================================================
# RUN ONE BENCHMARK
# ============================================================

def run_benchmark(benchmark_dir: Path) -> dict:
    """
    Run pytest for a single benchmark repository.
    """

    repo_dir = benchmark_dir / "repo"

    print("\n" + "-" * 60)
    print(f"Running benchmark: {benchmark_dir.name}")
    print(f"Repository: {repo_dir}")
    print("-" * 60)

    if not repo_dir.exists():
        return {
            "benchmark": benchmark_dir.name,
            "passed": False,
            "runtime_seconds": 0,
            "output": "Repository directory not found."
        }

    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q"
            ],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=120
        )

        runtime = time.perf_counter() - start_time

        output = (
            result.stdout
            + "\n"
            + result.stderr
        ).strip()

        passed = result.returncode == 0

        if passed:
            print("✓ PASSED")
        else:
            print("❌ FAILED")

        print(f"Runtime: {runtime:.2f}s")

        if output:
            print(output)

        return {
            "benchmark": benchmark_dir.name,
            "passed": passed,
            "runtime_seconds": round(runtime, 4),
            "output": output
        }

    except subprocess.TimeoutExpired:
        runtime = time.perf_counter() - start_time

        print("❌ TIMEOUT")

        return {
            "benchmark": benchmark_dir.name,
            "passed": False,
            "runtime_seconds": round(runtime, 4),
            "output": "Tests timed out after 120 seconds."
        }

    except Exception as error:
        runtime = time.perf_counter() - start_time

        print(f"❌ ERROR: {error}")

        return {
            "benchmark": benchmark_dir.name,
            "passed": False,
            "runtime_seconds": round(runtime, 4),
            "output": str(error)
        }


# ============================================================
# FIND BENCHMARKS
# ============================================================

def get_benchmarks():
    """
    Discover all valid bug benchmarks.
    """

    if not BENCHMARKS.exists():
        raise FileNotFoundError(
            f"Benchmarks directory not found: {BENCHMARKS}"
        )

    benchmarks = []

    for directory in BENCHMARKS.iterdir():

        if not directory.is_dir():
            continue

        if not directory.name.startswith("bug_"):
            continue

        issue_file = directory / "issue.txt"
        repo_directory = directory / "repo"

        if (
            issue_file.is_file()
            and repo_directory.is_dir()
        ):
            benchmarks.append(directory)

    benchmarks.sort(
        key=lambda path: path.name
    )

    return benchmarks


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results: list):
    """
    Save complete evaluation results as JSON.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total - passed

    total_runtime = sum(
        result["runtime_seconds"]
        for result in results
    )

    average_runtime = (
        total_runtime / total
        if total > 0
        else 0
    )

    success_rate = (
        (passed / total) * 100
        if total > 0
        else 0
    )

    evaluation_report = {
        "summary": {
            "total_benchmarks": total,
            "passed": passed,
            "failed": failed,
            "success_rate_percent": round(
                success_rate,
                2
            ),
            "total_runtime_seconds": round(
                total_runtime,
                4
            ),
            "average_runtime_seconds": round(
                average_runtime,
                4
            )
        },
        "results": results
    }

    RESULTS_FILE.write_text(
        json.dumps(
            evaluation_report,
            indent=2
        ),
        encoding="utf-8"
    )

    return evaluation_report


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(report: dict):

    summary = report["summary"]

    print("\n")
    print("=" * 60)
    print("🤖 AUTONOMOUS BUG FIX AGENT")
    print("       EVALUATION SUMMARY")
    print("=" * 60)

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
        f"{summary['success_rate_percent']}%"
    )

    print(
        f"Total Runtime    : "
        f"{summary['total_runtime_seconds']}s"
    )

    print(
        f"Average Runtime  : "
        f"{summary['average_runtime_seconds']}s"
    )

    print("=" * 60)

    print("\nBenchmark Results:")

    for result in report["results"]:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"  {result['benchmark']:<12} "
            f"{status:<6} "
            f"{result['runtime_seconds']:.2f}s"
        )

    print("\n" + "=" * 60)

    print(
        "Evaluation report saved to:"
    )

    print(
        RESULTS_FILE
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 60)
    print("🚀 STARTING AUTONOMOUS BUG FIX EVALUATION")
    print("=" * 60)

    benchmarks = get_benchmarks()

    if not benchmarks:
        print(
            "\n❌ No benchmarks found."
        )
        return

    print(
        f"\nFound {len(benchmarks)} benchmark(s)."
    )

    results = []

    for benchmark in benchmarks:

        result = run_benchmark(
            benchmark
        )

        results.append(
            result
        )

    report = save_results(
        results
    )

    print_summary(
        report
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()