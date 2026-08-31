import json
from pathlib import Path
from statistics import mean


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

AUDIT_DIR = BASE_DIR / "evaluation" / "audit_logs"
RESULTS_FILE = BASE_DIR / "evaluation" / "results" / "evaluation_results.json"


# ============================================================
# LOAD JSON SAFELY
# ============================================================

def load_json(path: Path):
    """Load a JSON file safely."""

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError):
        return None


# ============================================================
# LOAD AUDIT LOGS
# ============================================================

def load_audit_logs():
    """Load all audit log JSON files."""

    if not AUDIT_DIR.exists():
        return []

    logs = []

    for path in sorted(AUDIT_DIR.glob("*.json")):

        data = load_json(path)

        if data is not None:
            logs.append(data)

    return logs


# ============================================================
# LOAD EVALUATION RESULTS
# ============================================================

def load_evaluation_results():
    """Load benchmark evaluation results."""

    if not RESULTS_FILE.exists():
        return None

    return load_json(RESULTS_FILE)


# ============================================================
# EXTRACT BENCHMARK RESULTS
# ============================================================

def extract_benchmark_results(results):
    """
    Normalize benchmark results from evaluation_results.json.
    """

    if not results:
        return []

    if isinstance(results, list):
        return results

    if isinstance(results, dict):

        for key in (
            "benchmark_results",
            "results",
            "benchmarks"
        ):

            value = results.get(key)

            if isinstance(value, list):
                return value

    return []


# ============================================================
# CALCULATE BENCHMARK STATISTICS
# ============================================================

def calculate_benchmark_stats(results):

    benchmarks = extract_benchmark_results(results)

    total = len(benchmarks)

    passed = 0
    failed = 0

    runtimes = []

    normalized = []

    for item in benchmarks:

        if not isinstance(item, dict):
            continue

        name = (
            item.get("benchmark")
            or item.get("name")
            or item.get("id")
            or "unknown"
        )

        status = str(
            item.get("status")
            or item.get("result")
            or ""
        ).upper()

        success = item.get("passed")

        if success is None:
            success = status in {
                "PASS",
                "PASSED",
                "SUCCESS"
            }

        if success:
            passed += 1
            display_status = "PASS"
        else:
            failed += 1
            display_status = "FAIL"

        runtime = item.get("runtime")

        if runtime is None:
            runtime = item.get("runtime_seconds")

        try:
            if runtime is not None:
                runtimes.append(float(runtime))
        except (TypeError, ValueError):
            pass

        normalized.append(
            {
                "benchmark": name,
                "status": display_status,
                "runtime": runtime
            }
        )

    success_rate = (
        (passed / total) * 100
        if total
        else 0
    )

    average_runtime = (
        mean(runtimes)
        if runtimes
        else 0
    )

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "average_runtime": average_runtime,
        "benchmarks": normalized
    }


# ============================================================
# CALCULATE AUDIT STATISTICS
# ============================================================
def calculate_audit_stats(logs):

    total_runs = len(logs)

    successful_runs = 0
    accepted_runs = 0

    for log in logs:

        if not isinstance(log, dict):
            continue

        # ----------------------------------------------------
        # SUCCESS DETECTION
        # ----------------------------------------------------

        verification = log.get(
            "verification",
            {}
        )

        success = (
            log.get("success")
            or log.get("successful")
            or log.get("status") in {
                "success",
                "SUCCESS",
                "passed",
                "PASSED"
            }
            or verification.get(
                "tests_passed",
                False
            )
        )

        # ----------------------------------------------------
        # ACCEPTANCE DETECTION
        # ----------------------------------------------------

        acceptance = log.get(
            "acceptance",
            {}
        )

        accepted = (
            log.get("accepted")
            or log.get("patch_accepted")
            or log.get("acceptance_status") in {
                "accepted",
                "ACCEPTED"
            }
            or acceptance.get(
                "accepted",
                False
            )
        )

        if success:
            successful_runs += 1

        if accepted:
            accepted_runs += 1

    success_rate = (
        (successful_runs / total_runs) * 100
        if total_runs
        else 0
    )

    acceptance_rate = (
        (accepted_runs / total_runs) * 100
        if total_runs
        else 0
    )

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "accepted_runs": accepted_runs,
        "success_rate": success_rate,
        "acceptance_rate": acceptance_rate
    }

# ============================================================
# SYSTEM SCORE
# ============================================================

def calculate_system_score(
    benchmark_stats,
    audit_stats
):
    """
    Calculate an overall system score.

    Correctness = benchmark success rate
    Safety      = patch acceptance rate
    Reliability = average of correctness and safety
    """

    correctness = benchmark_stats["success_rate"]

    safety = audit_stats["acceptance_rate"]

    reliability = (
        (correctness + safety) / 2
    )

    overall = (
        correctness * 0.50
        + safety * 0.30
        + reliability * 0.20
    )

    return {
        "correctness": round(correctness, 2),
        "safety": round(safety, 2),
        "reliability": round(reliability, 2),
        "overall": round(overall, 2)
    }


# ============================================================
# PRINT DASHBOARD
# ============================================================

def print_dashboard():

    print()
    print("=" * 60)
    print("       🤖 AUTONOMOUS BUG FIX EVALUATION")
    print("=" * 60)

    results = load_evaluation_results()

    audit_logs = load_audit_logs()

    benchmark_stats = calculate_benchmark_stats(
        results
    )

    audit_stats = calculate_audit_stats(
        audit_logs
    )

    score = calculate_system_score(
        benchmark_stats,
        audit_stats
    )

    # --------------------------------------------------------
    # BENCHMARK SUMMARY
    # --------------------------------------------------------

    print()
    print("========== BENCHMARK PERFORMANCE ==========")
    print()

    print(
        f"Total Benchmarks       : "
        f"{benchmark_stats['total']}"
    )

    print(
        f"Passed                  : "
        f"{benchmark_stats['passed']}"
    )

    print(
        f"Failed                  : "
        f"{benchmark_stats['failed']}"
    )

    print(
        f"Success Rate            : "
        f"{benchmark_stats['success_rate']:.2f}%"
    )

    print(
        f"Average Runtime         : "
        f"{benchmark_stats['average_runtime']:.2f}s"
    )

    # --------------------------------------------------------
    # INDIVIDUAL BENCHMARKS
    # --------------------------------------------------------

    if benchmark_stats["benchmarks"]:

        print()
        print("Benchmark Results:")
        print()

        for benchmark in benchmark_stats["benchmarks"]:

            runtime = benchmark["runtime"]

            runtime_text = (
                f"{float(runtime):.2f}s"
                if runtime is not None
                else "N/A"
            )

            print(
                f"  {benchmark['benchmark']:<15}"
                f"{benchmark['status']:<8}"
                f"{runtime_text}"
            )

    # --------------------------------------------------------
    # AUDIT SUMMARY
    # --------------------------------------------------------

    print()
    print("========== AUDIT PERFORMANCE ==========")
    print()

    print(
        f"Total Agent Runs       : "
        f"{audit_stats['total_runs']}"
    )

    print(
        f"Successful Runs        : "
        f"{audit_stats['successful_runs']}"
    )

    print(
        f"Accepted Patches       : "
        f"{audit_stats['accepted_runs']}"
    )

    print(
        f"Agent Success Rate     : "
        f"{audit_stats['success_rate']:.2f}%"
    )

    print(
        f"Patch Acceptance Rate  : "
        f"{audit_stats['acceptance_rate']:.2f}%"
    )

    # --------------------------------------------------------
    # SYSTEM SCORE
    # --------------------------------------------------------

    print()
    print("========== SYSTEM SCORE ==========")
    print()

    print(
        f"Correctness            : "
        f"{score['correctness']:.2f}/100"
    )

    print(
        f"Safety                 : "
        f"{score['safety']:.2f}/100"
    )

    print(
        f"Reliability            : "
        f"{score['reliability']:.2f}/100"
    )

    print()
    print(
        f"🏆 OVERALL SCORE       : "
        f"{score['overall']:.2f}/100"
    )

    print()
    print("=" * 60)


# ============================================================
# EXPORT REPORT
# ============================================================

def generate_report():

    results = load_evaluation_results()

    audit_logs = load_audit_logs()

    benchmark_stats = calculate_benchmark_stats(
        results
    )

    audit_stats = calculate_audit_stats(
        audit_logs
    )

    score = calculate_system_score(
        benchmark_stats,
        audit_stats
    )

    report = {
        "benchmark_statistics": benchmark_stats,
        "audit_statistics": audit_stats,
        "system_score": score
    }

    report_dir = BASE_DIR / "evaluation" / "reports"

    report_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path = (
        report_dir /
        "evaluation_dashboard.json"
    )

    with report_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    return report_path


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print_dashboard()

    report_path = generate_report()

    print()
    print(
        f"✓ Evaluation report saved to:"
    )
    print(
        report_path
    )

