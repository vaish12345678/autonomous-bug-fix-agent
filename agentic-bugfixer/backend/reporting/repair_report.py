import json
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

REPORT_DIR = (
    BASE_DIR
    / "evaluation"
    / "repair_reports"
)


# ============================================================
# BUILD REPAIR REPORT
# ============================================================

def build_repair_report(
    benchmark,
    issue,
    analysis,
    target_file,
    patch_risk,
    risk_score,
    syntax_passed,
    tests_passed,
    regression_passed,
    acceptance_passed,
    confidence_score,
    confidence_level,
    runtime_seconds=None
):
    """
    Build a structured explainable repair report.

    This function does not modify the repository.
    It only records the outcome of an autonomous repair.
    """

    if tests_passed and regression_passed and acceptance_passed:
        status = "VERIFIED"
        final_decision = (
            "PATCH VERIFIED AND ACCEPTED"
        )
    else:
        status = "REJECTED"
        final_decision = (
            "PATCH NOT VERIFIED"
        )

    report = {

        "report_metadata": {

            "generated_at":
                datetime.now().isoformat(),

            "benchmark":
                benchmark,

            "status":
                status
        },

        "bug": {

            "issue":
                issue.strip()
        },

        "root_cause_analysis": {

            "root_cause":
                analysis.get(
                    "root_cause",
                    ""
                ),

            "correction":
                analysis.get(
                    "correction",
                    ""
                ),

            "target_file":
                target_file
        },

        "patch_quality": {

            "risk_level":
                patch_risk,

            "risk_score":
                risk_score
        },

        "validation": {

            "syntax":
                "PASS"
                if syntax_passed
                else "FAIL",

            "tests":
                "PASS"
                if tests_passed
                else "FAIL",

            "regression":
                "PASS"
                if regression_passed
                else "FAIL",

            "acceptance_gate":
                "ACCEPTED"
                if acceptance_passed
                else "REJECTED"
        },

        "confidence": {

            "score":
                confidence_score,

            "level":
                confidence_level
        },

        "performance": {

            "runtime_seconds":
                runtime_seconds
        },

        "final_decision":
            final_decision
    }

    return report


# ============================================================
# SAVE REPORT
# ============================================================

def save_repair_report(
    report,
    filename=None
):
    """
    Save repair report as JSON.
    """

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not filename:

        benchmark = (
            report["report_metadata"]
            ["benchmark"]
        )

        timestamp = (
            datetime.now()
            .strftime("%Y%m%d_%H%M%S")
        )

        filename = (
            f"{benchmark}_"
            f"{timestamp}.json"
        )

    report_path = (
        REPORT_DIR / filename
    )

    report_path.write_text(
        json.dumps(
            report,
            indent=4
        ),
        encoding="utf-8"
    )

    return report_path


# ============================================================
# DISPLAY REPORT
# ============================================================

def display_repair_report(
    report
):

    metadata = (
        report["report_metadata"]
    )

    bug = report["bug"]

    analysis = (
        report["root_cause_analysis"]
    )

    quality = (
        report["patch_quality"]
    )

    validation = (
        report["validation"]
    )

    confidence = (
        report["confidence"]
    )

    performance = (
        report["performance"]
    )

    print()

    print("=" * 65)

    print(
        "              🔍 AUTONOMOUS REPAIR REPORT"
    )

    print("=" * 65)

    print()

    print(
        f"Benchmark       : "
        f"{metadata['benchmark']}"
    )

    print(
        f"Status          : "
        f"{metadata['status']}"
    )

    print()

    print(
        "---------------- BUG ----------------"
    )

    print()

    print(
        "Issue:"
    )

    print(
        bug["issue"]
    )

    print()

    print(
        "---------------- ROOT CAUSE ----------------"
    )

    print()

    print(
        analysis["root_cause"]
    )

    print()

    print(
        "Correction:"
    )

    print(
        analysis["correction"]
    )

    print()

    print(
        "Modified File:"
    )

    print(
        analysis["target_file"]
    )

    print()

    print(
        "---------------- PATCH QUALITY ----------------"
    )

    print()

    print(
        f"Risk Level      : "
        f"{quality['risk_level']}"
    )

    print(
        f"Risk Score      : "
        f"{quality['risk_score']}/100"
    )

    print()

    print(
        "---------------- VALIDATION ----------------"
    )

    print()

    print(
        f"Syntax          : "
        f"{validation['syntax']}"
    )

    print(
        f"Tests           : "
        f"{validation['tests']}"
    )

    print(
        f"Regression      : "
        f"{validation['regression']}"
    )

    print(
        f"Acceptance Gate : "
        f"{validation['acceptance_gate']}"
    )

    print()

    print(
        "---------------- CONFIDENCE ----------------"
    )

    print()

    print(
        f"Confidence      : "
        f"{confidence['score']}/100"
    )

    print(
        f"Level           : "
        f"{confidence['level']}"
    )

    print()

    if performance["runtime_seconds"] is not None:

        print(
            f"Runtime         : "
            f"{performance['runtime_seconds']:.2f}s"
        )

    print()

    print(
        "---------------- FINAL DECISION ----------------"
    )

    print()

    if metadata["status"] == "VERIFIED":

        print(
            "🎉 PATCH VERIFIED AND ACCEPTED"
        )

    else:

        print(
            "❌ PATCH NOT VERIFIED"
        )

    print()

    print("=" * 65)


# ============================================================
# DEMO
# ============================================================

def demo():

    analysis = {

        "root_cause":
            "The implementation performs "
            "the wrong arithmetic operation.",

        "correction":
            "Use division instead of multiplication."
    }

    report = build_repair_report(

        benchmark="bug_01",

        issue=(
            "divide() returns an incorrect "
            "result."
        ),

        analysis=analysis,

        target_file="calculator.py",

        patch_risk="LOW",

        risk_score=0,

        syntax_passed=True,

        tests_passed=True,

        regression_passed=True,

        acceptance_passed=True,

        confidence_score=100.0,

        confidence_level="VERY HIGH",

        runtime_seconds=1.84
    )

    display_repair_report(
        report
    )

    report_path = save_repair_report(
        report
    )

    print()

    print(
        "✓ Repair report saved to:"
    )

    print(
        report_path
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    demo()