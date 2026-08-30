import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS_DIR = ROOT / "benchmarks"
PATCHES_DIR = BENCHMARKS_DIR / "patches"

RESULTS_DIR = ROOT / "evaluation" / "results"
RESULTS_FILE = RESULTS_DIR / "baseline_results.json"


def get_benchmarks():
    return sorted(
        [
            path
            for path in BENCHMARKS_DIR.iterdir()
            if path.is_dir() and path.name.startswith("bug_")
        ],
        key=lambda path: path.name
    )


def find_patch(benchmark_name):
    patches = list(
        PATCHES_DIR.glob(
            f"{benchmark_name}_*.patch"
        )
    )

    return patches[0] if patches else None


def apply_patch(repo_dir, patch_file):
    result = subprocess.run(
        [
            "git",
            "apply",
            str(patch_file.resolve())
        ],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return False, result.stderr.strip()

    return True, ""


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
    original_repo = benchmark_dir / "repo"

    patch_file = find_patch(benchmark_name)

    if patch_file is None:
        return {
            "benchmark": benchmark_name,
            "passed": False,
            "patch_applied": False,
            "runtime_seconds": 0,
            "output": "No baseline patch found."
        }

    temp_repo = benchmark_dir / "_baseline_repo"

    if temp_repo.exists():
        shutil.rmtree(temp_repo)

    shutil.copytree(
        original_repo,
        temp_repo
    )

    start = time.perf_counter()

    try:
        patch_applied, patch_error = apply_patch(
            temp_repo,
            patch_file
        )

        if not patch_applied:
            return {
                "benchmark": benchmark_name,
                "passed": False,
                "patch_applied": False,
                "runtime_seconds": round(
                    time.perf_counter() - start,
                    4
                ),
                "output": patch_error
            }

        passed, output = run_tests(
            temp_repo
        )

        return {
            "benchmark": benchmark_name,
            "passed": passed,
            "patch_applied": True,
            "runtime_seconds": round(
                time.perf_counter() - start,
                4
            ),
            "output": output
        }

    finally:
        shutil.rmtree(
            temp_repo,
            ignore_errors=True
        )


def main():

    print("\n")
    print("=" * 60)
    print("BASELINE BUG FIX EVALUATION")
    print("=" * 60)

    print(
        "\nBaseline strategy:"
        "\n  1. Apply the predefined single-pass patch"
        "\n  2. Run the repository tests"
        "\n  3. No autonomous analysis"
        "\n  4. No retry loop"
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
            "strategy": (
                "single_pass_predefined_patch"
            ),
            "autonomous_analysis": False,
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