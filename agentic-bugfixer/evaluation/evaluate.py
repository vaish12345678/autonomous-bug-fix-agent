import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS = ROOT / "benchmarks"


def run_benchmark(benchmark_dir):
    repo_dir = benchmark_dir / "repo"

    start = time.perf_counter()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(repo_dir),
            "-q",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    elapsed = time.perf_counter() - start

    passed = result.returncode == 0

    return {
        "benchmark": benchmark_dir.name,
        "passed": passed,
        "runtime_seconds": round(elapsed, 3),
        "output": result.stdout.strip(),
    }


def main():
    print("=" * 60)
    print("AUTONOMOUS BUG FIX AGENT - BENCHMARK EVALUATION")
    print("=" * 60)

    results = []

    benchmark_dirs = sorted(
        [
            path
            for path in BENCHMARKS.iterdir()
            if path.is_dir() and path.name.startswith("bug_")
        ]
    )

    if not benchmark_dirs:
        print("No benchmarks found.")
        return

    for benchmark_dir in benchmark_dirs:
        print(f"\nRunning {benchmark_dir.name}...")

        result = run_benchmark(benchmark_dir)
        results.append(result)

        if result["passed"]:
            print(
                f"✓ {result['benchmark']} PASSED "
                f"({result['runtime_seconds']}s)"
            )
        else:
            print(
                f"✗ {result['benchmark']} FAILED "
                f"({result['runtime_seconds']}s)"
            )

    passed = sum(result["passed"] for result in results)
    total = len(results)

    total_runtime = sum(
        result["runtime_seconds"] for result in results
    )

    accuracy = (passed / total) * 100

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    print(f"Benchmarks:       {total}")
    print(f"Passed:           {passed}")
    print(f"Failed:           {total - passed}")
    print(f"Success rate:     {accuracy:.1f}%")
    print(f"Total runtime:    {total_runtime:.3f}s")

    print("=" * 60)


if __name__ == "__main__":
    main()