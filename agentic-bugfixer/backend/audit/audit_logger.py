import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

AUDIT_DIR = BASE_DIR / "evaluation" / "audit_logs"

AUDIT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def create_audit_log(
    benchmark,
    issue,
    target_file,
    root_cause,
    correction,
    risk_level,
    risk_score,
    accepted,
    test_passed,
    attempts,
):
    """
    Create a complete audit record for one autonomous
    bug-fixing run.
    """

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "benchmark": benchmark,

        "issue": issue,

        "target_file": target_file,

        "root_cause": root_cause,

        "correction": correction,

        "risk": {
            "level": risk_level,
            "score": risk_score,
        },

        "acceptance": {
            "accepted": accepted,
        },

        "verification": {
            "tests_passed": test_passed,
            "attempts": attempts,
        },
    }

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    log_file = (
        AUDIT_DIR
        / f"{benchmark}_{timestamp}.json"
    )

    log_file.write_text(
        json.dumps(
            record,
            indent=4
        ),
        encoding="utf-8"
    )

    return log_file


def read_audit_logs():
    """
    Return all available audit records.
    """

    records = []

    if not AUDIT_DIR.exists():
        return records

    for path in sorted(
        AUDIT_DIR.glob("*.json")
    ):

        try:

            records.append(
                json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):

            continue

    return records


def get_audit_summary():
    """
    Generate high-level statistics from
    previous autonomous runs.
    """

    records = read_audit_logs()

    total = len(records)

    successful = sum(
        1
        for record in records
        if record.get(
            "verification",
            {}
        ).get(
            "tests_passed",
            False
        )
    )

    accepted = sum(
        1
        for record in records
        if record.get(
            "acceptance",
            {}
        ).get(
            "accepted",
            False
        )
    )

    success_rate = (
        (successful / total) * 100
        if total
        else 0
    )

    return {
        "total_runs": total,
        "successful_runs": successful,
        "accepted_runs": accepted,
        "success_rate": round(
            success_rate,
            2
        ),
    }


if __name__ == "__main__":

    print(
        "\n========== AUDIT LOGGER ==========\n"
    )

    log = create_audit_log(
        benchmark="demo",
        issue="Demo bug",
        target_file="demo.py",
        root_cause="Demo root cause",
        correction="Demo correction",
        risk_level="LOW",
        risk_score=0,
        accepted=True,
        test_passed=True,
        attempts=1,
    )

    print(
        f"✓ Audit log created:\n{log}"
    )

    print(
        "\n========== AUDIT SUMMARY ==========\n"
    )

    print(
        json.dumps(
            get_audit_summary(),
            indent=4
        )
    )