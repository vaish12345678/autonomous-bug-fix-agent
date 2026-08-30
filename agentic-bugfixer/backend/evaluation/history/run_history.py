import json
from pathlib import Path
from datetime import datetime


# ============================================================
# HISTORY DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

HISTORY_DIR = (
    BASE_DIR
    / "evaluation"
    / "history"
)

HISTORY_FILE = (
    HISTORY_DIR
    / "runs.json"
)


# ============================================================
# INITIALIZE HISTORY
# ============================================================

def initialize_history():

    HISTORY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not HISTORY_FILE.exists():

        HISTORY_FILE.write_text(
            "[]",
            encoding="utf-8"
        )


# ============================================================
# LOAD HISTORY
# ============================================================

def load_history():

    initialize_history()

    try:

        return json.loads(
            HISTORY_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ============================================================
# RECORD RUN
# ============================================================

def record_run(
    benchmarks_total: int,
    benchmarks_passed: int,
    confidence_score: float,
    runtime_seconds: float
):

    history = load_history()

    success_rate = 0.0

    if benchmarks_total > 0:

        success_rate = (
            benchmarks_passed
            / benchmarks_total
        ) * 100

    run = {

        "run_id": len(history) + 1,

        "timestamp": (
            datetime.now()
            .isoformat()
        ),

        "benchmarks_total":
            benchmarks_total,

        "benchmarks_passed":
            benchmarks_passed,

        "success_rate":
            round(
                success_rate,
                2
            ),

        "confidence_score":
            round(
                confidence_score,
                2
            ),

        "runtime_seconds":
            round(
                runtime_seconds,
                2
            )
    }

    history.append(run)

    HISTORY_FILE.write_text(
        json.dumps(
            history,
            indent=4
        ),
        encoding="utf-8"
    )

    return run


# ============================================================
# TREND ANALYSIS
# ============================================================

def analyze_trend():

    history = load_history()

    if not history:

        return {
            "total_runs": 0,
            "average_success_rate": 0,
            "average_confidence": 0,
            "trend": "NO DATA"
        }

    success_rates = [
        run["success_rate"]
        for run in history
    ]

    confidence_scores = [
        run["confidence_score"]
        for run in history
    ]

    average_success = (
        sum(success_rates)
        / len(success_rates)
    )

    average_confidence = (
        sum(confidence_scores)
        / len(confidence_scores)
    )

    trend = "STABLE"

    if len(history) >= 2:

        previous = history[-2]
        current = history[-1]

        if (
            current["success_rate"]
            > previous["success_rate"]
        ):

            trend = "IMPROVING"

        elif (
            current["success_rate"]
            < previous["success_rate"]
        ):

            trend = "DECLINING"

    return {

        "total_runs":
            len(history),

        "average_success_rate":
            round(
                average_success,
                2
            ),

        "average_confidence":
            round(
                average_confidence,
                2
            ),

        "trend":
            trend
    }


# ============================================================
# DISPLAY HISTORY
# ============================================================

def print_history():

    history = load_history()

    print()
    print("=" * 70)
    print("          📈 AGENT RUN HISTORY")
    print("=" * 70)

    print()

    if not history:

        print(
            "No evaluation runs recorded."
        )

    else:

        for run in history:

            print(
                f"Run #{run['run_id']}"
            )

            print(
                f"  Time       : "
                f"{run['timestamp']}"
            )

            print(
                f"  Benchmarks : "
                f"{run['benchmarks_passed']}/"
                f"{run['benchmarks_total']}"
            )

            print(
                f"  Success    : "
                f"{run['success_rate']:.2f}%"
            )

            print(
                f"  Confidence : "
                f"{run['confidence_score']:.2f}/100"
            )

            print(
                f"  Runtime    : "
                f"{run['runtime_seconds']:.2f}s"
            )

            print()

    trend = analyze_trend()

    print(
        "---------- TREND SUMMARY ----------"
    )

    print(
        f"Total Runs          : "
        f"{trend['total_runs']}"
    )

    print(
        f"Average Success     : "
        f"{trend['average_success_rate']:.2f}%"
    )

    print(
        f"Average Confidence  : "
        f"{trend['average_confidence']:.2f}/100"
    )

    print(
        f"System Trend        : "
        f"{trend['trend']}"
    )

    print()
    print("=" * 70)


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":

    record_run(
        benchmarks_total=5,
        benchmarks_passed=5,
        confidence_score=100,
        runtime_seconds=1.84
    )

    print_history()