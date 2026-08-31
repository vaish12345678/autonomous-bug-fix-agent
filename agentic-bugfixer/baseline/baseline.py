import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS_DIR = ROOT / "benchmarks"

RESULTS_DIR = ROOT / "evaluation" / "results"
RESULTS_FILE = RESULTS_DIR / "baseline_results.json"

BASE_COMMIT = "ea8e62f"

TARGET_FILES = {
    "bug_01": "calculator.py",
    "bug_02": "discount.py",
    "bug_03": "statistics.py",
    "bug_04": "agent.py",
    "bug_05": "positive_checker.py",
    "bug_06": "agent.py",
    "bug_07": "agent.py",
    "bug_08": "agent.py",
    "bug_09": "agent.py",
    "bug_10": "agent.py",
    "bug_11": "agent.py",
    "bug_12": "agent.py",
}


def get_benchmarks():
    return sorted(
        [
            path
            for path in BENCHMARKS_DIR.iterdir()
            if path.is_dir() and path.name.startswith("bug_")
        ],
        key=lambda path: path.name
    )


def get_buggy_source(benchmark_name, file_name):
    git_path = (
        f"{BASE_COMMIT}^:"
        f"agentic-bugfixer/benchmarks/"
        f"{benchmark_name}/repo/{file_name}"
    )

    result = subprocess.run(
        ["git", "show", git_path],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout


def run_tests(repo_dir):
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

    output = (
        result.stdout
        + "\n"
        + result.stderr
    ).strip()

    return result.returncode == 0, output


def run_benchmark(benchmark_dir):
    benchmark_name = benchmark_dir.name
    repo_dir = benchmark_dir / "repo"
    file_name = TARGET_FILES[benchmark_name]
    target_file = repo_dir / file_name

    start = time.perf_counter()

    original_content = target_file.read_text(
        encoding="utf-8"
    )

    try:
        buggy_content = get_buggy_source(
            benchmark_name,
            file_name
        )

        # Restore the benchmark to its original buggy state.
        target_file.write_text(
            buggy_content,
            encoding="utf-8"
        )

        passed, output = run_tests(repo_dir)

        return {
            "benchmark": benchmark_name,
            "passed": passed,
            "runtime_seconds": round(
                time.perf_counter() - start,
                4
            ),
            "output": output
        }

    finally:
        # Always restore the current fixed benchmark.
        target_file.write_text(
            original_content,
            encoding="utf-8"
        )


def main():

    print("\n")
    print("=" * 60)
    print("BASELINE BUG FIX EVALUATION")
    print("=" * 60)

    print(
        "\nBaseline strategy:"
        "\n  1. Restore the original buggy implementation"
        "\n  2. Run the repository tests"
        "\n  3. No autonomous analysis"
        "\n  4. No AI patch generation"
        "\n  5. No retry loop"
    )

    benchmarks = get_benchmarks()

    print(
        f"\nFound {len(benchmarks)} benchmark(s)."
    )

    results = []

    for benchmark in benchmarks:

        print("\n" + "-" * 60)
        print(
            f"Running baseline: "
            f"{benchmark.name}"
        )
        print("-" * 60)

        result = run_benchmark(
            benchmark
        )

        results.append(result)

        if result["passed"]:
            print("PASSED")
        else:
            print("FAILED")

        print(
            f"Runtime: "
            f"{result['runtime_seconds']:.2f}s"
        )

        print(result["output"])

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
        if total
        else 0
    )

    report = {
        "baseline": {
            "strategy": "single_pass_no_repair",
            "autonomous_analysis": False,
            "ai_patch_generation": False,
            "retry_loop": False
        },
        "summary": {
            "total_benchmarks": total,
            "passed": passed,
            "failed": failed,
            "success_rate_percent": round(
                (passed / total) * 100,
                2
            ) if total else 0,
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

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    RESULTS_FILE.write_text(
        json.dumps(
            report,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("BASELINE SUMMARY")
    print("=" * 60)

    print(
        f"Total Benchmarks : {total}"
    )
    print(
        f"Passed           : {passed}"
    )
    print(
        f"Failed           : {failed}"
    )
    print(
        f"Success Rate     : "
        f"{report['summary']['success_rate_percent']}%"
    )

    print(
        f"Total Runtime    : "
        f"{report['summary']['total_runtime_seconds']}s"
    )

    print(
        f"Average Runtime  : "
        f"{report['summary']['average_runtime_seconds']}s"
    )

    print("=" * 60)

    print(
        "\nBaseline report saved to:"
    )

    print(RESULTS_FILE)


if __name__ == "__main__":
    main()